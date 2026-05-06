"""Pull all sessions from the lab Mongo collection and flatten to CSV.

Run from repo root:
    python3 analysis/fetch_data.py

Reads connection info from .env. Writes:
    analysis/data/sessions.csv   one row per participant
    analysis/data/trials.csv     one row per trial (long format)
    analysis/data/raw.json       raw documents
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

OUT = ROOT / "analysis" / "data"
OUT.mkdir(parents=True, exist_ok=True)

MONGO_URL = os.environ["MONGO_URL"]
DATABASE = os.environ.get("DATABASE", "mochi_kids")
COLLECTION = os.environ.get("COLLECTION", "trials")

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=8000)
coll = client[DATABASE][COLLECTION]

# Skip probe / debug docs whose participantID starts with "__".
docs = list(coll.find({"participantID": {"$not": {"$regex": "^__"}}}))
print(f"fetched {len(docs)} sessions from {DATABASE}.{COLLECTION}")


def _json_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)


with open(OUT / "raw.json", "w") as f:
    json.dump(docs, f, indent=2, default=_json_default)

session_rows = []
trial_rows = []
for d in docs:
    pid = d.get("participantID")
    consent = d.get("consent") or {}
    screen = d.get("screen") or {}
    session_rows.append({
        "participantID": pid,
        "study": d.get("study"),
        "consent_age": consent.get("age"),
        "consent_agree": consent.get("agree"),
        "finishedAt": d.get("finishedAt"),
        "n_trials": d.get("n_trials"),
        "n_correct": d.get("n_correct"),
        "mean_rt": d.get("mean_rt"),
        "ua": d.get("ua"),
        "screen_w": screen.get("w"),
        "screen_h": screen.get("h"),
        "screen_dpr": screen.get("dpr"),
    })
    for i, t in enumerate(d.get("trials") or []):
        trial_rows.append({
            "participantID": pid,
            "consent_age": consent.get("age"),
            "trial_index": i,
            "trial_id": t.get("trial_id"),
            "tier": t.get("tier"),
            "dataset": t.get("dataset"),
            "condition": t.get("condition"),
            "n_objects": t.get("n_objects"),
            "oddity_index_orig": t.get("oddity_index_orig"),
            "chosen_orig_index": t.get("chosen_orig_index"),
            "chosen_display_pos": t.get("chosen_display_pos"),
            "correct": t.get("correct"),
            "rt": t.get("rt"),
            "human_avg_adult": t.get("human_avg_adult"),
            "score_after": t.get("score_after"),
        })

SESSION_COLS = [
    "participantID", "study", "consent_age", "consent_agree", "finishedAt",
    "n_trials", "n_correct", "mean_rt", "ua",
    "screen_w", "screen_h", "screen_dpr",
]
TRIAL_COLS = [
    "participantID", "consent_age", "trial_index", "trial_id", "tier",
    "dataset", "condition", "n_objects", "oddity_index_orig",
    "chosen_orig_index", "chosen_display_pos", "correct", "rt",
    "human_avg_adult", "score_after",
]
pd.DataFrame(session_rows, columns=SESSION_COLS).to_csv(OUT / "sessions.csv", index=False)
pd.DataFrame(trial_rows, columns=TRIAL_COLS).to_csv(OUT / "trials.csv", index=False)
print(f"wrote {OUT}/sessions.csv ({len(session_rows)} rows)")
print(f"wrote {OUT}/trials.csv ({len(trial_rows)} rows)")
client.close()
