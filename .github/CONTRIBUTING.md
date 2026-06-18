# Contributing to the Nexus Gaming Leaderboard System

Thank you for your interest in contributing to our project. To maintain system stability, clean microservice boundaries, and consistent code quality across languages, please review and adhere to the following guidelines.

## Branching Model

We operate on a standard branching model to protect production environments:

1. **`master`:** Represents production-ready code. No direct commits are allowed on `master`.
2. **`dev`:** Represents the active development branch. All feature branches should be created from `dev`.
3. **Feature Branches (`feature/name` or `bugfix/name`):** Created from `dev`. Once complete, submit a Pull Request targeting the `dev` branch.

## How to Contribute

### 1. Reporting Bugs or Requesting Features
* Before opening a new issue, search the active issue tracker to ensure it has not been reported yet.
* Use the automated bug report or feature request templates provided in the repository to submit clear diagnostics, terminal trace logs, and context.

### 2. Making Changes
* Ensure your changes are strictly scoped to the specific microservice engine you are targeting. Avoid cross-contaminating service configurations.
* Enforce local environment configurations using `.env` files rather than hardcoding port locations or hostnames.
* Keep internal dependencies clean and secure.

### 3. Code Style Standards
We enforce static analysis and linting checks in our continuous integration pipeline:
* **Python Services (Gateway, Player, Leaderboard, AI):** Format your code using `black` and check it using `ruff`.
* **Node.js/Bun Services (Match):** Enforce formatting checks via `eslint` or native Bun formatters.

### 4. Testing Requirements
Any code contribution must pass the test criteria before pull requests are approved:
* Run the service standalone on your host environment to verify local port routing.
* Run the containerized stack using `docker compose up -d --build` to verify system-level compatibility.
* Assert that the `/health` endpoint on the API Gateway reports `"gateway_status": "operational"`.

## Pull Request Process

1. Submit your pull request using the provided markdown Pull Request Template.
2. Ensure the GitHub Actions linting, unit-testing, and Docker build verification jobs pass successfully.
3. Once approved, your changes will be merged into `dev` and eventually staged into `master` during the next release cycle.