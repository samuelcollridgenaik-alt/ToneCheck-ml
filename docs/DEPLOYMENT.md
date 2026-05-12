# Deployment Guide

## Recommended Production Setup

The cleanest deployment path for this app is a single Docker web service on Render.

Why this setup fits:

- the React frontend is static after build
- the FastAPI backend serves both UI and API traffic
- the model should live close to the backend process
- Hugging Face model weights benefit from persistent disk caching

## Memory Note For Render

If you see an error like:

```text
Ran out of memory (used over 512MB) while running your code
```

that usually means the service is on Render's `starter` instance type. Render's instance type docs list `starter` as `512 MB RAM` and `standard` as `2 GB RAM` for web services. This app is ML-backed, so `512 MB` is usually too tight for a Python runtime plus model inference.  
Source:

- [Render instance types](https://render.com/docs/one-off-jobs)

To reduce memory pressure, the production config now uses a much smaller production model by default:

The current default production model is:

- `gravitee-io/bert-small-toxicity`

Its model card says it is a multilingual toxicity classifier with `not-toxic` / `toxic` outputs and lists the model size as `28.8M params`, which is far smaller than the earlier BERT-scale options.  
Sources:

- [gravitee-io/bert-small-toxicity model card](https://huggingface.co/gravitee-io/bert-small-toxicity)

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
- `plan: starter`

If Render still reports memory pressure after switching to the smaller model, then the next step is to move the service to `standard` for `2 GB RAM`.

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
