# Nexus Gaming Leaderboard System

Nexus is a scalable, Service-Oriented Architecture (SOA) backend designed to process high-throughput gaming scores and generate real-time global leaderboards. The system features a decoupled multi-language ecosystem and integrates a local Large Language Model (LLM) using LangChain and Ollama to dynamically generate personalized player feedback.

## System Architecture

The backend is decoupled into five independent, isolated engines communicating via internal HTTP REST APIs. All client-facing external traffic is routed through a single API Gateway which manages traffic, enforces UUIDv4 schemas, and acts as an asynchronous circuit breaker.

For technical deep-dives on individual components, refer to their respective directories:

* **[API Gateway Engine](services/api_gateway_engine/README.md) (`services/api_gateway_engine`):** Python and FastAPI. Serves as the single, public-facing gateway and circuit breaker.
* **[Player Engine](services/player_engine/README.md) (`services/player_engine`):** Python and Django. Manages player accounts, persistent profiles, and identities.
* **[Match Engine](services/match_engine/README.md) (`services/match_engine`):** Node.js and Express running on Bun. Specialized for high-throughput score logging.
* **[Leaderboard Engine](services/leaderboard_engine/README.md) (`services/leaderboard_engine`):** Python and Flask. Stateless business orchestrator that performs soft joins across services.
* **[AI Engine](services/ai_engine/README.md) (`services/ai_engine`):** Python and FastAPI. Integrates with Ollama via LangChain to generate dynamic Esports-commentary hype messages.

## Prerequisites

Ensure the following runtimes and tools are installed on your host system:

* **Docker and Docker Compose:** For containerized orchestration.
* **Bun:** Required as the package manager and runtime for Node.js services.
* **Python 3.13:** Required for local execution of the gateway, player, leaderboard, and AI engines.
* **Ollama:** Installed locally on the host machine running the gemma4:31b-cloud model.

## Local Host Development Setup

Running the microservices directly on your host machine allows for rapid debugging and hot-reloading. Since local environments may route internal calls through global system proxies or VPN loops (causing WinError 10061 connection refusals), the internal HTTP clients are configured with proxy bypass settings.

### 1. Configure the Environment Files
Create a `.env` file in the directories of the engines listed below to map the local ports:

* **services/api_gateway_engine/.env**
  ```env
  PLAYER_ENGINE_URL=http://127.0.0.1:8001
  MATCH_ENGINE_URL=http://127.0.0.1:8002
  LEADERBOARD_ENGINE_URL=http://127.0.0.1:8003
  AI_ENGINE_URL=http://127.0.0.1:8004
  ```

* **services/leaderboard_engine/.env**
  ```env
  PLAYER_ENGINE_URL=http://127.0.0.1:8001
  MATCH_ENGINE_URL=http://127.0.0.1:8002
  AI_ENGINE_URL=http://127.0.0.1:8004
  ```

* **services/ai_engine/.env**
  ```env
  OLLAMA_BASE_URL=http://127.0.0.1:11434
  OLLAMA_MODEL=gemma4:31b-cloud
  ```

### 2. Startup Commands
Launch each service in a separate terminal window from the root of the repository:

* **Terminal 1 (API Gateway - Port 8000):**
  ```bash
  cd services/api_gateway_engine
  python -m venv venv
  source venv/bin/activate  # On Windows use: venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```

* **Terminal 2 (Player Engine - Port 8001):**
  ```bash
  cd services/player_engine
  python -m venv venv
  source venv/bin/activate  # On Windows use: venv\Scripts\activate
  pip install -r requirements.txt
  python manage.py makemigrations players
  python manage.py migrate
  python manage.py runserver 8001
  ```

* **Terminal 3 (Match Engine - Port 8002):**
  ```bash
  cd services/match_engine
  bun install
  bun run src/index.js
  ```

* **Terminal 4 (Leaderboard Engine - Port 8003):**
  ```bash
  cd services/leaderboard_engine
  python -m venv venv
  source venv/bin/activate  # On Windows use: venv\Scripts\activate
  pip install -r requirements.txt
  python app.py
  ```

* **Terminal 5 (AI Engine - Port 8004):**
  ```bash
  cd services/ai_engine
  python -m venv venv
  source venv/bin/activate  # On Windows use: venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8004
  ```

Once all terminals are active, verify the routing health check at `http://127.0.0.1:8000/health`.

## Containerized Deployment (Docker)

To run the complete network inside isolated Docker containers, we utilize RFC 1034/1035 compliant hostnames (avoiding underscores) to satisfy Django host validation requirements.

1. Ensure Ollama is running on your host machine (outside Docker) on port 11434.
2. From the root directory of the repository, execute:
   ```bash
   docker compose up -d --build
   ```
3. Docker Compose will automatically build the images, create persistent volumes for the SQLite databases, apply Django database migrations on startup, and bridge the AI Engine container back to your host's Ollama instance.
4. Access the API Gateway at `http://localhost:8000/api/v1/` and verify the status at `http://localhost:8000/health`.

## API Validation and Testing (Postman)

The system is delivered with an automated Postman collection that handles registration, dynamic player UUID extraction, score generation, and leaderboard retrieval.

You can interact with the API endpoints using either of the following methods:

* **Local Collection File:** Import the `Nexus_Leaderboard.postman_collection.json` file located in the root directory of this repository into your Postman Workspace.
* **Postman Web Workspace:** Access the public web collection directly via the [Nexus Gaming Leaderboard System Postman Collection](https://www.postman.com/ronnex-soft-team-01/nexus-gaming-leaderboard-system).

## Continuous Integration (CI/CD Workflows)

Automated quality control checks are configured via GitHub Actions in the `.github/workflows/` directory. These pipelines run on pull requests and commits to the branch to ensure codebase stability:

* **Linting and Formatting:** Enforces Python (`black`, `flake8`) and Node.js (`bun x eslint`) code styles.
* **Automated Testing:** Runs `pytest` suites on the Python microservices and `bun test` on the Match Engine.
* **Build Verification:** Ensures all service Dockerfiles build successfully without compilation or caching conflicts.

## Architecture Documentation Directory

For complete documentation on the database strategy, requirements, and deployment protocols, refer to the `Docs/` directory:

* [Product Requirements Document (PRD)](./Docs/PRD.md)
* [Product Engineering Document (PED)](./Docs/PED.md)
* [API Response Contracts & Response Guidelines](./Docs/API_CONTRACTS.md)
* [Database Schema & Multi-DB Data Flow](./Docs/SCHEMA.md)
* [Testing Strategy](./Docs/TESTING.md)
* [Deployment Guide](./Docs/DEPLOYMENT.md)
