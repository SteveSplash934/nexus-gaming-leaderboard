# Player Engine

The Player Engine is a database-backed microservice dedicated to player identity and profile management within the Nexus system. It operates on a clean, isolated SQLite instance, handles registration database constraints, enforces username uniqueness, and provides internal profile resolution using globally unique identifiers (UUIDv4).

## Technical Specifications

* **Runtime:** Python 3.13
* **Framework:** Django 6 (configured as a lightweight, headless API service)
* **Database:** SQLite (`players.sqlite3`)
* **Default Port:** 8001 (Internal, hidden from public routing)

## Core Responsibilities

### 1. Identity Management and Persistence
The Player Engine acts as the source of truth for player accounts. It persists basic profile metadata and strictly enforces database constraints:
* **UUIDv4 Keys:** Every player account is assigned a globally unique `UUIDv4` primary key upon creation. This key is used throughout the entire Nexus network for cross-service soft links.
* **Username Constraints:** Usernames are restricted to a minimum length of 3 and a maximum length of 15 characters. The database enforces standard SQL `UNIQUE` constraints to prevent profile duplication.

### 2. Internal Profile Resolution ("Soft Joins")
Because other services (like the Match Engine) do not have access to the player profile database, the Player Engine exposes an internal endpoint to resolve player IDs:
* When the Leaderboard Engine aggregates standings, it queries the Player Engine via an internal HTTP GET request to fetch the corresponding username string for each player UUID.
* If a player is missing from the database, the caller handles the fallback gracefully, ensuring decoupled reliability.

### 3. Automated Schema Management
To simplify local development and deployment pipelines:
* The container is configured to automatically run `python manage.py migrate` on boot before starting the server. This ensures that the local SQLite schema is always structurally synchronized with the application code.

## Directory Structure

* `manage.py`: Django entry point.
* `player_engine/settings.py`: Minimalist configuration omitting HTML templates, static files, admin panels, and standard cookie middlewares to optimize performance.
* `players/models.py`: Defines the Player database model with UUID field mapping.
* `players/views.py`: Exposes registration, internal profile lookups, and system health endpoints.

## Endpoints

### External Endpoint (Routed via Gateway)
* **`POST /api/v1/players/register`**
  * Payload: `{"username": "string"}`
  * Returns: Standard success envelope containing the newly created Player `id` and `username`.

### Internal Endpoint (Unexposed to Public)
* **`GET /internal/players/<uuid:player_id>`**
  * Returns: Success envelope with matching player profile details, or a `404 Not Found` if the UUID is missing.

### Health Endpoint
* **`GET /health`**
  * Returns: Service operational state. Used by the API Gateway to monitor the health of this engine.

## Setup and Local Execution

To run this specific service independently on your host machine:

### 1. Install Dependencies
Ensure you are in this directory and execute:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Database Migrations
Before starting the server, prepare the local SQLite database file:
```bash
python manage.py makemigrations players
python manage.py migrate
```

### 3. Launch Development Server
```bash
python manage.py runserver 8001
```