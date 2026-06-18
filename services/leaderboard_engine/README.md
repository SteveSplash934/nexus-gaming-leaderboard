# Leaderboard Engine

The Leaderboard Engine is a stateless data aggregator that orchestrates the core business logic of the Nexus Gaming system. It compiles raw score standings, resolves player usernames across network boundaries, and interfaces with the AI Engine to construct a complete, unified leaderboard payload for the API Gateway.

## Technical Specifications

* **Runtime:** Python 3.13
* **Framework:** Flask
* **Server:** Gunicorn (production) or Flask WSGI (development)
* **Default Port:** 8003 (Internal, hidden from public routing)

## Core Responsibilities

### 1. Network-Based Data Aggregation (Soft Joins)
Since databases are isolated per service under SOA principles, standard database JOIN operations are impossible. The Leaderboard Engine performs this data synthesis over the network:
* **Standings Collection:** It queries the Match Engine over HTTP to fetch the top 10 maximum scores and their associated player UUIDv4s.
* **Username Resolution:** For each score, it makes a subsequent, isolated HTTP GET request to the Player Engine to fetch the matching username string.
* **In-Memory Synthesis:** It maps the scores and usernames together in-memory, constructing a unified ranked array.

### 2. Defensive Circuit Breaking (AI Fallback)
The engine queries the AI Engine to generate dynamic commentary based on the top standing. If the AI Engine is offline or times out, the Leaderboard Engine acts as a circuit breaker:
* **Exception Interception:** It catches the network connection error or timeout.
* **Graceful Degradation:** Instead of failing the client request (500 Server Error), it sets a friendly, hardcoded fallback string in the JSON payload and successfully returns the standings.

### 3. Proxy Bypass (Windows Loopback Support)
To prevent global system proxies, VPNs, or network filters on Windows environments from intercepting internal localhost requests (which triggers `WinError 10061` connection refusals), the engine's network client is configured with custom parameters:
* **Session Trust Isolation:** It initializes a dedicated `requests.Session` with `trust_env = False` to bypass local operating system loopback proxy rules.

## Directory Structure

* `requirements.txt`: Stateless Python dependencies, including Flask, Requests, Gunicorn, and python-dotenv.
* `.env`: Stores local port mapping variables for independent host testing.
* `app.py`: Contains Flask routing, network aggregation loops, proxy bypass sessions, and health check handlers.

## Endpoints

### External Endpoint (Routed via Gateway)
* **`GET /api/v1/leaderboard`**
  * Returns: Standard success envelope containing a ranked array of high scores with mapped usernames, alongside a dynamic AI hype message.

### Health Endpoint
* **`GET /health`**
  * Returns: Service operational state. Used by the API Gateway to monitor the health of this engine.

## Setup and Local Execution

To run this specific service independently on your host machine:

### 1. Configure Local Environment
Ensure you have a `.env` file in this directory to map local port paths:
```env
PLAYER_ENGINE_URL=http://127.0.0.1:8001
MATCH_ENGINE_URL=http://127.0.0.1:8002
AI_ENGINE_URL=http://127.0.0.1:8004
```

### 2. Install Dependencies
Ensure you are in this folder and execute:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Launch Development Server
```bash
python app.py
```