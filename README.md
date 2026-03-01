# AI Growth Operating System

A unified marketing intelligence infrastructure that combines machine learning predictions, deterministic decision logic, and LLM-based strategy generation to autonomously optimize cross-platform advertising campaigns.

## 🚀 Project Overview

**AI Growth Operating System (AIOS)** is an enterprise-grade marketing automation platform designed for agencies and businesses to:

- **Unify** data from multiple advertising platforms (Meta, Google, TikTok, LinkedIn, Shopify, WooCommerce)
- **Predict** campaign performance using advanced ML models
- **Decide** optimal budget allocations and actions using deterministic logic
- **Generate** data-driven marketing strategies using LLMs
- **Execute** changes autonomously or manually with full transparency
- **Learn** continuously from results to improve predictions

## 📊 Key Features

✅ **Multi-Platform Integration** - Connect to 6+ advertising platforms  
✅ **Real-Time Data Pipeline** - Live sync of campaign, audience, and creative data  
✅ **ML-Powered Predictions** - 4 specialized models for audience, creatives, ROAS, and budget optimization  
✅ **Intelligent Decision Engine** - Deterministic rules blending ML outputs with business constraints  
✅ **LLM Strategy Generation** - Auto-generated content calendars, ad copy, and strategic recommendations  
✅ **Autonomous Execution** - Manual or auto mode with risk management safeguards  
✅ **Comprehensive Analytics** - Dashboards, cohort analysis, and prediction accuracy tracking  
✅ **Enterprise Security** - OAuth2, JWT tokens, GDPR compliance, multi-tenant isolation  

## 🏗️ Architecture

### Monorepo Structure

```
├── backend/
│   ├── api_gateway/              # Central request router
│   ├── auth_service/             # OAuth2 + JWT authentication
│   ├── business_service/         # Business logic & constraints
│   ├── platform_integration/     # API connectors for ad platforms
│   ├── attribution_engine/       # Multi-touch attribution
│   ├── ml_service/              # Model training & inference
│   ├── intelligence_orchestrator/ # ML output merger
│   ├── decision_engine/         # Deterministic rules engine
│   └── execution_engine/        # Campaign updates & automation
├── frontend/                     # React/Vue dashboard
├── database/                     # PostgreSQL schema & migrations
├── shared/                       # Shared models & utilities
├── infrastructure/               # K8s, Docker, CI/CD configs
├── docs/                         # Architecture & API docs
└── ROADMAP.md                   # 8-phase implementation plan
```

### System Flow

```
Data Layer (PostgreSQL, Redis)
    ↓
Data Normalization & Attribution
    ↓
ML Models (Audience, Creative, ROAS, Budget)
    ↓
Intelligence Orchestrator (merge outputs)
    ↓
Decision Engine (deterministic logic)
    ↓
LLM Strategy Layer (generate recommendations)
    ↓
Execution Engine (apply changes)
    ↓
Feedback Loop (weekly cycle, monthly retraining)
```

## 📋 Implementation Roadmap

### Phase 1: Foundation & Core Infrastructure (Weeks 1-4)
- API Gateway, Authentication, Database setup
- **Status**: ✅ IN PROGRESS

### Phase 2: Core Services & Data Integration (Weeks 5-8)
- Business Service, Platform Connectors, Attribution Engine
- **Status**: 🔄 QUEUED

### Phase 3: Machine Learning Foundation (Weeks 9-14)
- Feature Store, ML Models (4 models)
- **Status**: 🔄 QUEUED

### Phase 4: Intelligence & Decision Layer (Weeks 15-18)
- Intelligence Orchestrator, Decision Engine, LLM Integration
- **Status**: 🔄 QUEUED

### Phase 5: Execution & Automation (Weeks 19-22)
- Execution Engine, Experimentation Framework, Risk Management
- **Status**: 🔄 QUEUED

### Phase 6: Frontend & Analytics (Weeks 23-26)
- Web Dashboard, Analytics Views, User Management
- **Status**: 🔄 QUEUED

### Phase 7: Optimization & Feedback Loop (Weeks 27-30)
- Data Governance, Continuous Learning, Security
- **Status**: 🔄 QUEUED

### Phase 8: Scaling & Monitoring (Weeks 31+)
- Kubernetes deployment, Performance optimization
- **Status**: 🔄 QUEUED

