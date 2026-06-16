# Product Engineering Document (PED)

**Project Name:** Nexus Gaming Leaderboard System
**Architecture Style:** Service-Oriented Architecture (SOA)

## 1. System Architecture

The backend is completely decoupled into five independent engines, communicating via HTTP REST APIs. An API Gateway serves as the single point of entry for all external traffic, ensuring the internal architecture remains hidden and secure. All unique identifiers across the system utilize **UUIDv4** to prevent ID collision and ensure global uniqueness.

## 2. Tech Stack & Service Boundaries

| Engine                 | Technology                | Port   | Primary Responsibility                                                              |
| ---------------------- | ------------------------- | ------ | ----------------------------------------------------------------------------------- |
| **api_gateway_engine** | Python (FastAPI)          | `8000` | Routes external client requests to the appropriate internal microservice.           |
| **player_engine**      | Python (Django)           | `8001` | Manages player accounts. Handles database reads/writes for user profiles.           |
| **match_engine**       | Node.js (Express)         | `8002` | High-throughput ingestion of match scores.                                          |
| **leaderboard_engine** | Python (Flask)            | `8003` | Data aggregation. Fetches scores, cross-references player UUIDv4s, and sorts ranks. |
| **ai_engine**          | Python (FastAPI + Ollama) | `8004` | Interfaces with a local LLM to generate dynamic text based on match outcomes.       |

## 3. Database Strategy

To adhere strictly to SOA principles, services will **not** share a database.

* **Player Engine:** `players.sqlite3` (Managed by Django ORM)
* Primary Key: `id` (UUIDv4)


* **Match Engine:** `matches.sqlite3` (Managed by Node.js / Knex or Prisma)
* Primary Key: `id` (UUIDv4)
* Foreign Reference: `player_id` (UUIDv4) - Acts as a soft link to the Player Engine.


* *(Note: Gateway, Leaderboard, and AI engines are stateless and do not require primary persistent databases).*

## 4. Internal API Contracts (Service-to-Service)

These endpoints are internal to the cluster and not exposed to the public internet.

* `GET /internal/players/{uuidv4}` (Player Engine) -> Returns username for Leaderboard aggregation.
* `GET /internal/scores/top` (Match Engine) -> Returns raw top scores for Leaderboard aggregation.
* `POST /internal/generate/hype` (AI Engine) -> Accepts score/rank data, returns generated LLM text.

## 5. External API Gateway Endpoints (Client-Facing)

All requests to the Gateway are forwarded internally.

* `POST /api/v1/players/register` -> Routes to `player_engine`
* `POST /api/v1/scores` -> Routes to `match_engine`
* `GET /api/v1/leaderboard` -> Routes to `leaderboard_engine` (which simultaneously calls `ai_engine`)

## 6. Error Handling & Resilience

* The Gateway acts as a circuit breaker. If `ai_engine` fails, the `api_gateway_engine` will return the leaderboard data with a default hardcoded message rather than failing the entire request (500 Error).
* If `match_engine` is under heavy load or offline, `player_engine` remains unaffected, allowing new user registrations to continue processing normally.