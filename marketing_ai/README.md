# AI Marketing Operating System

This directory represents the **Final Architecture Blueprint** implementation of the enterprise-grade AI SaaS Marketing System.

## Architecture Highlights

- **FastAPI Core**: Highly scalable async Python web framework using `app/main.py` entrypoint.
- **Multi-Tenant SaaS Foundation**: Enforced role-based limits (`can_create_company()`).
- **Connector Framework**: Abstract interface ready to scale across Meta, Google, TikTok pipelines.
- **Daily Intelligence Cycle**: 24H Background Celery Worker sequence (Metrics -> Engine -> Reasoner -> execution).
- **Automation Safety Layer**: Hard rule budget limits and confidence scoring (No LLM hallucinations trigger money burns).
- **Qdrant + Competitor Intelligence**: Document stores and embeddings mapped to SQLAlchemy.

## Quick Start (Docker Compose)

1. Provide valid keys in `.env` by copying the `.env.example`.
2. Ensure you have Docker and Docker Compose installed.
3. Boot the environment. This will spin up PostgreSQL, Redis, Qdrant, the API, and Celery worker.

```bash
docker-compose up -d --build
```

You can view the OpenAPI GUI swagger spec at <http://localhost:8000/docs> once running.
