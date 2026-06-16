# API Contracts & Design Document

**Project Name:** Nexus Gaming Leaderboard System

## Purpose

Define a consistent, predictable JSON response structure for API endpoints across all internal and external engines, covering success, data delivery, and error handling.

## Core Principles

1. HTTP status codes indicate success or failure.
2. JSON body provides details, messages, and data.
3. Response structure must be consistent across all endpoints.
4. Errors must be machine-readable and human-readable.
5. Never expose stack traces or internal implementation details.
6. **All Identifiers (IDs) MUST be strictly formatted as UUIDv4.**

---

## Standard Response Envelopes

### Success Response (With Data)

**HTTP Status Codes:** 200 OK, 201 Created

**Example: Fetching the Leaderboard (`GET /api/v1/leaderboard`)**
```json
{
    "success": true,
    "message": "Global leaderboard fetched successfully",
    "data": {
        "ranks": [
            {
                "player_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "username": "CyberNinja",
                "high_score": 15400
            }
        ],
        "ai_hype_message": "CyberNinja is dominating the grid with an untouchable score!"
    }
}
```

### Success Response (No Data)

**HTTP Status Codes:** 200 OK, 204 No Content

**Example: Submitting a Match Score (`POST /api/v1/scores`)**
```json
{
    "success": true,
    "message": "Match score recorded successfully"
}
```

### Error Response (Standard)

**HTTP Status Codes:** 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error

**Example: Player Not Found (`GET /api/v1/players/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d`)**
```json
{
    "success": false,
    "error": {
        "code": "PLAYER_NOT_FOUND",
        "message": "The requested player profile does not exist"
    }
}
```

### Validation Error Response

**HTTP Status Code:** 422 Unprocessable Entity

**Example: Invalid Registration Data (`POST /api/v1/players/register`)**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request data",
        "details": [
            {
                "field": "username",
                "message": "Username must be between 3 and 15 characters"
            }
        ]
    }
}
```

---

## Endpoint Specifications (API Gateway)

### 1. Register Player

* **URL:** `/api/v1/players/register`
* **Method:** `POST`
* **Payload:** `{ "username": "string" }`
* **Success Data:** `{ "id": "UUIDv4", "username": "string" }`

### 2. Submit Match Score

* **URL:** `/api/v1/scores`
* **Method:** `POST`
* **Payload:** `{ "player_id": "UUIDv4", "score": integer }`
* **Success Data:** *None*

### 3. Get Leaderboard

* **URL:** `/api/v1/leaderboard`
* **Method:** `GET`
* **Success Data:** Array of ranked player objects and a dynamic AI generated string.