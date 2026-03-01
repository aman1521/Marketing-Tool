# 🌌 Atlas System (Gas Matter)

The foundational data layer of the AI Growth Operating System. Atlas serves as the single source of truth for:

1. Multi-platform marketing data ingestion
2. Automatic feature engineering
3. Anonymized global benchmarking
4. Hybrid-ML structured Event Memory Tracking

## 🏗 Architecture Layers

### 🧱 1. Atlas Collect

Orchestrates idempotent REST/GraphQL sync loops against advertising platforms. Uses robust background `celery` tasks to scale.
*Connectors*: Meta, Google Ads, TikTok.

### 📊 2. Atlas Signals

Translates abstract raw datasets (`impressions`, `spend`) into predictive intelligence vectors (`fatigue_score`, `scaling_confidence_score`). Serves as the backbone feature engine for Captain and Genesis downstream.

### 🌍 3. Atlas Benchmarks

Processes continuous background cluster analysis assigning anonymized campaigns into industry aggregations, granting zero-day ad operators global standard percentiles for targeting.

### 🗂 4. Atlas Memory

Persists AI system predictions asynchronously, providing exact inference payloads to validate Data Drift and optimize MLOps loops. Uses Online/Offline Feature Store separation logic.

## 🚀 Running the Atlas System

### Using Docker (Preferred)

```bash
docker-compose up -d --build
```

### Manual Setup

1. Create PostgreSQL and Redis instances.
2. Initialize virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set Environment variables mapping `.env.template`.
2. Run FastAPI:

```bash
uvicorn backend.services.atlas.main:app --reload --port 8003
```

5. Run Celery Worker & Beat locally:

```bash
celery -A backend.services.atlas.celery_app worker --loglevel=info
celery -A backend.services.atlas.celery_app beat --loglevel=info
```
