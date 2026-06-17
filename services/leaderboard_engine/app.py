import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Fallbacks default to Docker internal aliases, overridable locally via Env vars
PLAYER_ENGINE_URL = os.environ.get("PLAYER_ENGINE_URL", "http://player_engine:8001")
MATCH_ENGINE_URL = os.environ.get("MATCH_ENGINE_URL", "http://match_engine:8002")
AI_ENGINE_URL = os.environ.get("AI_ENGINE_URL", "http://ai_engine:8004")

@app.route("/api/v1/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        # 1. Query Match Engine for top standings
        match_response = requests.get(f"{MATCH_ENGINE_URL}/internal/scores/top", timeout=2.0)
        if match_response.status_code != 200:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MATCH_ENGINE_ERROR",
                    "message": "Oops! Could not retrieve the current standings from the Match Engine."
                }
            }), 502
            
        raw_scores = match_response.json().get("data", [])
        
        # 2. Map UUIDs to usernames via Player Engine
        ranks = []
        for score_record in raw_scores:
            player_id = score_record.get("player_id")
            high_score = score_record.get("high_score")
            
            try:
                player_response = requests.get(f"{PLAYER_ENGINE_URL}/internal/players/{player_id}", timeout=1.5)
                if player_response.status_code == 200:
                    username = player_response.json().get("data", {}).get("username", "Unknown Player")
                else:
                    username = "Unknown Player"
            except requests.RequestException:
                # Fail-safe: if Player Engine is offline, do not crash; return rankings as "Unknown Player"
                username = "Unknown Player"
                
            ranks.append({
                "player_id": player_id,
                "username": username,
                "high_score": high_score
            })
            
        # 3. Request AI Hype Message (Fallback implementation)
        ai_hype_message = "Oops! The dynamic AI hype engine is temporarily offline."
        if ranks:
            try:
                top_player = ranks[0]
                payload = {
                    "username": top_player["username"],
                    "high_score": top_player["high_score"]
                }
                ai_response = requests.post(f"{AI_ENGINE_URL}/internal/generate/hype", json=payload, timeout=2.0)
                if ai_response.status_code == 200:
                    ai_hype_message = ai_response.json().get("data", {}).get("hype_message", ai_hype_message)
            except requests.RequestException:
                # Circuit Breaker: Keep the friendly offline string instead of failing the request
                pass

        return jsonify({
            "success": True,
            "message": "Global leaderboard fetched successfully",
            "data": {
                "ranks": ranks,
                "ai_hype_message": ai_hype_message
            }
        }), 200

    except requests.RequestException:
        # Crucial fallback if match_engine is entirely unreachable
        return jsonify({
            "success": False,
            "error": {
                "code": "DEPENDENCY_ERROR",
                "message": "Oops! A critical dependency service is currently offline or unreachable."
            }
        }), 503
        
    except Exception:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred while building the leaderboard."
            }
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "success": True,
        "service": "leaderboard_engine",
        "status": "healthy"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=True)