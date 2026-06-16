# Testing Strategy for SOA

**Project Name:** Nexus Gaming Leaderboard System

Testing a decoupled Service-Oriented Architecture (SOA) requires a multi-layered approach. Since services are isolated, we must ensure individual engines function correctly on their own and communicate seamlessly when integrated.

## 1. Unit Testing (Engine Level)

Each engine is responsible for testing its own isolated business logic and database interactions.

* **Player Engine (Python/Django):**
* **Tooling:** `pytest` and `pytest-django`.
* **Focus:** Validate user registration logic, ensure duplicate usernames are rejected, and verify that the engine correctly generates and returns a strictly formatted **UUIDv4** for new accounts.


* **Match Engine (Node.js/Express):**
* **Tooling:** `Jest` and `Supertest`.
* **Focus:** Validate the high-speed ingestion API. Ensure the system accepts valid JSON payloads and correctly validates that the incoming `player_id` is a valid **UUIDv4** before recording the score.


* **Leaderboard Engine (Python/Flask):**
* **Tooling:** `pytest` and `responses`.
* **Focus:** Test the in-memory data aggregation and sorting algorithms (the cross-service "soft join").



## 2. Mocking Cross-Service Calls

During unit development and CI/CD pipelines, services must not depend on other engines being live.

* When testing the Leaderboard Engine, use HTTP mocking libraries (like `responses` in Python) to intercept outward GET requests.
* Provide the test suite with mock JSON arrays mimicking the Match Engine and Player Engine outputs. This tests the aggregation logic without requiring actual network connections or live databases.

## 3. Integration & API Contract Testing

Integration tests run against the **API Gateway (FastAPI)** to ensure routing, data contracts, and failure handling work correctly.

* **Happy Path:** Verify that an external request to `/api/v1/players/register` correctly routes to the Player Engine and returns the expected JSON envelope and UUIDv4 payload.
* **Resilience / Circuit Breaking:** Simulate the AI Engine being offline. Assert that the Gateway catches the timeout and returns a 200 OK with the leaderboard data and a fallback hardcoded message, rather than cascading into a 500 Internal Server Error.