**View full roadmap**: [ROADMAP.md](ROADMAP.md)

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL + Redis
- **Message Queue**: RabbitMQ
- **ML**: scikit-learn, XGBoost, PyTorch
- **LLM**: OpenAI API, Anthropic Claude

### Frontend
- **Framework**: React or Vue.js
- **UI**: Material-UI / Tailwind CSS
- **State**: Redux / Pinia
- **Charts**: Recharts

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 16 (if running locally without Docker)

### Setup with Docker

```bash
# 1. Clone repository
git clone <repo-url>
cd marketing-tool

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration

# 3. Start services
docker-compose up -d

# 4. Initialize database
docker-compose exec postgres psql -U aios_user -d aios_database -f /docker-entrypoint-initdb.d/schema.sql

# 5. Run migrations (when available)
docker-compose exec api_gateway alembic upgrade head
```

### Service Endpoints (Local Development)

| Service | Port | Health Check |
|---------|------|--------------|
| API Gateway | 8000 | `http://localhost:8000/health` |
| Auth Service | 8001 | `http://localhost:8001/health` |
| Business Service | 8002 | `http://localhost:8002/health` |
| Platform Integration | 8003 | `http://localhost:8003/health` |
| ML Service | 8004 | `http://localhost:8004/health` |
| Frontend | 3000 | `http://localhost:3000` |
| PostgreSQL | 5432 | `psql -U aios_user -d aios_database` |
| Redis | 6379 | `redis-cli ping` |
| RabbitMQ | 5672 | `http://localhost:15672` (admin/admin) |

## 📚 API Documentation

Once services are running:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🗄️ Database

### Schema Highlights

- **Users & Businesses**: Multi-user, multi-tenant architecture
- **Platform Accounts**: OAuth token management for 6+ platforms
- **Campaigns & Creatives**: Full campaign hierarchy
- **Performance Metrics**: Time-series data for all platforms
- **ML Predictions**: Versioned prediction logs
- **Audit Logs**: Complete action audit trail

**Initialize schema**:
```bash
psql -U aios_user -d aios_database -f database/schema.sql
```

## 🤖 Machine Learning Models

### 1. Audience Clustering
- **Inputs**: Demographics, interests, behavior, ROAS
- **Outputs**: Cluster ID, profitability score, scalability score

### 2. Creative Performance
- **Inputs**: Hook type, video length, watch time, CTR, format
- **Outputs**: Predicted CTR, CVR, creative score

### 3. ROAS Prediction
- **Inputs**: Budget, platform, creative score, audience cluster, seasonality
- **Outputs**: Predicted ROAS

### 4. Budget Optimization
- **Algorithm**: Multi-armed bandit
- **Objective**: Maximize ROI while minimizing waste

## 🎯 Decision Logic

### Platform Fit Score
```
Score = (40% ROAS) + (20% Engagement) + (20% Conversion Volume) + (20% Growth Potential)

- Score > 75: Scale (+20% budget)
- 50-75: Maintain (hold steady)
- < 50: Reduce (pause/test new creatives)
```

### Budget Scaling
```
if Predicted ROAS > Target → Increase 20%
if Predicted ROAS < Break-even → Pause
else → Test new creative
```

## 🔐 Security

- **Authentication**: OAuth2 + JWT tokens
- **Encryption**: TLS in transit, AES at rest
- **RBAC**: Role-based access control
- **Rate Limiting**: 1000 requests/hour per IP
- **Audit Logging**: Complete action trail
- **GDPR Compliant**: Data isolation, right to deletion

## 📊 Deployment Checklist

- [ ] Configure `.env` with production secrets
- [ ] Set up PostgreSQL with backups
- [ ] Configure Redis with persistence
- [ ] Set up RabbitMQ clustering
- [ ] Configure JWT secret key
- [ ] Add SSL certificates
- [ ] Configure monitoring & alerting
- [ ] Set up CI/CD pipeline
- [ ] Deploy to Kubernetes
- [ ] Configure DNS & load balancer
- [ ] Run security audit
- [ ] Set up logging aggregation

## 📞 Support & Contact

For questions, issues, or feature requests:
- 📧 Email: support@aios.dev
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📖 Docs: [Full Documentation](docs/README.md)

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last Updated**: February 22, 2026  
**Current Phase**: 1 - Foundation & Core Infrastructure  
**Overall Progress**: ~15% Complete  
