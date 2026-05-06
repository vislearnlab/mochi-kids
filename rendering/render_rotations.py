"""
Step 3: render the rotation flipbooks.

For each downloaded ShapeNet model, render 13 frames in a +/-45 deg arc
around the vertical (yaw) axis, smooth ease-in-out interpolation,
matched lighting, transparent background. Frames are saved as
`<model_id>_<frame>.png` and the matching MOCHI viewpoint angle is recorded
so each MOCHI still maps to a frame index.

This script uses pyrender + osmesa or EGL. Install:

    sudo apt-get install libosmesa6-dev   # Linux
    pip install trimesh pyrender pyopengl Pillow numpy

If running on macOS without easy GL, use render_blender.py instead.

Usage:
    python render_rotations.py \
        --meshes ./meshes \
        --out ./rotation_frames \
        --size 384 --n-frames 13 --arc 45
"""
import argparse, os, math, json
import numpy as np
from PIL import Image

# Force pyrender headless
os.environ.setdefault('PYOPENGL_PLATFORM', 'egl')

import trimesh
import pyrender

# How a kid-game frame should look:
BG_COLOR = (250, 250, 250, 255)
LIGHT_COLOR = np.ones(3) * 1.0

def load_mesh(path):
    obj = trimesh.load(path, force='scene')
    # GLB scenes can have multiple meshes; merge into one
    if isinstance(obj, trimesh.Scene):
        meshes = [g for g in obj.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise RuntimeError(f'no mesh geometries in {path}')
        merged = trimesh.util.concatenate(meshes)
    else:
        merged = obj
    # Center + scale to unit cube
    bounds = merged.bounds
    center = (bounds[0] + bounds[1]) / 2
    extent = (bounds[1] - bounds[0]).max()
    merged.apply_translation(-center)
    merged.apply_scale(2.0 / extent)
    return merged

def render_object(glb_path, out_dir, size=384, n_frames=13, arc=45.0):
    os.makedirs(out_dir, exist_ok=True)
    mesh = load_mesh(glb_path)
    pr_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)
    scene = pyrender.Scene(bg_color=BG_COLOR, ambient_light=np.ones(3) * 0.35)
    scene.add(pr_mesh)

    # Camera: orthographic looking down -Z
    cam = pyrender.OrthographicCamera(xmag=1.4, ymag=1.4, znear=0.05, zfar=10.0)
    cam_pose = np.eye(4)
    cam_pose[:3, 3] = [0, 0.3, 3.5]
    cam_pose[:3, :3] = trimesh.transformations.euler_matrix(-0.15, 0, 0)[:3, :3]
    scene.add(cam, pose=cam_pose)

    # Lights: key + fill
    key = pyrender.DirectionalLight(color=LIGHT_COLOR, intensity=4.0)
    key_pose = np.eye(4); key_pose[:3, 3] = [1.0, 1.5, 2.0]
    scene.add(key, pose=key_pose)
    fill = pyrender.DirectionalLight(color=LIGHT_COLOR, intensity=1.5)
    fill_pose = np.eye(4); fill_pose[:3, 3] = [-1.5, 0.5, 1.5]
    scene.add(fill, pose=fill_pose)

    renderer = pyrender.OffscreenRenderer(size, size)
    angles = []
    for i in range(n_frames):
        u = i / (n_frames - 1)
        eased = u * u * (3 - 2 * u)  # smoothstep
        angles.append(-arc + 2 * arc * eased)

    # Apply rotation by transforming the mesh node each frame
    mesh_node = list(scene.mesh_nodes)[0]
    base_pose = mesh_node.matrix.copy()

    for i, ang in enumerate(angles):
        R = trimesh.transformations.rotation_matrix(math.radians(ang), [0, 1, 0])
        scene.set_pose(mesh_node, R @ base_pose)
        color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
        Image.fromarray(color).save(os.path.join(out_dir, f'{i:02d}.png'))

    renderer.delete()
    return angles

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--meshes', required=True, help='dir from download_shapenet.py')
    p.add_argument('--out', required=True)
    p.add_argument('--size', type=int, default=384)
    p.add_argument('--n-frames', type=int, default=13)
    p.add_argument('--arc', type=float, default=45.0)
    args = p.parse_args()

    log = []
    for cat in sorted(os.listdir(args.meshes)):
        cat_dir = os.path.join(args.meshes, cat)
        if not os.path.isdir(cat_dir): continue
        for fname in sorted(os.listdir(cat_dir)):
            if not fname.endswith('.glb'): continue
            mid = fname[:-4]
            out_dir = os.path.join(args.out, cat, mid)
            try:
                angles = render_object(os.path.join(cat_dir, fname),
                                       out_dir, size=args.size,
                                       n_frames=args.n_frames, arc=args.arc)
                log.append({'cat': cat, 'mid': mid, 'angles': angles, 'ok': True})
                print(f'  OK   {cat}/{mid}')
            except Exception as e:
                print(f'  ERR  {cat}/{mid} -> {e}')
                log.append({'cat': cat, 'mid': mid, 'error': str(e), 'ok': False})

    with open(os.path.join(args.out, '_render_log.json'), 'w') as f:
        json.dump(log, f, indent=2)
    n_ok = sum(1 for x in log if x.get('ok'))
    print(f'\nrendered {n_ok}/{len(log)} models -> {args.out}')

if __name__ == '__main__':
    main()
