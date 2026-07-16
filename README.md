# MOCHI Kids — Shape Detective

A kid-friendly (4–6 year olds) adaptation of the MOCHI 3D-shape oddity
benchmark (Bonnen et al., NeurIPS 2024 D&B). Three-image trials: two
views of the same object, one different — tap the odd one out.

Live (production): **https://ucsdlearninglabs.org/mochi-kids/** — served by
the Express app on the lab Ubuntu box (pm2 + nginx), saving to MongoDB.

> A legacy static mirror also exists at
> `https://vislearnlab.github.io/mochi-kids/`, but it is **not** wired to a
> build workflow and serves an older single-file version. Treat the
> `ucsdlearninglabs.org` deployment as canonical.

[![tests](https://github.com/vislearnlab/mochi-kids/actions/workflows/test.yml/badge.svg)](https://github.com/vislearnlab/mochi-kids/actions/workflows/test.yml)

## Quick start

```bash
# install deps once
npm install

# play it locally (Vite dev server, hot reload) → http://localhost:3000
make dev                    # or: npm run dev

# run all tests
make test
```

The app is a Vite + TypeScript build — the experiment source is
`src/survey/experiment.ts`, not a static HTML file, so serving `public/`
directly will not run it. Use `npm run dev` (or `npm run build` + the
Express server).

## What's here

```
mochi-kids/
├── index.html                 # Vite entry (HUD markup, fonts)
├── src/
│   ├── survey/experiment.ts   # THE experiment — jsPsych v8 timeline, consent,
│   │                          #   trials, rewards, kiosk Stop button, end screen
│   ├── survey/assets/styles.css
│   ├── server.ts              # Express save layer (serves dist/, POST /submit)
│   └── mongo.ts               # MongoDB client
├── public/                    # static assets copied into the build (NO index.html)
│   ├── manifest.json          # 86 curated trials
│   ├── stimuli/<trial>/0..2.jpg
│   ├── audio/                 # spoken prompts (.m4a)
│   └── images/zorpie/         # mascot GIFs (from vislearnlab/museumkiosk)
├── dist/                      # `npm run build` output (gitignored)
├── analysis/                  # fetch_data.py → CSVs + sanity-check Rmd
├── rendering/                 # rotation-animation pipeline (planned)  → rendering/README.md
├── tests/                     # asset-integrity + Playwright e2e       → tests/README.md
├── docs/                      # research artifacts (figures, sims)     → docs/README.md
├── .github/workflows/         # CI (test.yml)
├── TESTING.md                 # full testing strategy
└── vite.config.mts            # build config (BASE_PATH-aware)
```

## Trial set (86 trials, gray-render only)

The authoritative composition is `public/manifest.json` (86 entries):

| tier | n | dataset | content | mean adult acc |
| --- | --- | --- | --- | --- |
| training | 12 | synthesized | same image × 2 + 1 different image (pop-out) | trivial |
| warmup | 12 | shapenet | easiest chair / lamp / bench | 1.00 |
| familiar | 28 | shapenet | 8 categories: chair, lamp, bench, telephone (4 each) + car, airplane, sofa, table (3 each) | 0.97 |
| novel | 28 | shapegen | random sample from `abstract4`/`abstract3`/`abstract2` | 0.91 |
| catch | 6 | catch | attention-check trials (used for QA / exclusions) | ~1.00 |

Familiar and novel are interleaved into a mixed block at runtime; catch
trials are sprinkled in for quality control. Each block opens with a
short Zorpie intro screen.

> Note: older pilot sessions in Mongo show different `n_trials` (74/80/86)
> and now-retired tiers (`animals`, `photos`) because the trial set evolved
> during piloting. When analyzing, group by tier from `trials.csv` rather
> than assuming a fixed count.

Each manifest entry preserves `human_avg_adult` and `rt_avg_adult`
so calibration analyses can use them directly. See
[`public/stimuli/README.md`](public/stimuli/README.md) for the curate
logic and re-run instructions.

## Audio + reward design

Spoken voice fires at three structured moments only — never per-trial,
so the soundscape stays calm:

| when | what plays |
| --- | --- |
| Consent screen | `welcome.mp3` |
| How-to-play | `how_to_play.mp3` |
| Every 10 trials (`?reminder_every=N`) | `reminder.mp3` |

Reward audio = **chime only**. A C-major arpeggio synthesized live via
Web Audio API on every correct answer. No sound on wrong (no harsh
buzzer). 16-particle multicolor sparkle burst from the correct card.
HUD score pill ticks up with a small pop animation. End screen shows
Zorpie + a count of correct answers (no star rating).

The voice files were generated with gTTS — they're functional but
robotic. Drop in real recordings at the same filenames in
`public/audio/` to upgrade with no code changes.

## URL parameters

| param | default | what it does |
| --- | --- | --- |
| `participantID` | random `kid_xxxxxxxx` | Prolific / SONA / lab ID |
| `study` | `mochi_kids_v1` | Study tag stored with the record |
| `site` | `unknown` | Collection site, stored on the record (e.g. `cdm` = Children's Discovery Museum kiosk, `lab`, `prolific`) |
| `save` | `true` (auto-`false` on `*.github.io`/`*.web.app`/etc.) | Set to `false` to skip POST |
| `submit_url` | `/submit` | Override server endpoint |
| `reminder_every` | `10` | Trials between spoken reminders |
| `break_every` | `20` | Trials between break screens |

Example: `https://ucsdlearninglabs.org/mochi-kids/?participantID=pilot01`

## Data shape

Each completed session POSTs (or the kid downloads) one JSON document:

```json
{
  "participantID": "kid_xxxx",
  "study": "mochi_kids_v1",
  "site": "cdm",
  "consent": { "age": "6", "agreed": true },
  "n_trials": 86, "n_correct": 64, "mean_rt": 3145.2,
  "trials": [{ "task": "mochi_oddity", "trial_id": "shapenet1234",
               "tier": "familiar", "condition": "chair",
               "correct": true, "rt": 2810.4,
               "oddity_index_orig": 1, "chosen_orig_index": 1,
               "display_order": [2, 0, 1], ... }]
}
```

In production (`ucsdlearninglabs.org/mochi-kids/`) the payload is POSTed
to `/submit` and upserted to MongoDB on `participantID`. When `save` is
off (e.g. the static `*.github.io` mirror, or `?save=false`), the user
instead gets a "Download my data" button on the end screen.

## Pulling & analyzing data

Connection info (`MONGO_URL`, `DATABASE=mochi_kids`, `COLLECTION=trials`)
lives in `.env` (gitignored — never commit it). To export:

```bash
python3 analysis/fetch_data.py     # → analysis/data/{sessions.csv, trials.csv, raw.json}
make sanity                        # export + knit analysis/sanity_check.Rmd (needs R)
```

`sessions.csv` is one row per participant (incl. QA flags: `qa_pass`,
`qa_mash`, `qa_low_acc`, …); `trials.csv` is long format, one row per
trial with `tier`, `correct`, `rt`. Group by `tier` for accuracy —
don't assume a fixed trial count (see the trial-set note above).

## Testing

CI runs the full suite on every push to `main`. Three layers:

1. **Static** — JS syntax (`node --check`), Python compile, manifest
   schema + image existence checks
2. **End-to-end** — Playwright drives a real headless Chromium through
   the entire experiment (consent, all trials, breaks, reminders,
   end screen) and asserts no console errors, all RTs captured,
   double-clicks ignored
3. **Server** *(optional, planned)* — supertest against `/submit` with
   in-memory MongoDB

Locally: `make test` or `bash tests/run_all.sh`.

Full strategy: [TESTING.md](TESTING.md).

## Deploying

**Production — lab Ubuntu server (canonical, with MongoDB save).**
The app runs as a pm2 process (Express server, `npm start`) on
`localhost:9009`; nginx proxies `https://ucsdlearninglabs.org/mochi-kids/`
to it. To ship a change:

```bash
# 1. locally: commit + push (NEVER commit .env or credentials)
git push origin main

# 2. on the server (ssh blong@ucsdlearninglabs.org):
cd /labs/vislearnlab/mochi-kids
git pull --ff-only origin main
npm run build
pm2 restart mochi-kids --update-env

# 3. verify the live bundle serves your change
curl -s https://ucsdlearninglabs.org/mochi-kids/ | grep -oE 'assets/index-[^"]+\.js'
```

Server config: prod `.env` lives at `/labs/vislearnlab/mochi-kids/.env`;
the nginx location is `/etc/nginx/locations/mochi-kids.locations`.

**Static mirror (legacy).** The `*.github.io` copy has no build workflow
and is stale. The client auto-disables `/submit` POSTs on `*.github.io` /
`*.web.app` so that mirror falls back to the "Download my data" button.

## Roadmap

- [x] Static play-through w/ jsPsych v8, kid-friendly UX
- [x] Curated 86-trial easy-tail set (familiar real objects + novel
      abstract shapes)
- [x] Consent + age picker, scoped audio (welcome, how-to-play, every
      10-trial reminder)
- [x] CI + automated tests, GH Pages deploy
- [ ] Real pilot — N≈30 kids per age (4, 5, 6) + matched adult sample
- [ ] Rotation-animation manipulation (within-subjects ±45° yaw on a
      random half of trials — waiting on ShapeNet GLB access and
      shapegen meshes from Bonnen; see
      [`rendering/README.md`](rendering/README.md))
- [ ] Pre-registration of the human-model crossover hypothesis (kids
      beat models on familiar real objects, models beat kids on novel
      abstracts — see `docs/simulated_results.png` for the predicted
      pattern)
- [ ] Replace gTTS prompts with a real recorded voice

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
Stimuli from [tzler/MOCHI](https://huggingface.co/datasets/tzler/MOCHI)
on Hugging Face. Schoolbell font from Google Fonts. jsPsych v8.
