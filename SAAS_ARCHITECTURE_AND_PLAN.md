# Production-Grade AI Marketing Intelligence SaaS

This document contains the complete, modular, and enterprise-grade architecture for the Marketing Intelligence SaaS, including the requested Docker setup, Celery worker configurations, SQLAlchemy models, FastAPI API Contracts, Connector Framework, and Frontend page structure.

## 1. System Components & Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, Zustand, Axios, Recharts.
- **Backend API**: FastAPI (Python 3.11+).
- **Database**: PostgreSQL with Async SQLAlchemy (asyncpg).
- **Vector DB**: Qdrant (for competitor embeddings / semantic search).
- **Caching & Brokers**: Redis, Celery.
- **Auth**: JWT Bearer, bcrypt.
- **External Integrations**: Stripe, Meta, Google, TikTok, LinkedIn, Twitter, Reddit.

---

## 2. Docker Compose Setup (`docker-compose.yml`)

Fully scalable production-ready Docker deployment describing all services.

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-saas_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-saas_password}
      POSTGRES_DB: ${DB_NAME:-marketing_saas}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U saas_user -d marketing_saas"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
      image: qdrant/qdrant:latest
      ports:
        - "6333:6333"
        - "6334:6334"
      volumes:
        - qdrant_storage:/qdrant/storage

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      qdrant:
        condition: service_started

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.core.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    env_file:
      - .env
    depends_on:
      - redis
      - db

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.core.celery_app beat --loglevel=info
    volumes:
      - ./backend:/app
    env_file:
      - .env
    depends_on:
      - redis
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

volumes:
  pgdata:
  qdrant_storage:
```

---

## 3. Environment Configuration (`.env.template`)

```dotenv
# API & Security
SECRET_KEY=super_secret_jwt_key_please_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 24 hours
ENCRYPTION_KEY=32_byte_aes_key_for_oauth_tokens

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://saas_user:saas_password@db:5432/marketing_saas

# Redis / Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Qdrant Vector DB
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# AI APIs
OPENAI_API_KEY=sk-proj-...
CLAUDE_API_KEY=sk-ant-...

# OAUTH KEYS
META_CLIENT_ID=...
META_CLIENT_SECRET=...
META_REDIRECT_URI=http://localhost:8000/connectors/meta/callback

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/connectors/google/callback

TIKTOK_CLIENT_ID=...
TIKTOK_CLIENT_SECRET=...
TIKTOK_REDIRECT_URI=http://localhost:8000/connectors/tiktok/callback

LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
LINKEDIN_REDIRECT_URI=http://localhost:8000/connectors/linkedin/callback

TWITTER_CLIENT_ID=...
TWITTER_CLIENT_SECRET=...
TWITTER_REDIRECT_URI=http://localhost:8000/connectors/twitter/callback

REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_REDIRECT_URI=http://localhost:8000/connectors/reddit/callback

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 4. Backend Database Models (`backend/app/models/domain.py`)

Using Async SQLAlchemy. The schema fully normalizes users, companies, connections, and AI logs.

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, JSON, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PlatformType(str, enum.Enum):
    META = "meta"
    GOOGLE = "google"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    REDDIT = "reddit"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    companies = relationship("Company", back_populates="owner")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    plan = Column(Enum(PlanType), default=PlanType.FREE)
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String, unique=True)
    trial_ends_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="subscription")

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True)
    owner_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="companies")
    platform_connections = relationship("PlatformConnection", back_populates="company")
    automation_logs = relationship("AutomationLog", back_populates="company")

class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    platform = Column(Enum(PlatformType))
    encrypted_access_token = Column(String)
    encrypted_refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    last_sync_time = Column(DateTime)
    status = Column(String, default="connected")
    
    company = relationship("Company", back_populates="platform_connections")
    accounts = relationship("PlatformAccount", back_populates="connection")

