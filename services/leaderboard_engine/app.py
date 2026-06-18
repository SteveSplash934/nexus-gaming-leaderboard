import os
import requests
from flask import Flask, jsonify

# Safely load dotenv if present (prevents ModuleNotFoundError in Docker)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

PLAYER_ENGINE_URL = os.environ.get("PLAYER_ENGINE_URL", "http://player-engine:8001")
MATCH_ENGINE_URL = os.environ.get("MATCH_ENGINE_URL", "http://match-engine:8002")
AI_ENGINE_URL = os.environ.get("AI_ENGINE_URL", "http://ai-engine:8004")

# Diagnostics: Prints out your active URLs on startup
print("\n" + "="*50)
print("LEADERBOARD ENGINE STARTUP ROUTING INFO")
print(f" * Player Engine:      {PLAYER_ENGINE_URL}")
print(f" * Match Engine:       {MATCH_ENGINE_URL}")
print(f" * AI Engine:          {AI_ENGINE_URL}")
print("="*50 + "\n")

http_client = requests.Session()
http_client.trust_env = False

@app.route("/api/v1/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        # 1. Query Match Engine for top standings
        match_response = http_client.get(f"{MATCH_ENGINE_URL}/internal/scores/top", timeout=2.0)
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
                player_response = http_client.get(f"{PLAYER_ENGINE_URL}/internal/players/{player_id}", timeout=1.5)
                if player_response.status_code == 200:
                    username = player_response.json().get("data", {}).get("username", "Unknown Player")
                else:
                    username = "Unknown Player"
            except requests.RequestException as e:
                print(f"DEBUG Error: Could not resolve player {player_id}. Details: {e}")
                username = "Unknown Player"
                
            ranks.append({
                "player_id": player_id,
                "username": username,
                "high_score": high_score
            })
            
        # 3. Request AI Hype Message
        ai_hype_message = "Oops! The dynamic AI hype engine is temporarily offline."
        if ranks:
            try:
                top_player = ranks[0]
                payload = {
                    "username": top_player["username"],
                    "high_score": top_player["high_score"]
                }
                ai_response = http_client.post(f"{AI_ENGINE_URL}/internal/generate/hype", json=payload, timeout=5.0)
                if ai_response.status_code == 200:
                    ai_hype_message = ai_response.json().get("data", {}).get("hype_message", ai_hype_message)
                else:
                    print(f"DEBUG Error: AI Engine returned status code {ai_response.status_code}")
            except requests.RequestException as e:
                # Diagnostics: Print why the AI connection is failing
                print(f"DEBUG Error: Connection to AI Engine failed at {AI_ENGINE_URL}. Details: {e}")

        return jsonify({
            "success": True,
            "message": "Global leaderboard fetched successfully",
            "data": {
                "ranks": ranks,
                "ai_hype_message": ai_hype_message
            }
        }), 200

    except requests.RequestException as e:
        print(f"DEBUG Error: Critical dependency unreachable. Details: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "DEPENDENCY_ERROR",
                "message": "Oops! A critical dependency service is currently offline or unreachable."
            }
        }), 503
        
    except Exception as e:
        print(f"DEBUG Error: Unexpected exception. Details: {e}")
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