# Match Engine

The Match Engine is a specialized, high-throughput microservice designed to ingest, log, and query raw game match scores. It operates on Bun's fast JavaScript runtime, runs an Express server, and utilizes Bun's native, low-latency database driver (`bun:sqlite`) to execute write operations on an isolated SQLite database.

## Technical Specifications

* **Runtime:** Bun (Node.js compatibility layer)
* **Framework:** Express
* **Database Driver:** Bun's native SQLite driver (`bun:sqlite`)
* **Database File:** `matches.sqlite3`
* **Default Port:** 8002 (Internal, hidden from public routing)

## Core Responsibilities

### 1. High-Throughput Score Ingestion
The primary responsibility of the Match Engine is handling write-heavy score-logging traffic:
* **Asynchronous Ingestion:** Scores submitted by clients are quickly written to the database with a system-generated UUIDv4 and timestamp, ensuring minimal connection hold times.
* **Database Optimization:** A performance index is automatically maintained on the `player_id` column inside SQLite to prevent slow sequential table scans as millions of matches are logged.

### 2. Leaderboard Standings Queries
The Match Engine exposes a read-optimized internal endpoint used during leaderboard aggregation:
* **Group and Sort queries:** It groups the raw logs by `player_id`, extracts the absolute maximum (`MAX`) score for each unique player, and sorts the results in descending order.
* **Query Limiting:** Standings are limited to the top 10 records to keep network payload transfer and in-memory sorting latency minimal.

### 3. Decoupled Data Design ("Soft Links")
Following Service-Oriented Architecture (SOA) principles, this engine does not share database tables or join SQL structures with the Player Engine. It treats the incoming `player_id` purely as an unvalidated UUID string ("soft link"). The responsibility of validating the existence of that user or resolving their username is offloaded to other engines.

## Directory Structure

* `package.json`: Dependency mapping using standard unpinned packages (e.g. Express, UUID, CORS).
* `src/db.js`: Database initialization using `bun:sqlite`, schema creations, and index generation.
* `src/index.js`: Express server initialization, routing, payload parsing, and logging logic.

## Endpoints

### External Endpoint (Routed via Gateway)
* **`POST /api/v1/scores`**
  * Payload: `{"player_id": "UUIDv4", "score": integer}`
  * Returns: Standard success envelope confirming the score has been persisted.

### Internal Endpoint (Unexposed to Public)
* **`GET /internal/scores/top`**
  * Returns: Standard success envelope containing an array of the top 10 maximum scores, mapped to their player UUIDs.

### Health Endpoint
* **`GET /health`**
  * Returns: Service operational state. Used by the API Gateway to monitor the health of this engine.

## Setup and Local Execution

To run this specific service independently on your host machine:

### 1. Install Dependencies
Ensure you have Bun installed on your machine. From this folder, run:
```bash
bun install
```

### 2. Start Development Server
Launch the server in watch mode (updates automatically on code changes):
```bash
bun dev
```

### 3. Start Production Server
Launch the server in standard execution mode:
```bash
bun run src/index.js
```