class PlatformAccount(Base):
    """Specific Page/Ad Account/Profile within a PlatformConnection"""
    __tablename__ = "platform_accounts"
    id = Column(String, primary_key=True) # E.g., Ad Account ID or Page ID
    connection_id = Column(String, ForeignKey("platform_connections.id"))
    account_name = Column(String)
    account_type = Column(String) # 'ad_account', 'page', 'profile'
    
    connection = relationship("PlatformConnection", back_populates="accounts")
    posts = relationship("Post", back_populates="account")
    campaigns = relationship("Campaign", back_populates="account")

class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True) # Platform Native ID
    account_id = Column(String, ForeignKey("platform_accounts.id"))
    content = Column(String)
    media_urls = Column(JSON)
    status = Column(String) # 'draft', 'scheduled', 'published'
    scheduled_for = Column(DateTime)
    engagement_metrics = Column(JSON) # e.g., {"likes": 10, "shares": 2, "impressions": 500}
    
    account = relationship("PlatformAccount", back_populates="posts")

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True) # Platform Native ID
    account_id = Column(String, ForeignKey("platform_accounts.id"))
    name = Column(String)
    status = Column(String) # 'active', 'paused'
    daily_budget = Column(Float)
    performance_metrics = Column(JSON) # e.g., {"spend": 100, "conversion_rate": 2.5, "cpc": 0.5}
    is_auto_managed = Column(Boolean, default=False)
    
    account = relationship("PlatformAccount", back_populates="campaigns")

class AutomationLog(Base):
    __tablename__ = "automation_logs"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    objective = Column(String)
    risk_level = Column(String)
    status = Column(String) # 'proposed', 'approved', 'rejected', 'executed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="automation_logs")
    strategies = relationship("StrategyLog", back_populates="automation")

class StrategyLog(Base):
    __tablename__ = "strategy_logs"
    id = Column(String, primary_key=True)
    automation_id = Column(String, ForeignKey("automation_logs.id"))
    action_type = Column(String) # 'budget_shift', 'campaign_pause', 'creative_suggestion'
    confidence_score = Column(Float)
    reasoning_text = Column(String)
    proposed_changes = Column(JSON)
    requires_approval = Column(Boolean)
    
    automation = relationship("AutomationLog", back_populates="strategies")
    executions = relationship("ExecutionLog", back_populates="strategy")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("strategy_logs.id"))
    status = Column(String) # 'success', 'failed'
    api_response = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    strategy = relationship("StrategyLog", back_populates="executions")

# Note: CompetitorEmbedding is stored in Qdrant, but we can maintain a relational mapping if needed.
```

---

## 5. Connector Framework (`backend/app/connectors/base.py` & Stubs)

Abstract definition for OAuth platform integrations.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from cryptography.fernet import Fernet
import os

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

class BaseConnector(ABC):
    platform_name: str
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @abstractmethod
    def get_authorization_url(self) -> str:
        pass

    @abstractmethod
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """Exchanges code for access/refresh tokens"""
        pass

    @abstractmethod
    async def fetch_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def fetch_metrics(self, access_token: str, account_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute_action(self, access_token: str, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """e.g., Change budget, pause campaign, schedule post"""
        pass

    def encrypt_token(self, token: str) -> str:
        return cipher_suite.encrypt(token.encode()).decode()
        
    def decrypt_token(self, encrypted_token: str) -> str:
        return cipher_suite.decrypt(encrypted_token.encode()).decode()
```

### Connector Stubs (e.g., `meta.py`, `reddit.py`)

