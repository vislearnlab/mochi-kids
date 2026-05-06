"""
Step 2: download just the ShapeNet GLB files we need (76 models for the
curated kid trial set), to a local cache.

The HF repo `ShapeNet/shapenetcore-glb` is gated. Before this script works,
you must:
  1. Sign in at https://huggingface.co
  2. Visit https://huggingface.co/datasets/ShapeNet/shapenetcore-glb and
     accept the ShapeNet terms of use.
  3. Generate a read token at https://huggingface.co/settings/tokens
  4. `export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx`

Usage:
    python download_shapenet.py --needed needed_shapenet.json --out ./meshes
"""
import argparse, json, os
from huggingface_hub import hf_hub_download

REPO = 'ShapeNet/shapenetcore-glb'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--needed', required=True)
    p.add_argument('--out', default='./meshes')
    args = p.parse_args()

    token = os.environ.get('HF_TOKEN')
    if not token:
        raise SystemExit('Set HF_TOKEN env var (see docstring).')

    with open(args.needed) as f:
        spec = json.load(f)

    n_ok, n_err = 0, 0
    for cat, mids in spec['categories'].items():
        for mid in mids:
            relpath = f'{cat}/{mid}.glb'
            try:
                local = hf_hub_download(
                    repo_id=REPO, repo_type='dataset',
                    filename=relpath, local_dir=args.out, token=token,
                )
                n_ok += 1
            except Exception as e:
                print(f'  ERR  {relpath} -> {e}')
                n_err += 1
    print(f'\ndone: {n_ok} downloaded, {n_err} failed -> {args.out}')

if __name__ == '__main__':
    main()
