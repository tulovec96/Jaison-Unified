# Deployment Guide

This document explains basic deployment options for Voxelle.

## 1. Docker (recommended)

Build and run locally using Docker and docker-compose:

```bash
# Build images and run in background
docker-compose up --build -d

# View logs
docker-compose logs -f jaison

# Stop
docker-compose down
```

Notes:
- `docker-compose.yml` exposes ports `7272` (REST) and `7273` (WebSocket).
- Mount your `models/` and `config.yaml` as volumes for persistence.

## 2. Run on a VM or Bare Metal

1. Install Python 3.12+, FFmpeg and system dependencies.
2. Create a virtual environment and install requirements:

```bash
python -m venv venv
source venv/bin/activate  # Windows use: .\venv\Scripts\activate
pip install -r requirements.txt
python manager.py core
```

## 3. CI/CD & Production

- Use the included GitHub Actions workflow to run linting and tests on PRs.
- For production, build a Docker image and push to your registry. Use orchestration (Docker Swarm / Kubernetes) for high-availability.

## 4. Environment & Secrets

Use environment variables for all secrets (do not commit `.env`). Example `.env` is provided as `.env-template`.

## 5. Healthchecks

Add container healthchecks in your orchestration to verify `http://localhost:7272/health`.

## 6. Monitoring & Logging

- Persist logs from `/app/logs` to the host or a centralized logging service.
- Configure Prometheus/Grafana if advanced metrics are needed.

## 7. Notes on GPU

- GPU support requires a base image with CUDA and compatible PyTorch builds. For GPU deployments, prepare a custom image (not the default `python:3.12-slim`) and install CUDA-compatible PyTorch wheels.

## 8. Rollback

Keep previous Docker images and tag releases. Use `docker-compose pull` & `docker-compose up -d` to roll forward/back.
