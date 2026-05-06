# server/

Express + MongoDB server for collecting trial data. Mirrors the lab's
existing `Insert(data, participantID, 'participantID')` pattern from
`hybrid-drawing-rating`.

The static client (`public/`) tries to POST every completed session to
`DEFAULT_SUBMIT_URL` defined at the top of `public/index.html`. Override
per-session with `?submit_url=https://...`.

## Endpoints

- `POST /submit` — receives `{ participantID, data }` JSON, upserts on
  `participantID`. Returns `{ ok: true, result }` on success.
- `GET  /health` — returns `{ ok: true, db: <bool> }` for monitoring.

The server also serves `../public` statically at `/`, so you can deploy
both the game and the API together.

## Environment

Copy `.env.example` to `.env` and fill in:

```bash
PORT=8080
MONGO_URL=mongodb+srv://USER:PASS@CLUSTER.mongodb.net    # vislearnlab Atlas conn string
DATABASE=mochi_kids
COLLECTION=trials
```

## Running locally

```bash
cd server
cp .env.example .env       # then edit MONGO_URL
npm install
npm start                  # http://localhost:8080
```

Open `http://localhost:8080` and the game saves to your configured
collection.

## Deploying to vislearnlab MongoDB

The static site is hosted on GitHub Pages (no server). To save to the
lab's MongoDB, deploy this Express server somewhere and point the client
at it.

### Option A — Render (free tier, zero-config)

1. Sign in to [render.com](https://render.com) with the lab GitHub.
2. New → Web Service → connect `vislearnlab/mochi-kids` → root directory
   `server/`. Render auto-detects Node and runs `npm install && npm start`.
3. Add env vars under Settings → Environment:
   - `MONGO_URL` = the lab Atlas connection string (Settings → Database
     access in Atlas; whitelist `0.0.0.0/0` so Render can reach it, or
     use the Render outbound IP)
   - `DATABASE` = `mochi_kids`
   - `COLLECTION` = `trials`
4. After first deploy you'll have a URL like
   `https://vislearnlab-mochi.onrender.com`. Set it as
   `DEFAULT_SUBMIT_URL` in `public/index.html` (already a one-line
   constant for this purpose):
   ```js
   const DEFAULT_SUBMIT_URL = 'https://vislearnlab-mochi.onrender.com/submit';
   ```
5. Push that change to `main`; Pages re-deploys; the live game now
   POSTs every session to your Render server, which writes to the lab
   MongoDB.

### Option B — Fly.io / Railway / EC2

Same shape — any host that runs Node can host this. Configure the same
env vars, expose port 8080, and update `DEFAULT_SUBMIT_URL` in the
client.

### Option C — point at an existing lab endpoint

If the lab already runs an Express+MongoDB service that uses the
`Insert(data, participantID, 'participantID')` upsert pattern (e.g.,
the same backend as `hybrid-drawing-rating`), point
`DEFAULT_SUBMIT_URL` at it directly. The kid game's payload shape
matches.

## CORS

`server.js` enables CORS wide-open by default (`cors()` with no
options). Lock it down to your study domain before going to production:

```js
app.use(cors({
  origin: ['https://vislearnlab.github.io', 'http://localhost:8000'],
  methods: ['POST'],
}));
```

If the client can't POST cross-origin, the thank-you page falls back
to a "Download my data" button so pilot data isn't lost.

## What gets stored

One document per `participantID`, upserted as the experiment finishes.
Document shape matches the `data` payload from the client:

```js
{
  participantID: "kid_xxxx",
  study: "mochi_kids_v1",
  consent: { age: "6", agreed: true },
  finishedAt: "2026-05-05T18:32:12.345Z",
  n_trials: 74, n_correct: 58, mean_rt: 3145.2,
  trials: [{ task: "mochi_oddity", trial_id, correct, rt, … }],
  ua: "...", screen: { w, h, dpr },
  createdAt, updatedAt
}
```

Re-runs with the same `participantID` overwrite cleanly — useful for
mid-session resumes if the kid clicks away and comes back.
