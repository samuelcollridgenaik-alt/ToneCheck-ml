# ToneCheck

ToneCheck is a full-stack toxicity detection app with a polished React interface and a real machine-learning backend.

It combines:

- a React + Vite frontend
- a FastAPI backend
- a Hugging Face toxicity model running server-side
- a Dockerized production setup for cloud deployment

## Features

- Analyze pasted social media comments for toxicity
- Show a clean toxic vs. non-toxic verdict with confidence
- Surface model-driven category scores
- Run locally as an ML project, not just a frontend mock
- Deploy as a single container with the frontend bundled into the backend service

## Project Structure

- [src/App.jsx](/Users/apple/Documents/New%20project/src/App.jsx): main React interface
- [src/lib/api.js](/Users/apple/Documents/New%20project/src/lib/api.js): frontend API client
- [backend/app.py](/Users/apple/Documents/New%20project/backend/app.py): FastAPI application
- [backend/model_service.py](/Users/apple/Documents/New%20project/backend/model_service.py): local toxicity model loading and inference
- [Dockerfile](/Users/apple/Documents/New%20project/Dockerfile): production image build
- [render.yaml](/Users/apple/Documents/New%20project/render.yaml): Render deployment blueprint

## Local Development

### Run the whole stack

```bash
./ml-dev.sh
```

This starts:

- backend: `http://localhost:8000`
- frontend: `http://localhost:5173`

### Run services separately

Backend:

```bash
./backend.sh
```

Frontend:

```bash
./dev.sh
```

### Build the frontend

```bash
./build.sh
```

## Production Deployment

The app is set up to deploy as a single web service:

1. the frontend is built with Vite
2. the built assets are copied into the production image
3. FastAPI serves both the UI and the `/api/*` routes
4. the ML model is preloaded during startup when enabled

Deployment details live here:

- [Deployment Guide](/Users/apple/Documents/New%20project/docs/DEPLOYMENT.md)

## Publish to GitHub

Git publishing and access handoff details live here:

- [GitHub Publishing Guide](/Users/apple/Documents/New%20project/docs/GITHUB-PUBLISHING.md)

## Environment Variables

- `TOXICITY_MODEL_NAME`
- `TOXICITY_THRESHOLD`
- `PRELOAD_MODEL_ON_STARTUP`
- `PORT`
- `WEB_CONCURRENCY`
- `HF_HOME`
- `HUGGINGFACE_HUB_CACHE`

## Notes

- The default local moderation model is `unitary/toxic-bert`.
- The Render deployment defaults now use `gravitee-io/bert-small-toxicity`, which is much smaller and better suited to memory-constrained deployments.
- The first model download is large, so persistent model cache storage matters in production.
- `WEB_CONCURRENCY` should usually stay at `1` for this setup, because each worker would load its own model copy.
- The local helper scripts are designed to work even if `npm` is not installed globally.