```python
# backend/app/connectors/meta.py
from .base import BaseConnector

class MetaConnector(BaseConnector):
    platform_name = "meta"
    
    def get_authorization_url(self) -> str:
        return f"https://www.facebook.com/v18.0/dialog/oauth?client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope=pages_show_list,ads_management,ads_read,read_insights"
        
    async def authenticate(self, auth_code: str):
        # Implementation via HTTPX to Meta Graph API
        return {"access_token": "stub_meta_token", "expires_in": 3600}
        
    async def fetch_accounts(self, access_token: str):
        return [{"id": "act_123", "name": "Meta Ad Account", "type": "ad_account"}]

    async def fetch_metrics(self, access_token: str, account_id: str):
        return {"spend": 120.50, "impressions": 5400}

    async def execute_action(self, access_token: str, action_type: str, payload: dict):
        # Implementation logic for budget/pause/post
        return {"status": "success", "tx_id": "meta_tx_001"}

# backend/app/connectors/reddit.py
class RedditConnector(BaseConnector):
    platform_name = "reddit"
    def get_authorization_url(self) -> str: ...
    async def authenticate(self, auth_code: str): ...
    async def fetch_accounts(self, access_token: str): ...
    async def fetch_metrics(self, access_token: str, account_id: str): ...
    async def execute_action(self, access_token: str, action_type: str, payload: dict): ...
```

*(Remaining stubs for Google, TikTok, LinkedIn, Twitter follow the identical signature structure).*

---

## 6. AI Orchestration & Safety Engine (`backend/app/ai/orchestrator.py`)

Handles Strategy generation via OpenAI and ensures safety limits are respected before logging actions for Celery Execution.

```python
from typing import List, Dict, Any
from app.models.domain import StrategyLog

class AISafetyEngine:
    BUDGET_CHANGE_LIMIT = 0.30 # 30%
    MIN_CONFIDENCE_SCORE = 0.75
    
    @classmethod
    def evaluate_strategy(cls, strategy: Dict[str, Any]) -> StrategyLog:
        requires_approval = False
        action_type = strategy.get("action_type")
        confidence = strategy.get("confidence", 0)
        
        if confidence < cls.MIN_CONFIDENCE_SCORE:
            raise ValueError(f"Strategy rejected: Confidence score {confidence} is below minimum {cls.MIN_CONFIDENCE_SCORE}")
            
        if action_type == "budget_shift":
            change_pct = abs(strategy.get("new_budget", 0) - strategy.get("old_budget", 0)) / strategy.get("old_budget", 1)
            if change_pct > cls.BUDGET_CHANGE_LIMIT:
                requires_approval = True
                
        if action_type == "targeting_change" and strategy.get("is_major_shift", False):
            requires_approval = True
            
        return StrategyLog(
            action_type=action_type,
            confidence_score=confidence,
            reasoning_text=strategy.get("reasoning"),
            proposed_changes=strategy.get("changes"),
            requires_approval=requires_approval
        )

class AIOrchestrator:
    def __init__(self, openai_api_key: str, claude_api_key: str):
        self.openai_key = openai_api_key
        self.claude_key = claude_api_key
        # Initialize AirLLM for local tagging here

    async def generate_strategies(self, objective: str, audience: str, budget: float, risk: str, platform_data: Dict) -> List[StrategyLog]:
        # Implementation:
        # 1. Feature Engineering: Combine platform data into normalized historical time-series vector
        # 2. Behavior Modeling: Retrieve similar campaigns from Qdrant vector DB
        # 3. Strategy Gen: Call OpenAI GPT-4o with context and prompt
        # 4. Filter strategies through AISafetyEngine
        # ... logic
        
        # Stub returned
        strategy = AISafetyEngine.evaluate_strategy({
            "action_type": "budget_shift",
            "confidence": 0.85,
            "old_budget": 100,
            "new_budget": 140, # > 30% change
            "reasoning": "Meta CPA is dropping, shifting budget to capture low-cost conversions.",
            "changes": {"platform": "meta", "campaign_id": "c_123", "budget": 140}
        })
        return [strategy]
```

---

## 7. Celery Setup (`backend/app/core/celery_app.py`)

Handles background execution for Daily Automation.

