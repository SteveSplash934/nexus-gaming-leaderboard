import express from "express";
import cors from "cors";
import { v4 as uuidv4 } from "uuid";
import db from "./db.js";

const app = express();
const PORT = 8002;

app.use(cors());
app.use(express.json());

// ---------------------------------------------------------------------------
// External Route (Invoked via API Gateway)
// ---------------------------------------------------------------------------
app.post("/api/v1/scores", (req, res) => {
  try {
    const { player_id, score } = req.body;

    if (!player_id || typeof score !== "number" || score < 0) {
      return res.status(422).json({
        success: false,
        error: {
          code: "VALIDATION_ERROR",
          message: "Invalid request payload. Score must be positive.",
        },
      });
    }

    const id = uuidv4();

    // Bun's native SQLite query preparation (extremely fast)
    const query = db.prepare(
      "INSERT INTO match_scores (id, player_id, score) VALUES (?, ?, ?)",
    );
    query.run(id, player_id, score);

    return res.status(201).json({
      success: true,
      message: "Match score recorded successfully",
    });
  } catch (error) {
    console.error("Match Engine Ingestion Error:", error);
    return res.status(500).json({
      success: false,
      error: {
        code: "SERVER_ERROR",
        message: "An internal database error occurred while saving the match.",
      },
    });
  }
});

// ---------------------------------------------------------------------------
// Internal Route (Invoked by Leaderboard Engine)
// ---------------------------------------------------------------------------
app.get("/internal/scores/top", (req, res) => {
  try {
    // Get high score grouped by player, ordered descending, limit to top 10
    const query = db.prepare(`
      SELECT player_id, MAX(score) as high_score 
      FROM match_scores 
      GROUP BY player_id 
      ORDER BY high_score DESC 
      LIMIT 10
    `);

    const rows = query.all();

    return res.status(200).json({
      success: true,
      data: rows,
    });
  } catch (error) {
    console.error("Match Engine Query Error:", error);
    return res.status(500).json({
      success: false,
      error: {
        code: "SERVER_ERROR",
        message: "Could not retrieve leaderboard standings.",
      },
    });
  }
});

// Health check
app.get("/health", (req, res) => {
  res.status(200).json({ success: true, service: "match_engine" });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Match Engine operational on Bun on port ${PORT}`);
});
