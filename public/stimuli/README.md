# public/stimuli/

80 curated trials, each in its own folder. Every trial is a 3-image
oddity (3AFC): two viewpoints of the same object + one different
object's viewpoint.

```
stimuli/
├── training_00/0.jpg, 1.jpg, 2.jpg     # 12 synthesized pop-out trials
├── shapenet1234/0.jpg, 1.jpg, 2.jpg     # 60 shapenet trials (warmup + familiar)
└── shapegen2486/0.jpg, 1.jpg, 2.jpg     #  8 novel abstract4 trials
```

## How these were curated

Source: `tzler/MOCHI` on Hugging Face (Bonnen et al., NeurIPS 2024 D&B).

Strategy: per-category, sort by adult accuracy desc (then RT_avg asc)
and take the easiest N — instead of a hard `human_avg ≥ 0.95` cutoff
that excluded kid-friendly categories like car/airplane/sofa/table.
Each manifest entry preserves `human_avg_adult` and `rt_avg_adult` so
calibration analyses can use them as continuous difficulty signals.

Categories chosen for kid familiarity. Dropped: watercraft, cabinet,
loudspeaker, display.

## Tier composition

| tier | n | what | source |
| --- | --- | --- | --- |
| training | 12 | same image duplicated × 2 + a different image | synthesized at curate time |
| warmup | 12 | easiest chair/lamp/bench (mean adult acc=1.0) | shapenet |
| familiar | 48 | 8 categories × 6 each: chair, lamp, bench, telephone, car, airplane, sofa, table | shapenet |
| novel | 8 | easiest `abstract4` only | shapegen |

Order in the manifest: training → warmup → familiar (shuffled) →
novel (shuffled). Reminders interleaved every 10, breaks every 20.

## Image format

512px max dimension JPEGs at quality 88. Original MOCHI renders are
1000×1000 PNGs; we downsample on curation to keep page-load and Pages
deploy size manageable. ~2 MB total for all 240 images.

## Re-curating

```bash
# 1. Download the MOCHI parquet (~365 MB, gitignored at rendering/MOCHI/)
pip install huggingface_hub pyarrow pillow
python -c "from huggingface_hub import snapshot_download; \
  snapshot_download(repo_id='tzler/MOCHI', repo_type='dataset', \
                    local_dir='rendering/MOCHI')"

# 2. Re-run the curate. Edit rendering/curate_kids.py to change the
#    tier composition / category list / per-category counts.
python3 rendering/curate_kids.py
```

## Citation

If you publish using these trials, cite MOCHI:

> Bonnen, T., Fu, S., Bai, Y., O'Connell, T., Friedman, Y., Kanwisher,
> N., Tenenbaum, J. B., & Efros, A. A. (2024). Evaluating Multiview
> Object Consistency in Humans and Image Models. NeurIPS Datasets
> & Benchmarks. arXiv:2409.05862.
