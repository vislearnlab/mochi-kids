# MOCHI Kids — Shape Detective

A kid-friendly (4–6 year olds) adaptation of the MOCHI 3D-shape oddity
benchmark (Bonnen et al., NeurIPS 2024 D&B). Three-image trials: two
views of the same object, one different — tap the odd one out.

Live demo: **https://vislearnlab.github.io/mochi-kids/**

[![tests](https://github.com/vislearnlab/mochi-kids/actions/workflows/test.yml/badge.svg)](https://github.com/vislearnlab/mochi-kids/actions/workflows/test.yml)
[![pages](https://github.com/vislearnlab/mochi-kids/actions/workflows/pages.yml/badge.svg)](https://github.com/vislearnlab/mochi-kids/actions/workflows/pages.yml)

## Quick start

```bash
# play it locally
make serve                  # or: cd public && python3 -m http.server 8000

# run all tests
make test
```

Or double-click `start.command` from Finder on macOS.

## What's here

```
mochi-kids/
├── public/                    # the static site GH Pages serves   → public/README.md
│   ├── index.html             # single-file jsPsych v8 experiment
│   ├── manifest.json          # 35 curated trials
│   ├── stimuli/<trial>/0..2.jpg
│   └── images/zorpie/         # mascot GIFs (from vislearnlab/museumkiosk)
├── server/                    # optional Express + MongoDB save layer  → server/README.md
├── rendering/                 # rotation-animation pipeline (planned)  → rendering/README.md
├── tests/                     # asset-integrity + Playwright e2e       → tests/README.md
├── docs/                      # research artifacts (figures, sims)     → docs/README.md
├── .github/workflows/         # CI (test) + GH Pages (pages)           → .github/README.md
├── TESTING.md                 # full testing strategy
├── start.command              # double-click → serves locally + opens browser
└── push_to_vislearnlab.command  # one-click: gh repo create + push + enable Pages
```

## Trial set (35 trials, two datasets)

| tier | n | dataset | filter | adult acc |
| --- | --- | --- | --- | --- |
| training | 6 | synthesized | same image × 2 + 1 different image (pop-out) | trivial |
| warmup | 8 | shapenet | chair, lamp, bench; adjacent viewpoints; RT < 2.5s | 1.0 |
| familiar | 13 | shapenet | broader real-object set | 1.0 |
| novel | 8 | shapegen | abstract4 (easiest abstract shape bin) | 1.0 |

All MOCHI trials filtered to `human_avg = 1.0` *and* `RT < 2500 ms` so
kids see only trials that adults nailed quickly. No `majaj` (HVM /
Yamins-lab images) and no `barense` (faces).

See [`public/stimuli/README.md`](public/stimuli/README.md) for the
full curate logic.

## Reward design (intentionally minimal)

- **No spoken voice anywhere.** First-pass voice prompts via gTTS were
  too robotic; we removed them. On-screen text is sized for a parent to
  read aloud if the kid can't read yet.
- **Reward audio = chime only.** A C-major arpeggio synthesized live
  via Web Audio API on every correct answer. No sound on wrong (no
  harsh buzzer). 16-particle multi-color sparkle burst from the correct
  card. Score pill in the HUD pops when it ticks up. 5-star end screen
  scaled to accuracy.

## Data shape

Each completed session POSTs (or the kid downloads) one JSON document:

```json
{
  "participantID": "kid_xxxx",
  "study": "mochi_kids_v1",
  "consent": { "age": "6", "agreed": true },
  "n_trials": 35, "n_correct": 28, "mean_rt": 3145.2,
  "trials": [{ "task": "mochi_oddity", "trial_id": "shapenet1234",
               "tier": "familiar", "correct": true, "rt": 2810.4, ... }]
}
```

When running via GitHub Pages (no server), the user gets a
"Download my data" button on the end screen. When running with the
Express server (`cd server && npm start`), the same payload is
upserted to MongoDB on `participantID`.

## Testing

CI runs the full suite on every push to `main`. Three layers:

1. **Static** — JS syntax (`node --check`), Python compile, manifest
   schema + image existence checks
2. **End-to-end** — Playwright drives a real headless Chromium through
   the entire experiment (consent, all 35 trials, breaks, reminders,
   end screen) and asserts no console errors, all RTs captured,
   double-clicks ignored
3. **Server** *(optional, planned)* — supertest against `/submit` with
   in-memory MongoDB

Locally: `make test` or `bash tests/run_all.sh`.

Full strategy: [TESTING.md](TESTING.md).

## Deploying

- **GitHub Pages** (no server) — `git push` to `main`. The
  `pages.yml` workflow publishes `public/` automatically. Live URL:
  `https://vislearnlab.github.io/mochi-kids/`.
- **Lab server** (with MongoDB save) — see
  [`server/README.md`](server/README.md).

The static client auto-disables `/submit` POSTs on `*.github.io`,
`*.web.app`, and similar hosts.

## Roadmap

- [x] Static play-through w/ jsPsych v8, kid-friendly UX
- [x] Curated 35-trial easy-tail set
- [x] Consent + age picker
- [x] CI + automated tests
- [ ] Rotation-animation manipulation (waiting on ShapeNet GLB access
      and shapegen meshes from Bonnen — see
      [`rendering/README.md`](rendering/README.md))
- [ ] Real pilot with N≈30 kids per age
- [ ] Pre-registration of the human-model dissociation hypothesis

## Citation

If you publish work using this code or stimuli, please cite the MOCHI
benchmark:

```
Bonnen, T., Fu, S., Bai, Y., O'Connell, T., Friedman, Y., Kanwisher, N.,
Tenenbaum, J. B., & Efros, A. A. (2024). Evaluating Multiview Object
Consistency in Humans and Image Models. NeurIPS Datasets & Benchmarks.
arXiv:2409.05862.
```

## Acknowledgments

Mascot art (Zorpie) from
[brialorelle/museumkiosk](https://github.com/brialorelle/museumkiosk).
Stimuli from MOCHI on Hugging Face. Schoolbell font from Google Fonts.
jsPsych v8.
