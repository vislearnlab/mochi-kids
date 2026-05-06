// MOCHI Kids — Express + MongoDB server.
// Mirrors the hybrid-drawing-rating pattern:
//   POST /submit  -> Insert(data, participantID, 'participantID')
//
// The Insert helper upserts on participantID, so partial submissions overwrite
// cleanly mid-experiment (matches the lab's existing convention).

require('dotenv').config();
const path = require('path');
const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');

const PORT = process.env.PORT || 8080;
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DATABASE = process.env.DATABASE || 'mochi_kids';
const COLLECTION = process.env.COLLECTION || 'trials';

const app = express();
app.use(cors());
app.use(express.json({ limit: '20mb' }));

// Static client (the public/ folder one level up).
app.use(express.static(path.join(__dirname, '..', 'public')));

let db;
async function initDB() {
  const client = new MongoClient(MONGO_URL);
  await client.connect();
  db = client.db(DATABASE);
  console.log(`[mochi-kids] connected to ${MONGO_URL} :: ${DATABASE}`);
}

// Upsert helper — same shape as Insert(data, participantID, 'participantID') in the lab repo.
async function Insert(data, keyValue, keyField) {
  const filter = { [keyField]: keyValue };
  const update = {
    $set: { ...data, [keyField]: keyValue, updatedAt: new Date() },
    $setOnInsert: { createdAt: new Date() },
  };
  return db.collection(COLLECTION).updateOne(filter, update, { upsert: true });
}

app.post('/submit', async (req, res) => {
  try {
    const { participantID, data } = req.body || {};
    if (!participantID) return res.status(400).json({ ok: false, error: 'missing participantID' });
    const result = await Insert(data || {}, participantID, 'participantID');
    res.json({ ok: true, result });
  } catch (err) {
    console.error('[submit] error', err);
    res.status(500).json({ ok: false, error: String(err) });
  }
});

app.get('/health', (_req, res) => res.json({ ok: true, db: !!db }));

initDB().then(() => {
  app.listen(PORT, () => console.log(`[mochi-kids] http://localhost:${PORT}`));
}).catch(err => {
  console.error('failed to start', err);
  process.exit(1);
});
