# AI Engine

The AI Engine is an isolated microservice that uses Large Language Models (LLMs) to generate dynamic, personalized game commentary. Operating on FastAPI and integrated with LangChain, the engine translates raw player and score data into thrilling, Esports-announcer-style hype commentary [1].

## Technical Specifications

* **Runtime:** Python 3.13
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Integration Library:** LangChain (via `langchain-ollama` integration package)
* **Underlying Model:** `gemma4:31b-cloud` (Running via Ollama on the host machine)
* **Default Port:** 8004 (Internal, hidden from public routing)

## Core Responsibilities

### 1. LangChain LLM Orchestration
The engine abstracts direct raw HTTP calls to the Ollama API by using the production-grade `OllamaLLM` wrapper from LangChain:
* **Host Communication:** The AI Engine (running either locally or inside Docker) points its client connection to the Ollama instance on Port 11434.
* **Model Configuration:** Temperature, max tokens, and system parameters are managed programmatically via the LangChain initializer.

### 2. Asynchronous Inference Execution
Because generating text from an LLM can be computationally expensive and introduce latency, the engine protects the FastAPI event loop:
* **Async Invocations:** The service invokes the LLM asynchronously using LangChain's native `ainvoke` method.
* **Loop Preservation:** This ensures that the single-threaded Python event loop is never blocked, allowing the service to continue parsing health checks and handling other incoming requests while waiting for the LLM token completion.

### 3. Defensive Error Fallbacks
If the host's Ollama instance is disconnected, or if the `gemma4:31b-cloud` model is busy or not loaded, the AI Engine prevents cascading failure:
* **Exception Handling:** It catches timeout, connection, and model exceptions.
* **Static Fallback:** Instead of throwing an HTTP 500 error, it returns a pre-formatted, high-quality static hype message (incorporating the player's name and score), ensuring the upstream Leaderboard Engine still receives a valid payload.

## Directory Structure

* `requirements.txt`: Python dependencies including FastAPI, Uvicorn, LangChain, and langchain-ollama.
* `.env`: Holds local configuration parameters, including the target host's Ollama address and the active model name.
* `app/main.py`: Contains FastAPI initialization, Pydantic settings loading, LangChain client execution, and health validation routes.

## Endpoints

### Internal Endpoint (Unexposed to Public)
* **`POST /internal/generate/hype`**
  * Payload: `{"username": "string", "high_score": integer}`
  * Returns: Standard success envelope with the dynamically generated hype message.

### Health Endpoint
* **`GET /health`**
  * Returns: Service operational state. It actively pings the local Ollama backend and reports whether the connection is `connected`, `unreachable`, or `disconnected`.

## Setup and Local Execution

To run this specific service independently on your host machine:

### 1. Configure Local Environment
Create a `.env` file in this directory to specify your target local Ollama parameters:
```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4:31b-cloud
```

### 2. Prepare Your Model
Ensure your local host machine has the Ollama engine running, and you have pulled the model:
```bash
ollama pull gemma4:31b-cloud
```

### 3. Install Dependencies
Ensure you are in this folder and execute:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Launch Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8004
```