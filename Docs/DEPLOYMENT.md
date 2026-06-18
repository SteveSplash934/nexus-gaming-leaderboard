# Infrastructure & Deployment Guide

This document outlines the deployment and configuration strategy for the Nexus architecture. To align with modern DevOps practices and ensure environment parity, the entire project is containerized.

## 1. Local Development Strategy

For local development and testing, all five engines can be spun up simultaneously using Docker Compose.

### Prerequisites

* Docker Desktop installed and running.
* Ollama installed locally with your preferred model pulled (e.g., `gemma4:31b-cloud` or `qwen3.5:397b-cloud`).

### Ollama Host Loopback Configuration (Windows)

By default, the Ollama application binds to `127.0.0.1`, and Windows Defender Firewall blocks incoming connections from virtual subnets (like the Docker bridge network). To allow the containerized `ai-engine` to communicate with the host's Ollama instance, execute the following steps:

1. **Configure Ollama Binding:**
   * Quit Ollama completely from your taskbar system tray.
   * Add a new System/User Environment Variable named `OLLAMA_HOST` with the value `0.0.0.0`.
   * Relaunch the Ollama application.

2. **Unblock Windows Defender Firewall:**
   Open PowerShell as an Administrator and execute the following command to allow inbound TCP traffic on port 11434 from the virtual network adapter:
   ```powershell
   New-NetFirewallRule -DisplayName "Allow Ollama Port 11434 from Docker" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
   ```

### Startup Procedure

1. Navigate to the root directory of the repository.
2. Execute the build command:
   ```bash
   docker compose up -d --build
   ```
3. The API Gateway will bind to `localhost:8000`. Internal services will run on ports `8001` through `8004` within the isolated `nexus_internal_network` bridge and do not need to be accessed directly by the host machine.

## 2. Production Deployment Strategy (VPS/Droplet)

For live deployment, we recommend provisioning a Linux Virtual Private Server (VPS) such as a DigitalOcean Droplet.

### Phase 1: Server Provisioning

1. Deploy a standard Linux Droplet (Ubuntu 24.04 LTS).
2. Install Docker Engine and Docker Compose.
3. Secure the server by configuring `UFW` (Uncomplicated Firewall) to block all ports except `22` (SSH), `80` (HTTP), and `443` (HTTPS).

### Phase 2: Application Deployment

1. Clone the repository to the production server.
2. Set up environment variables (e.g., database credentials, internal service URLs) in a `.env` file.
3. Run the orchestration command in detached mode:
   ```bash
   docker compose up -d
   ```

### Phase 3: Traffic Routing & Security (Cloudflare)

To protect the Gateway and manage DNS routing securely:

1. Map your domain (e.g., `api.nexusgaming.com`) to the Droplet's public IP address in the Cloudflare dashboard.
2. Enable the Cloudflare Proxy (Orange Cloud status) to handle SSL/TLS termination and provide DDoS mitigation.
3. Configure an Nginx reverse proxy on the Droplet to forward external traffic from ports `80`/`443` to the internal API Gateway container running on port `8000`.

*Note: All internal engines (`player_engine`, `match_engine`, `leaderboard_engine`, and `ai_engine`) must be configured to communicate only within the internal Docker network. They should never be directly exposed to the internet.*
