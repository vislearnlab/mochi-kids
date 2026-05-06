# server/

Optional Express + MongoDB server for collecting trial data when the
game is not running on a static-only host.

The static site (`public/`) auto-detects `*.github.io`, `*.web.app`,
etc. and disables saving. So you only need this server when running the
study from a dedicated lab host (e.g., a Render / Fly / EC2 box that
also has access to your MongoDB cluster).

## Endpoints

`POST /submit` — receives `{ participantID, data }` JSON, upserts on
`participantID` (matches the lab's
`Insert(data, participantID, 'participantID')` convention from
`hybrid-drawing-rating`).

`GET /health` — returns `{ ok: true, db: <bool> }` for monitoring.

The static site is served from `/` (the server statically serves
`../public`).

## Environment variables

```bash
# server/.env (copy from .env.example)
PORT=8080
MONGO_URL=mongodb://localhost:27017
DATABASE=mochi_kids
COLLECTION=trials
```

## Running locally

```bash
cd server
cp .env.example .env       # then edit
npm install
npm start                  # http://localhost:8080
```

Open `http://localhost:8080` and the game saves trial data to your
configured collection.

## What gets stored

One document per `participantID`, upserted as the experiment finishes.
Document body matches the `data` payload from the client:

```js
{
  participantID: "kid_xxxx",
  study: "mochi_kids_v1",
  consent: { age: "6", agreed: true },
  finishedAt: "2026-05-05T18:32:12.345Z",
  n_trials: 35, n_correct: 28, mean_rt: 3145.2,
  trials: [ { task: "mochi_oddity", trial_id, correct, rt, … } ],
  ua: "...", screen: { w, h, dpr },
  createdAt, updatedAt
}
```

## Deploying

Any Node hosting platform works. Render and Fly are easy; both honor
the env vars above. Point your DNS at the deployed URL and update
the `?submit_url=` parameter on the static site if hosting client
and server on different origins.

CORS is wide-open by default (`cors()` with no options). Lock it down
to your study domain before going to production.