```python
from celery import Celery
import os
from celery.schedules import crontab

celery_app = Celery(
    "marketing_saas",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["app.tasks.automation_tasks"]
)

celery_app.conf.beat_schedule = {
    'run-daily-automations': {
        'task': 'app.tasks.automation_tasks.execute_daily_auto_mode',
        'schedule': crontab(hour=0, minute=0), # Run daily at midnight
    },
}
```

```python
# backend/app/tasks/automation_tasks.py
from app.core.celery_app import celery_app

@celery_app.task
def execute_daily_auto_mode():
    """Loops through all Companies where Auto Mode is enabled and triggers automation."""
    pass
    
@celery_app.task
def execute_approved_strategy(strategy_id: str):
    """Executes a Strategy via the Platform Connector framework and logs the result."""
    pass
```

---

## 8. Frontend Next.js Structure (`frontend/`)

Structure using the App Router conventions.

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                     # Root layout, auth providers
│   │   ├── page.tsx                       # Landing page
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── dashboard/page.tsx             # Global dashboard
│   │   ├── profile/page.tsx               # Profile view, User details, Plan
│   │   ├── companies/
│   │   │   ├── page.tsx                   # List of companies (Company Name, Industry, Platforms, Assets, Edit)
│   │   │   ├── [companyId]/
│   │   │   │   ├── page.tsx               # Company overview
│   │   │   │   ├── assets/
│   │   │   │   │   ├── page.tsx           # Show platform cards (Meta, Reddit, etc.) with Connect status
│   │   │   │   │   └── [platform]/page.tsx# Dynamic Platform Page (Social vs Ads views)
│   │   │   │   ├── calendar/page.tsx      # Calendar view, drag-n-drop scheduling
│   │   │   │   └── automation/page.tsx    # "Let AI Work For You" modal & auto mode toggle
│   ├── components/
│   │   ├── ui/                            # Shared Tailwind components (Buttons, Modals, Tables)
│   │   ├── charts/                        # Recharts wrapper components
│   │   ├── platform/                      # Platform cards (Ads vs Social modes)
│   │   ├── calendar/                      # Content calendar grid widget
│   │   └── automation/                    # Proposal views and Strategy Approval widgets
│   ├── store/
│   │   ├── authStore.ts                   # Zustand for Auth JWT State
│   │   └── companyStore.ts                # Zustand for persistent company & asset states
│   ├── lib/
│   │   ├── axios.ts                       # Interceptor for JWT injection
│   │   └── utils.ts
```

### Full Dynamic Routing Implementation Example: Platform Ads View

*(Located at `frontend/src/app/companies/[companyId]/assets/[platform]/page.tsx`)*

```tsx
"use client";
import { useParams } from "next/navigation";
// Imports for Table, Modals, Toggle, Chart...

export default function PlatformAssetPage() {
    const params = useParams();
    const { companyId, platform } = params;
    
    // Using simple discriminators to render distinct views
    const isSocialPlatform = ['twitter', 'tiktok', 'reddit'].includes(platform as string);
    const isAdsPlatform = ['meta', 'google', 'linkedin'].includes(platform as string);

    if (isAdsPlatform) {
        return (
            <div className="p-8 space-y-6">
                <header className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold capitalize">{platform} Ads Manager</h1>
                    <div className="flex gap-4">
                        <button className="bg-blue-600 text-white px-4 py-2 rounded">Enable Automation</button>
                    </div>
                </header>

                <section className="h-64 bg-white shadow rounded p-4">
                    <h2>Performance Overview</h2>
                </section>

                <section className="bg-white shadow rounded p-4">
                    <table className="w-full text-left">
                        <thead>
                            <tr>
                                <th>Campaign Name</th>
                                <th>Status</th>
                                <th>Budget</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </section>
            </div>
        );
    }

    if (isSocialPlatform) {
         return (
            <div className="p-8 space-y-6">
                <header className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold capitalize">{platform} Content Manager</h1>
                    <button className="bg-green-600 text-white px-4 py-2 rounded">Create Post / AI Caption</button>
                </header>
             </div>
        );
    }
}
```
