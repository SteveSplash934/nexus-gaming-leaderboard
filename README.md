# Nexus Gaming Leaderboard System

Nexus is a scalable, Service-Oriented Architecture (SOA) backend designed to process high-throughput gaming scores and generate real-time global leaderboards. It features a decoupled multi-language ecosystem and integrates a local AI LLM to dynamically generate personalized player feedback.

## 🏗 Architecture Overview

The system is separated into five independent engines, demonstrating robust microservice boundaries.

**For a full technical breakdown, local setup instructions, and specific endpoints of each engine, please refer to their dedicated documentation:**

* 🚦 **[API Gateway Engine (`api_gateway_engine`)](./services/api_gateway_engine/README.md):** Python/FastAPI - Central traffic routing and circuit breaking.
* 👤 **[Player Engine (`player_engine`)](./services/player_engine/README.md):** Python/Django - Profile and identity management using UUIDv4.
* 🎮 **[Match Engine (`match_engine`)](./services/match_engine/README.md):** Node.js/Express (via Bun) - High-speed match logging.
* 🏆 **[Leaderboard Engine (`leaderboard_engine`)](./services/leaderboard_engine/README.md):** Python/Flask - Cross-service data compilation and sorting.
* 🧠 **[AI Engine (`ai_engine`)](./services/ai_engine/README.md):** Python/FastAPI + Ollama - LLM text generation for dynamic hype messages.

## 🛠 Prerequisites

Before running the Nexus ecosystem, ensure you have the following installed:

* **Docker & Docker Compose:** For running the containerized infrastructure.
* **Bun:** We strictly use Bun (`bun run`, `bun install`) as the JavaScript runtime and package manager for the Node.js services. **Do not use npm at the moment because this project haven't been testing on npm so things might break**
* **Postman:** Required for API contract testing and endpoint validation.
* **Ollama:** Must be installed locally and running the `llama3` model for the AI Engine to function.

## 🚀 Quick Start

1. Clone the repository to your local machine.
2. Ensure Docker Desktop and your local Ollama instance are running.
3. Boot the entire SOA cluster in detached mode:
`docker-compose up -d --build`
4. The API Gateway is now accessible at `http://localhost:8000/api/v1/`.

## 🧪 API Testing with Postman

All external and internal API interactions are tested using **Postman**.

1. Open Postman.
2. Import the `Nexus_Workspace.postman_collection.json` file (located in the root directory).
3. Select the `Local_Docker` environment in Postman.
4. Run the pre-configured requests to register a player, submit scores, and fetch the leaderboard.

## ⚙️ CI/CD Workflows (GitHub Actions)

This repository enforces automated quality checks via GitHub Actions located in the `.github/workflows/` directory. The pipelines automatically trigger on pull requests to the `main` branch and handle:

* **Linting & Formatting:** Validating Python (`black`, `flake8`) and Node.js (`bun x eslint`) codebases.
* **Automated Testing:** Running `pytest` for Python engines and `bun test` for the Match Engine.
* **Docker Build Verification:** Ensuring all 5 engine `Dockerfile`s build successfully without failing.

## 📖 Global Documentation Directory

For overarching system design and deployment strategies, refer to the global `Docs/` folder:

* [Product Requirements (PRD)](./Docs/PRD.md)
* [Engineering Design (PED)](./Docs/PED.md)
* [API Contracts & Response Guidelines](./Docs/API_CONTRACTS.md)
* [Database Schema & Data Flow](./Docs/SCHEMA.md)
* [Testing Strategy](./Docs/TESTING.md)
* [Deployment Guide](./Docs/DEPLOYMENT.md)