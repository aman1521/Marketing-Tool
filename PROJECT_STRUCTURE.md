# Project Structure Overview

## Directory Structure

```
Marketing tool/
├── backend/
│   ├── api_gateway/                    # Central API entry point
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application with routing
│   │   └── Dockerfile
│   │
│   ├── auth_service/                   # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── main.py                    # OAuth2 + JWT token handling
│   │   └── Dockerfile
│   │
│   ├── business_service/               # Business logic & constraints
│   │   ├── __init__.py
│   │   ├── main.py                    # Business rule validation
│   │   └── Dockerfile
│   │
│   ├── platform_integration/           # Advertising platform connectors
│   │   ├── __init__.py
│   │   ├── main.py                    # Meta, Google, TikTok, LinkedIn APIs
│   │   └── Dockerfile
│   │
│   ├── attribution_engine/             # Multi-touch attribution
│   │   ├── __init__.py
│   │   ├── main.py                    # Conversion tracking & mapping
│   │   └── Dockerfile
│   │
│   ├── ml_service/                     # ML models & inference
│   │   ├── __init__.py
│   │   ├── main.py                    # 4 predictive models
│   │   └── Dockerfile
│   │
│   ├── intelligence_orchestrator/      # ML output orchestration
│   │   ├── __init__.py
│   │   ├── main.py                    # Merge & constraint application
│   │   └── Dockerfile
│   │
│   ├── decision_engine/                # Deterministic rules
│   │   ├── __init__.py
│   │   ├── main.py                    # Decision logic & scoring
│   │   └── Dockerfile
│   │
│   └── execution_engine/               # Campaign automation
│       ├── __init__.py
│       ├── main.py                    # Execute recommendations
│       └── Dockerfile
│
├── frontend/
│   ├── src/                           # React/Vue components
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
│
├── shared/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── shared_models.py           # Pydantic request/response models
│   └── schemas/
│       ├── __init__.py
│       └── database_schemas.py         # SQLAlchemy models (WIP)
│
├── database/
│   ├── schema.sql                     # PostgreSQL schema definition
│   ├── migrations/                     # Alembic migrations (WIP)
│   └── seeds/                          # Sample data (WIP)
│
├── infrastructure/
│   ├── kubernetes/                    # K8s deployment configs
│   ├── docker/                        # Docker images
│   └── terraform/                     # Infrastructure as Code (WIP)
│
├── docs/
│   ├── README.md
│   ├── architecture.md                # System architecture
│   ├── api.md                         # API documentation
│   └── deployment.md                  # Deployment guide (WIP)
│
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Local development setup
├── requirements.txt                   # Python dependencies
├── ROADMAP.md                         # Implementation roadmap
├── QUICKSTART.md                      # Quick start guide
└── README.md                          # Project overview
```

## Key Files Description

### Configuration
- **`.env.example`** - Template for all environment variables
- **`requirements.txt`** - Python package dependencies
- **`docker-compose.yml`** - Local development with all services + databases

### Database
- **`database/schema.sql`** - Complete PostgreSQL schema with 16 tables
- Includes: Users, Businesses, Platforms, Campaigns, Creatives, Metrics, ML Logs, Audit Logs

### Backend Services (8 Microservices)

| Service | Port | Purpose |
|---------|------|---------|
| API Gateway | 8000 | Request routing, auth, rate limiting |
| Auth Service | 8001 | JWT tokens, OAuth2, session mgmt |
| Business Service | 8002 | Business rules, constraint validation |
| Platform Integration | 8003 | API connectors for 6 ad platforms |
| Attribution Engine | 8005 | Multi-touch attribution, revenue mapping |
| ML Service | 8004 | 4 predictive models, feature store |
| Intelligence Orchestrator | 8006 | Merge ML outputs + apply constraints |
| Decision Engine | 8007 | Deterministic rules for decisions |
| Execution Engine | 8008 | Execute changes, auto/manual modes |

### Shared Code
- **`shared/models/shared_models.py`** - Pydantic models for all API requests/responses
- Includes: User, Business, Campaign, Creative, Metrics, ML Prediction models

### Documentation
- **`ROADMAP.md`** - 8-phase implementation plan (30 weeks)
- **`QUICKSTART.md`** - Setup and first steps guide
- **`README.md`** - Project overview and features

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL (relational), Redis (cache)
- **Queue**: RabbitMQ (async tasks)
- **ML**: scikit-learn, XGBoost, PyTorch
- **LLM**: OpenAI/Anthropic

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Kubernetes (for production)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## Database Schema Overview

### Core Tables
1. **users** - User accounts with roles
2. **businesses** - Business profiles with constraints
3. **user_business_assignments** - Multi-tenant relationships
4. **platform_accounts** - OAuth tokens for 6 ad platforms

### Campaign Management
5. **campaigns** - Campaign definitions
6. **ad_sets** - Ad set details
7. **creatives** - Creative assets with scores
8. **campaign_creatives** - Many-to-many relationship

### Data & Analytics
9. **performance_metrics** - Time-series campaign metrics
10. **audience_clusters** - ML-generated audience segments
11. **ml_predictions** - Prediction logs with accuracy
12. **raw_data_logs** - Original API responses

### Operations
13. **budget_allocations** - Recommended budget changes
14. **strategy_outputs** - LLM-generated strategies
15. **audit_logs** - Complete action audit trail
16. **api_errors** - API error tracking

## API Structure

All endpoints follow REST conventions:

```
GET    /health                          - Service health check
POST   /api/v1/auth/login              - Login
POST   /api/v1/auth/refresh            - Refresh token
GET    /api/v1/businesses/{id}         - Get business
POST   /api/v1/platforms/{name}/sync   - Sync platform data
POST   /api/v1/ml/predict              - Get ML predictions
POST   /api/v1/decisions/evaluate      - Evaluate decisions
POST   /api/v1/execution/auto-mode     - Execute changes
```

## Service Dependencies

```
Client/Frontend (React)
    ↓
API Gateway (8000)
    ├→ Auth Service (8001)
    ├→ Business Service (8002)
    ├→ Platform Integration (8003)
    ├→ ML Service (8004)
    ├→ Attribution Engine (8005)
    ├→ Intelligence Orchestrator (8006)
    ├→ Decision Engine (8007)
    └→ Execution Engine (8008)
    
All services connect to:
    - PostgreSQL (Database)
    - Redis (Cache)
    - RabbitMQ (Message Queue)
```

## Development Workflow

1. **Local Development**: Use docker-compose for full stack
2. **Code Changes**: Hot-reload enabled in containers
3. **Testing**: Unit tests with pytest
4. **Deployment**: Docker → Kubernetes (production)

## Next Steps

1. ✅ Project structure created
2. ✅ Database schema designed
3. ✅ API models defined
4. ▶️ Implement Phase 1 services (in progress)
5. ▶️ Set up data pipelines (queued)
6. ▶️ Train ML models (queued)
7. ▶️ Build frontend (queued)
8. ▶️ Deploy to production (queued)

## File Statistics

- **Python Files**: 9 backend services + shared models
- **SQL**: Complete schema with 16 tables
- **YAML**: docker-compose + Kubernetes configs
- **Documentation**: 5 markdown files
- **Total Lines of Code**: ~2,000+ (Phase 1)

---

See [ROADMAP.md](ROADMAP.md) for detailed implementation phases.
