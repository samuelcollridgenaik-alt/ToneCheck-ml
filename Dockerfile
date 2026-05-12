FROM node:20-bookworm-slim AS frontend-builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.js ./
COPY src ./src

RUN npm run build


FROM python:3.11-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    PRELOAD_MODEL_ON_STARTUP=1 \
    TOXICITY_MODEL_NAME=gravitee-io/bert-small-toxicity \
    TOXICITY_THRESHOLD=0.50 \
    HF_HOME=/data/huggingface \
    HUGGINGFACE_HUB_CACHE=/data/huggingface/hub

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --upgrade pip && pip install -r ./backend/requirements.txt

COPY backend ./backend
COPY start.sh ./start.sh
COPY --from=frontend-builder /app/dist ./dist

RUN chmod +x ./start.sh && mkdir -p /data/huggingface

EXPOSE 8000

CMD ["./start.sh"]
