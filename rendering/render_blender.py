"""
Step 3 (alternate): same rendering job as render_rotations.py but using Blender.
Use this if your machine doesn't have OSMesa/EGL set up properly for pyrender.

Run with:
    blender --background --python render_blender.py -- \
        --meshes ./meshes --out ./rotation_frames --size 384 --n-frames 13 --arc 45

Tested with Blender 4.x (Cycles or Eevee).
"""
import bpy, math, os, sys, json, argparse

def cli_args():
    if '--' in sys.argv:
        idx = sys.argv.index('--')
        argv = sys.argv[idx+1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument('--meshes', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--size', type=int, default=384)
    p.add_argument('--n-frames', type=int, default=13)
    p.add_argument('--arc', type=float, default=45.0)
    return p.parse_args(argv)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.eevee.taa_render_samples = 32

def setup_camera_and_lights():
    # Orthographic camera looking from +Z slightly above
    cam_data = bpy.data.cameras.new('Cam')
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 2.6
    cam = bpy.data.objects.new('Cam', cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0.0, -3.5, 0.6)
    cam.rotation_euler = (math.radians(82), 0, 0)
    bpy.context.scene.camera = cam
    # Sun key + sun fill
    key = bpy.data.lights.new('Key', 'SUN'); key.energy = 4.0
    ko = bpy.data.objects.new('Key', key); bpy.context.collection.objects.link(ko)
    ko.rotation_euler = (math.radians(35), math.radians(-30), 0)
    fill = bpy.data.lights.new('Fill', 'SUN'); fill.energy = 1.5
    fo = bpy.data.objects.new('Fill', fill); bpy.context.collection.objects.link(fo)
    fo.rotation_euler = (math.radians(60), math.radians(120), 0)
    return cam

def import_glb_normalize(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    if not new: raise RuntimeError(f'no mesh in {path}')
    # Combine all meshes into a single empty parent
    parent = bpy.data.objects.new('ObjRoot', None)
    bpy.context.collection.objects.link(parent)
    for o in new:
        o.parent = parent
    # Recenter + rescale to unit-ish bounding box
    bpy.context.view_layer.update()
    bbox_min = [min(min((o.matrix_world @ v.co)[i] for v in o.data.vertices) for o in new) for i in range(3)]
    bbox_max = [max(max((o.matrix_world @ v.co)[i] for v in o.data.vertices) for o in new) for i in range(3)]
    center = [(bbox_min[i]+bbox_max[i])/2 for i in range(3)]
    extent = max(bbox_max[i]-bbox_min[i] for i in range(3))
    scale = 2.0 / extent
    for o in new:
        o.location = (o.location[0]-center[0], o.location[1]-center[1], o.location[2]-center[2])
    parent.scale = (scale, scale, scale)
    return parent

def smoothstep(u): return u*u*(3 - 2*u)

def render_object(glb_path, out_dir, size, n_frames, arc):
    reset_scene()
    setup_camera_and_lights()
    bpy.context.scene.render.resolution_x = size
    bpy.context.scene.render.resolution_y = size
    parent = import_glb_normalize(glb_path)
    os.makedirs(out_dir, exist_ok=True)
    angles = []
    for i in range(n_frames):
        u = i / (n_frames - 1)
        ang = -arc + 2*arc*smoothstep(u)
        parent.rotation_euler = (0, 0, math.radians(ang))
        bpy.context.scene.render.filepath = os.path.join(out_dir, f'{i:02d}.png')
        bpy.ops.render.render(write_still=True)
        angles.append(ang)
    return angles

def main():
    args = cli_args()
    log = []
    for cat in sorted(os.listdir(args.meshes)):
        cat_dir = os.path.join(args.meshes, cat)
        if not os.path.isdir(cat_dir): continue
        for fname in sorted(os.listdir(cat_dir)):
            if not fname.endswith('.glb'): continue
            mid = fname[:-4]
            try:
                angles = render_object(os.path.join(cat_dir, fname),
                                       os.path.join(args.out, cat, mid),
                                       args.size, args.n_frames, args.arc)
                log.append({'cat': cat, 'mid': mid, 'angles': angles, 'ok': True})
                print(f'OK  {cat}/{mid}')
            except Exception as e:
                log.append({'cat': cat, 'mid': mid, 'error': str(e), 'ok': False})
                print(f'ERR {cat}/{mid}: {e}')
    with open(os.path.join(args.out, '_render_log.json'), 'w') as f:
        json.dump(log, f, indent=2)

if __name__ == '__main__':
    main()
