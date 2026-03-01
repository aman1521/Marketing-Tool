# Database Setup Guide

## Overview

Your AI Growth Operating System uses **PostgreSQL** as the primary database with **SQLAlchemy ORM** for Python integration.

## Architecture

```
┌─────────────────────────────────────┐
│   FastAPI Services (Python)         │
└────────────┬────────────────────────┘
             │
      ┌──────▼────────┐
      │  SQLAlchemy   │
      │   ORM Layer   │
      └──────┬────────┘
             │
      ┌──────▼────────────────────┐
      │   PostgreSQL Database     │
      │   (16 Tables)             │
      └───────────────────────────┘
```

## Files Created

### 1. **ORM Models** (`shared/models/orm_models.py`)
- SQLAlchemy model classes for all 16 database tables
- Relationships defined between tables
- Automatic timestamp management

### 2. **Database Configuration** (`shared/models/database.py`)
- Connection pooling
- Session management
- Database utilities

### 3. **Initialization Script** (`init_database.py`)
- Create all tables
- Reset database option

### 4. **Test Script** (`test_database.py`)
- Verify connectivity
- Test CRUD operations

## Quick Start

### Step 1: Start PostgreSQL

```bash
cd "d:\Marketing tool"
docker-compose up -d postgres
```

Verify it's running:
```bash
docker-compose ps postgres
```

### Step 2: Initialize Database

```bash
# Option A: Using Python script
python init_database.py

# Option B: Direct import
python -c "from shared.models.database import DatabaseConfig; DatabaseConfig.create_all_tables()"
```

Expected output:
```
Creating all tables...
✅ All tables created successfully
```

### Step 3: Test Database

```bash
python test_database.py
```

Expected output:
```
1. Testing Database Connection
   ✅ Database connection test passed

2. Checking Database Status
   ✅ Database is properly initialized

3. Testing User Creation
   ✅ User creation test passed

4. Testing User Query
   ✅ User query test passed

✅ All tests passed!
```

### Step 4: Start the Auth Service

```bash
docker-compose up -d auth_service
```

Check service status:
```bash
curl http://localhost:8001/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Auth Service",
  "database": {
    "connected": true,
    "tables_count": 16
  }
}
```

## Using the ORM

### Importing Models

```python
from shared.models.orm_models import User, Business, Campaign
from shared.models.database import DatabaseConfig, get_db
```

### Creating Records

```python
from shared.models.orm_models import User
from shared.models.database import DatabaseConfig

session = DatabaseConfig.get_session()

# Create new user
user = User(
    email="user@example.com",
    username="username",
    password_hash="hashed_password",
    first_name="John",
    last_name="Doe",
    role="business_owner"
)

session.add(user)
session.commit()
session.refresh(user)

print(f"Created user: {user.id}")
session.close()
```

### Querying Records

```python
from shared.models.orm_models import User
from shared.models.database import DatabaseConfig

session = DatabaseConfig.get_session()

# Get all users
users = session.query(User).all()

# Get by email
user = session.query(User).filter(User.email == "user@example.com").first()

# Filter and limit
active_users = session.query(User).filter(
    User.is_active == True
).limit(10).all()

session.close()
```

### With FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from shared.models.database import get_db
from shared.models.orm_models import User

@app.post("/api/v1/users")
async def create_user(email: str, db: Session = Depends(get_db)):
    user = User(email=email, username=email, password_hash="hash", role="business_owner")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": str(user.id), "email": user.email}
```

## Database Configuration

### Environment Variables

```bash
# Database connection
DATABASE_URL=postgresql://aios_user:aios_password@localhost:5432/aios_database

# Connection pooling
DATABASE_POOL_SIZE=20          # Connections per pool
DATABASE_MAX_OVERFLOW=10       # Additional connections allowed
DATABASE_POOL_RECYCLE=3600     # Recycle connections after X seconds

# Debug
DATABASE_ECHO_SQL=false        # Log SQL queries
```

### Modifying Connection Settings

Edit `.env`:
```bash
DATABASE_URL=postgresql://user:password@host:5432/db_name
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20
```

## Common Operations

### List All Tables

```bash
# Using Docker
docker-compose exec postgres psql -U aios_user -d aios_database -c "\dt"

