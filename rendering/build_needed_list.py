"""
Step 1 of the rotation-animation pipeline.

Reads the curated kid-trial manifest + the MOCHI parquet, and writes
`needed_shapenet.json` with the (category, model_id) pairs we need to
download from ShapeNet.

Usage:
    python build_needed_list.py \
        --mochi /path/to/MOCHI/data/train-00000-of-00001.parquet \
        --manifest ../public/manifest.json \
        --out needed_shapenet.json
"""
import argparse, json, re
from collections import defaultdict
import pyarrow.parquet as pq

# MOCHI uses ShapeNet synset IDs in filenames; the public glb repo uses
# category names. This is the mapping for the categories we curate.
SYNSET_TO_CATEGORY = {
    '02828884': 'bench',
    '02933112': 'cabinet',
    '03001627': 'chair',
    '03211117': 'display',
    '03636649': 'lamp',
    '03691459': 'loudspeaker',
    '04256520': 'sofa',
    '04379243': 'table',
    '04401088': 'telephone',
    '04530566': 'vessel',  # MOCHI calls this 'watercraft'
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mochi', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--out', default='needed_shapenet.json')
    args = p.parse_args()

    with open(args.manifest) as f:
        kid_ids = {t['trial_id'] for t in json.load(f)['trials']}

    df = pq.read_table(args.mochi, columns=['dataset', 'trial', 'images']).to_pandas()
    sub = df[df['trial'].isin(kid_ids) & (df['dataset'] == 'shapenet')]

    needed = defaultdict(set)        # category -> set of model_ids
    trial_index = defaultdict(list)  # category/model_id -> [(trial, viewpoint_index)]

    for _, row in sub.iterrows():
        for img in row['images']:
            path = img.get('path') if isinstance(img, dict) else None
            if not path: continue
            m = re.match(r'(\d+)_([a-f0-9]+)_(\d+)\.png', path)
            if not m: continue
            synset, mid, vid = m.groups()
            cat = SYNSET_TO_CATEGORY.get(synset)
            if not cat: continue
            needed[cat].add(mid)
            trial_index[f'{cat}/{mid}'].append({'trial': row['trial'], 'viewpoint': int(vid)})

    out = {
        'categories': {cat: sorted(mids) for cat, mids in needed.items()},
        'total': sum(len(v) for v in needed.values()),
        'trial_index': trial_index,
    }
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'wrote {args.out}: {out["total"]} models across {len(needed)} categories')

if __name__ == '__main__':
    main()
