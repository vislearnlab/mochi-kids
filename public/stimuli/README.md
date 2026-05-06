# public/stimuli/

35 curated trials, each in its own folder. Every trial is a 3-image
oddity (3AFC): two viewpoints of the same object + one different
object's viewpoint.

```
stimuli/
├── training_00/0.jpg, 1.jpg, 2.jpg     # 6 same-image pop-out trials
├── shapenet1234/0.jpg, 1.jpg, 2.jpg     # 21 familiar-object trials (chair, lamp, bench, …)
└── shapegen2486/0.jpg, 1.jpg, 2.jpg     # 8 novel abstract-shape trials (shapegen abstract4)
```

## How these were curated

Source: `tzler/MOCHI` on Hugging Face (Bonnen et al., NeurIPS 2024 D&B).
Filter applied:

- `dataset` ∈ {shapenet, shapegen} — drops `majaj` (HVM/Yamins) and `barense` (faces)
- `n_objects == 3` — keeps the 3AFC layout consistent for kids
- `human_avg == 1.0` — adults nailed every trial we kept
- `RT_avg < 2500ms` — adults responded fast (visually obvious)
- For shapenet: matching-pair viewpoints are *adjacent* (smaller
  rotation between them)
- For shapegen: only `abstract4` (the easiest similarity bin)

Within those filters, sampled by condition with hard caps so no single
category dominates.

## Tier composition

| tier | n | what | source |
| --- | --- | --- | --- |
| training | 6 | same image duplicated × 2 + a different image | synthesized at curate time |
| warmup | 8 | super-easy real objects (chair, lamp, bench) | shapenet |
| familiar | 13 | broader familiar set (cabinet, display, sofa, telephone, etc.) | shapenet |
| novel | 8 | novel abstract 3D shapes | shapegen abstract4 |

Order in the manifest: training → warmup → familiar (shuffled) →
novel (shuffled). Reminders interleaved every 10, breaks every 20.

## Image format

512px max dimension JPEGs at quality 88. Original MOCHI renders are
1000×1000 PNGs; we downsample on curation to keep page-load and Pages
deploy size manageable. ~2.5 MB total for all 105 images.

## Re-curating

```bash
# Download MOCHI parquet (~365 MB, gated via HF token only if you want
# the metadata; the images themselves are public)
pip install huggingface_hub datasets pyarrow pillow
python -c "from huggingface_hub import snapshot_download; \
  snapshot_download(repo_id='tzler/MOCHI', repo_type='dataset', local_dir='./MOCHI')"

# Re-run the curate logic (lives in the git history; the snippet
# is also in the README at the project root). Replaces this folder
# wholesale and rewrites public/manifest.json.
```

## Citation

If you publish using these trials, cite MOCHI:

> Bonnen, T., Fu, S., Bai, Y., O'Connell, T., Friedman, Y., Kanwisher,
> N., Tenenbaum, J. B., & Efros, A. A. (2024). Evaluating Multiview
> Object Consistency in Humans and Image Models. NeurIPS Datasets
> & Benchmarks. arXiv:2409.05862.
