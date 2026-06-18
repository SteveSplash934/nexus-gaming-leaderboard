# API Gateway Engine

The API Gateway Engine serves as the single public-facing entry point and traffic orchestrator for the Nexus Gaming Leaderboard System. It manages external client traffic, isolates internal microservices from direct public exposure, validates incoming request formats, and implements circuit-breaking logic to handle downstream timeouts or failures.

## Technical Specifications

* **Runtime:** Python 3.13
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Communication Protocol:** Asynchronous HTTP/1.1 (via httpx)
* **Default Port:** 8000 (Exposed publicly)

## Core Responsibilities

### 1. Request Proxying
The Gateway translates public API requests into internal network requests. Clients communicate strictly with the Gateway on Port 8000, which then routes the payloads asynchronously to the designated internal engines:
* `POST /api/v1/players/register` proxies to `http://player-engine:8001/api/v1/players/register`
* `POST /api/v1/scores` proxies to `http://match-engine:8002/api/v1/scores`
* `GET /api/v1/leaderboard` proxies to `http://leaderboard-engine:8003/api/v1/leaderboard`

### 2. Defensive Validation (Fail-Fast)
To prevent invalid requests from consuming internal processing power or database cycles, the Gateway performs preliminary validation:
* **UUIDv4 Enforcement:** The Gateway enforces strict Pydantic `UUID4` formatting checks on incoming payloads (such as the `player_id` parameter on scores submission).
* If validation fails, the Gateway intercepts the transaction and immediately returns a `422 Unprocessable Entity` response, matching the standardized API error contract.

### 3. Circuit Breaking and Resilience
The Gateway monitors communication with downstream services. If a non-critical internal service (such as the AI Engine) is offline or times out, the circuit breaker pattern prevents the cascading failure of client-facing endpoints:
* **Gateway Timeouts:** Downstream requests are bounded by a strict timeout (typically 3 to 4 seconds).
* **Graceful Degradation:** If the Leaderboard Engine is unreachable, the Gateway captures the connection error and responds with an HTTP 503 Service Unavailable or HTTP 504 Gateway Timeout error containing a clean, structured JSON payload.

### 4. Dynamic Health Aggregation
The `/health` endpoint of the Gateway acts as an observational dashboard for the entire microservice cluster. Upon invocation, it pings the `/health` endpoints of all downstream services asynchronously using concurrent asyncio tasks and outputs a structured status map showing which engines are operational, degraded, or offline.

## Setup and Local Execution

To run this specific service independently on your host machine:

### 1. Configure Local Environment
Ensure you have a `.env` file in this directory mapping the target local engine locations:
```env
PLAYER_ENGINE_URL=http://127.0.0.1:8001
MATCH_ENGINE_URL=http://127.0.0.1:8002
LEADERBOARD_ENGINE_URL=http://127.0.0.1:8003
AI_ENGINE_URL=http://127.0.0.1:8004
```

### 2. Install Dependencies and Run
From this directory, run:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## API Documentation
FastAPI automatically generates interactive API documentation for the Gateway. Once the service is running, you can explore the available schemas, test requests, and read parameters by opening:
* Interactive Swagger UI: `http://127.0.0.1:8000/api/docs`
* ReDoc UI: `http://127.0.0.1:8000/api/redoc`