# Using Python
python -c "
from shared.models.database import DatabaseConfig
from sqlalchemy import inspect

engine = DatabaseConfig.get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()

for table in sorted(tables):
    print(f'  - {table}')
"
```

### Backup Database

```bash
docker-compose exec postgres pg_dump -U aios_user aios_database > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U aios_user aios_database < backup.sql
```

### Reset Database

```bash
# WARNING: This will delete all data!
python init_database.py --reset
```

### Connect Using Command Line

```bash
docker-compose exec postgres psql -U aios_user -d aios_database
```

Then run SQL:
```sql
SELECT * FROM users;
SELECT COUNT(*) FROM campaigns;
\dt  -- List tables
\q  -- Quit
```

## Tables Overview

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **users** | User accounts | email, username, role |
| **businesses** | Business profiles | name, industry, business_type |
| **platform_accounts** | Ad platform credentials | platform_name, platform_token |
| **campaigns** | Ad campaigns | campaign_name, daily_budget |
| **ad_sets** | Ad sets within campaigns | adset_name, daily_budget |
| **creatives** | Ad creatives | creative_type, body_copy |
| **audience_clusters** | ML audience segments | cluster_name, profitability_score |
| **performance_metrics** | Campaign performance data | impressions, clicks, spend, revenue |
| **ml_predictions** | ML model predictions | prediction_type, predicted_value |
| **budget_allocations** | Recommended budget changes | recommended_budget, status |
| **strategy_outputs** | LLM-generated strategies | content_calendar, ad_copy_variations |
| **raw_data_logs** | Original API responses | data_type, raw_response |
| **audit_logs** | Action audit trail | action, resource_type |
| **api_errors** | API error tracking | error_code, error_message |
| **user_business_assignments** | User-to-business relationships | user_id, business_id |
| **campaign_creatives** | Campaign-to-creative relationships | campaign_id, creative_id |

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Start if not running
docker-compose up -d postgres

# Check logs
docker-compose logs postgres
```

### Tables Not Found

```bash
# Initialize database
python init_database.py

# Verify
python test_database.py
```

### Slow Queries

Check connection pooling:
```python
from shared.models.database import DatabaseConfig
engine = DatabaseConfig.get_engine()
print(f"Pool size: {engine.pool.size()}")
print(f"Checked in: {engine.pool.checkedin()}")
```

### Memory Issues

Reduce pool size in `.env`:
```bash
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=5
```

## Advanced Topics

### Custom Queries

```python
from sqlalchemy import func, and_

session = DatabaseConfig.get_session()

# Count users by role
from shared.models.orm_models import User

result = session.query(
    User.role,
    func.count(User.id).label('count')
).group_by(User.role).all()

for role, count in result:
    print(f"{role}: {count}")

session.close()
```

### Transactions

```python
session = DatabaseConfig.get_session()

try:
    # Multiple operations
    user = User(email="test@example.com", ...)
    session.add(user)
    
    campaign = Campaign(...)
    session.add(campaign)
    
    session.commit()  # All or nothing
except Exception as e:
    session.rollback()
finally:
    session.close()
```

### Bulk Operations

```python
from sqlalchemy import insert

session = DatabaseConfig.get_session()

users = [
    {"email": "user1@example.com", "username": "user1", ...},
    {"email": "user2@example.com", "username": "user2", ...},
]

session.execute(insert(User), users)
session.commit()
session.close()
```

## Next Steps

1. ✅ Database initialized and tested
2. ▶️ **Next**: Implement business logic in services
3. ▶️ Create admin user for testing
4. ▶️ Add more ORM methods as needed
5. ▶️ Set up database backups

See [ROADMAP.md](ROADMAP.md) for implementation phases.

## Support

- Check logs: `docker-compose logs postgres`
- Test connection: `python test_database.py`
- Read SQLAlchemy docs: https://docs.sqlalchemy.org/
- PostgreSQL docs: https://www.postgresql.org/docs/

---

**Status**: ✅ Database ORM Integration Complete
