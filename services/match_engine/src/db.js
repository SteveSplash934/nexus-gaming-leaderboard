import { Database } from "bun:sqlite";
import path from "path";
import fs from "fs";

// Mount the volume inside Docker or fallback to the local project dir
const dbDir = fs.existsSync("/app/data") ? "/app/data" : ".";
const dbPath = path.join(dbDir, "matches.sqlite3");

const db = new Database(dbPath);

// Initialize high-throughput database structure
db.run(`
  CREATE TABLE IF NOT EXISTS match_scores (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    score INTEGER NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Crucial: Index the soft foreign key to prevent slow table scans as records pile up
db.run(`CREATE INDEX IF NOT EXISTS idx_player_id ON match_scores (player_id)`);

export default db;
