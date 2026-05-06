# MOCHI Kids — Shape Detective

A kid-friendly (4–6 year olds) adaptation of the MOCHI 3D-shape oddity task
(Bonnen et al., NeurIPS 2024). Three-image trials: two views of the same
object, one different — tap the odd one out.

## What's here

```
mochi-kids/
├── public/
│   ├── index.html          # jsPsych v8 game (single-page, CDN-loaded)
│   ├── manifest.json       # 30 curated trials w/ metadata
│   └── stimuli/<trial>/0.jpg, 1.jpg, 2.jpg
├── server/
│   ├── server.js           # Express + MongoDB; mirrors hybrid-drawing-rating /submit
│   ├── package.json
│   └── .env.example
└── README.md
```

## Trial set (59 trials, 15 conditions)

Curated from MOCHI's 2,019 trials by adult `human_avg` and kid-friendliness:

| Tier | Count | Conditions | Adult acc. floor |
| --- | --- | --- | --- |
| warmup | 10 | animals, chairs, lamp, chair | ≥ 0.95 |
| main | 39 | chair, bench, lamp, table, sofa, watercraft, cabinet, telephone, display, loudspeaker, animals, chairs | ≥ 0.80 |
| stretch | 10 | abstract4, abstract3, abstract2 (easier shapegen) | ≥ 0.90 |

Order in `manifest.json`: warmup first, then main (shuffled), then stretch
(shuffled). Re-curate by re-running the python in the curate section below.
A wiggle break is inserted every 12 trials.

All trials are 3-image (3AFC) so the layout stays consistent for kids.

## Audio (slim by design)

Spoken voice fires only at structured moments — never per-trial — so the
soundscape doesn't feel chatty:

| When | What plays |
| --- | --- |
| Welcome | `welcome.mp3` (Beep introduces himself) |
| How-to-play | `how_to_play.mp3` |
| Every 10 trials (`?reminder_every=N`) | `reminder.mp3` ("Remember, two are the same…") |
| Every 20 trials (`?break_every=N`) | `break_time.mp3` / `break_water.mp3` (alternates) |
| End | `all_done.mp3` |

Reward audio = **chime only**. A C-major arpeggio (Web Audio API,
synthesized live, zero files) plays on every correct response. Wrong
responses get visual feedback only — a gentle shake and the right answer
briefly highlighted — no sound, no harsh buzzer.

Pre-rendered prompts live in `public/audio/`, generated with Google TTS
(en-us). Extra `praise_*` and `gentle_*` mp3s are kept on disk so you can
swap them back in later if you want per-trial verbal feedback.

## Mascot — meet Beep

A friendly waving robot (`public/images/robot_wave.gif`, generated with
PIL) shows up on every screen with words on it:
- Welcome + how-to-play (large)
- Every reminder (medium)
- Every break (large)
- End screen (large)

He doesn't appear during trials so kids stay focused on the stimuli.

## Visual rewards (per trial)

- Card border bounce on correct, shake on wrong
- 16-particle multicolor sparkle burst from the correct card
- Score pill in the top-right HUD pops when it ticks up
- 5-star end screen scaled to accuracy

## Run it locally

### Quick preview (no server)

```bash
cd mochi-kids/public
python3 -m http.server 8000
# open http://localhost:8000?save=false
```

`?save=false` skips the POST to `/submit` — useful for the static preview.
At the end of the session there's a "Download my data" button that saves the
session JSON locally.

### Full run (with MongoDB save)

```bash
cd mochi-kids/server
cp .env.example .env       # edit MONGO_URL etc.
npm install
npm start
# open http://localhost:8080
```

The server serves `../public` statically and exposes `POST /submit`.

## URL parameters (client)

| Param | Default | Purpose |
| --- | --- | --- |
| `participantID` | random `kid_xxxxxxxx` | Prolific / SONA / lab ID. Same key the server upserts on. |
| `study` | `mochi_kids_v1` | Study tag stored with the record. |
| `consent` | `true` | Set to `false` to flag a no-consent / preview run. |
| `save` | `true` | Set to `false` to skip the network save (works fully offline). |
| `submit_url` | `/submit` | Override if hosting client and server on different origins. |

## Data shape (POSTed to `/submit`)

```json
{
  "participantID": "kid_abcd1234",
  "data": {
    "participantID": "kid_abcd1234",
    "study": "mochi_kids_v1",
    "consent": true,
    "finishedAt": "2026-05-05T18:32:12.345Z",
    "n_trials": 30,
    "n_correct": 26,
    "mean_rt": 3145.2,
    "trials": [
      {
        "task": "mochi_oddity",
        "trial_id": "hvm90",
        "dataset": "majaj",
        "condition": "animals",
        "tier": "warmup",
        "n_objects": 3,
        "oddity_index_orig": 1,
        "chosen_orig_index": 1,
        "chosen_display_pos": 2,
        "display_order": [2, 0, 1],
        "correct": true,
        "rt": 2810.4,
        "human_avg_adult": 1.0
      }
    ],
    "ua": "...",
    "screen": { "w": 1440, "h": 900, "dpr": 2 }
  }
}
```

The server upserts on `participantID` (matches the lab's
`Insert(data, participantID, 'participantID')` convention), so re-submits
overwrite cleanly.

## Audio prompts

Uses the Web Speech API for kid-friendly TTS. No audio files to manage. If
you want pre-recorded prompts later, drop MP3s in `public/audio/` and replace
the `speak(...)` calls in `index.html`.

Browsers vary in voice quality. On macOS Safari/Chrome you'll get "Samantha"
or similar — fine for testing. For deployment to schools, pre-recorded audio
is more reliable across devices.

## Re-curating trials

The trials in `manifest.json` are a curated subset of MOCHI. To pick a
different set:

```bash
# Download MOCHI from Hugging Face (~365 MB)
pip install huggingface_hub datasets pyarrow pillow
python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='tzler/MOCHI', repo_type='dataset', local_dir='./MOCHI')"
```

Then run a script like the one in `scripts/curate.py` (in the repo's git
history) — it reads the parquet, filters by `condition` and `human_avg`,
extracts the PNG stimuli into `public/stimuli/<trial_id>/`, resizes to 512px,
and writes `public/manifest.json`.

## Citation

If you publish results from this game, cite the MOCHI benchmark:

```
Bonnen, T., Fu, S., Bai, Y., O'Connell, T., Friedman, Y., Kanwisher, N.,
Tenenbaum, J. B., & Efros, A. A. (2024). Evaluating Multiview Object
Consistency in Humans and Image Models. NeurIPS Datasets & Benchmarks.
arXiv:2409.05862.
```
