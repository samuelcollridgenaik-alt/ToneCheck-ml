# Deployment Guide

## Recommended Production Setup

The cleanest deployment path for this app is a single Docker web service on Render.

Why this setup fits:

- the React frontend is static after build
- the FastAPI backend serves both UI and API traffic
- the model should live close to the backend process
- Hugging Face model weights benefit from persistent disk caching

## What Ships in Production

The production image:

1. installs Node dependencies
2. builds the Vite frontend into `dist`
3. installs Python dependencies
4. runs FastAPI with Uvicorn
5. serves the frontend from the backend process

Relevant files:

- [Dockerfile](/Users/apple/Documents/New%20project/Dockerfile)
- [start.sh](/Users/apple/Documents/New%20project/start.sh)
- [render.yaml](/Users/apple/Documents/New%20project/render.yaml)

## Render Deployment

This repo already includes a Render blueprint.

Important production settings:

- `healthCheckPath: /api/health`
- `PRELOAD_MODEL_ON_STARTUP=1`
- persistent disk mounted at `/data`
- Hugging Face cache rooted at `/data/huggingface`
- `WEB_CONCURRENCY=1`

### Render Deploy Flow

1. Push the repo to GitHub.
2. In Render, create a new Blueprint or Web Service from that repo.
3. Let Render read `render.yaml`.
4. Start the deploy.
5. Wait for the first startup to finish downloading or restoring the model cache.

## Manual Docker Deployment

Build locally:

```bash
docker build -t tonecheck-ml .
```

Run locally:

```bash
docker run -p 8000:8000 tonecheck-ml
```

Open:

```text
http://localhost:8000
```

## Deployment Considerations

### Cold start

The first container boot is slower because the model weights may need to be downloaded.

### Persistent storage

Without persistent storage, the model cache is re-downloaded on fresh instances.

### Worker count

Keep `WEB_CONCURRENCY=1` unless you intentionally want multiple model copies in memory.

### Health checks

Because the app can preload the model, `/api/health` is a more meaningful readiness check than a plain root-path ping.

## Alternative Platforms

You can also run this app on:

- Railway
- Fly.io
- any VM or container host that supports Docker

The same container strategy still applies.
