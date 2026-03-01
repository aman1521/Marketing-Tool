# Local Development Environment Setup - Complete ✅

## 🎉 Setup Status

### ✅ Completed

- [x] Python 3.13 configured
- [x] Core packages installed (FastAPI, SQLAlchemy, Pydantic, etc.)
- [x] Docker services started (PostgreSQL, Redis, RabbitMQ)
- [x] Database connectivity verified
- [x] All core dependencies available

---

## 🚀 What's Running Now

### Docker Services (Running on localhost)

| Service | Port | Status | Credentials |
|---------|------|--------|-------------|
| **PostgreSQL** | 5432 | ✅ Running | User: `aios_user` / Pass: `aios_password` |
| **Redis** | 6379 | ✅ Running | default |
| **RabbitMQ** | 5672 | ✅ Running | User: `admin` / Pass: `admin` |
| **RabbitMQ UI** | 15672 | ✅ Running | <http://localhost:15672> |

### Python Environment

```
Python Version: 3.13.6
Location: C:/Python313/python.exe
Packages Installed: 40+ core packages
Setup: Ready for development
```

---

## 📋 Next Steps

### 1. Create Local Environment File

```powershell
# Copy the template to create your local .env file
copy ".env.example" ".env"
```

**Key configurations already set:**

- Database: `postgresql://aios_user:aios_password@localhost:5432/aios_database`
- Redis: `redis://localhost:6379/0`
- RabbitMQ: `amqp://admin:admin@localhost:5672/`

---

### 2. Initialize Database Schema

```powershell
# Terminal 1: Run the database initialization script
C:\Python313\python.exe init_database.py
```

**Expected output:**

```
Database Initialization Script
============================================================
1. Verifying database configuration...
   Database URL: postgresql://aios_user:***
   Pool Size: 20
   ✅ Database connection successful

2. Creating database tables...
   ✅ All tables created successfully

3. Verifying tables...
   ✅ 16 tables created
   
✅ Database initialization complete!
```

---

### 3. Test Database Connection

```powershell
# Terminal 2: Run the test script
C:\Python313\python.exe test_database.py
```

**Expected output:**

```
Database Setup Verification Tests
============================================================

1. Testing Database Connection
   ✅ Database connection test passed

2. Checking Database Status
   ✅ Database is properly initialized

3. Testing User Creation
   ✅ User creation test passed

4. Testing User Query
   ✅ User query test passed

✅ All tests passed! Database is ready to use.
```

---

### 4. Start the Behavior Analyzer Service

```powershell
# Terminal 3: Build and start the behavior analyzer microservice
docker-compose up behavior_analyzer_service
```

**Monitor the logs - you should see:**

```
behavior_analyzer_service    | INFO:     Uvicorn running on http://0.0.0.0:8009
behavior_analyzer_service    | INFO:     Application startup complete
```

---

### 5. Test Behavior Analyzer Service

Once the service starts:

```powershell
# Health check
curl http://localhost:8009/health

# Test engagement analysis
curl -X POST http://localhost:8009/api/v1/analyze/engagement `
  -H "Content-Type: application/json" `
  -d @- <<'EOF'
{
  "platform": "tiktok",
  "watch_retention": 0.85,
  "save_rate": 0.08,
  "share_rate": 0.15,
  "comment_rate": 0.12,
  "view_count": 120000
}
EOF
```

**Expected response:**

```json
{
  "emotional_resonance_score": 0.1,
  "information_value_score": 0.7,
  "viral_potential_score": 0.27,
  "content_type": "Viral",
  "recommendation": "Focus on shareability and emotional hooks"
}
```

---

### 6. Start Auth Service (Optional)

```powershell
# Terminal 4: Start the auth service
docker-compose up auth_service
```

Once running:

```powershell
# Test registration
curl -X POST http://localhost:8001/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d @- <<'EOF'
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "SecurePassword123!",
  "first_name": "Test",
  "last_name": "User"
}
EOF
```

---

## 🛠️ Useful Commands

### Docker Management

```powershell
# View all services
docker-compose ps

# View logs for a service
docker-compose logs -f behavior_analyzer_service

# Stop all services
docker-compose down

# Stop and remove volumes (reset data)
docker-compose down -v

# Restart a specific service
docker-compose restart postgres
```

### Database Access

```powershell
# Connect with psql (if installed)
psql -h localhost -U aios_user -d aios_database

# Or use Python
C:\Python313\python.exe -c "
from shared.models.database import DatabaseConfig
from shared.models.orm_models import User
session = DatabaseConfig.get_session()
users = session.query(User).all()
print(f'Total users: {len(users)}')
session.close()
"
```

### Testing

```powershell
# Run all tests
pytest -v

# Run specific test module
pytest backend/behavior_analyzer_service/test_behavior_analyzer.py -v

# Run with coverage
pytest --cov=backend --cov=shared
```

---

## 📚 Documentation

Once services are running, access these URLs:

| Resource | URL |
|----------|-----|
| **Behavior Analyzer Docs** | <http://localhost:8009/docs> |
| **Behavior Analyzer ReDoc** | <http://localhost:8009/redoc> |
| **RabbitMQ Management** | <http://localhost:15672> (admin/admin) |
| **API Gateway (when running)** | <http://localhost:8000/docs> |

---

## 📋 Architecture Overview

```
Your Local Machine
├── Python 3.13 (development scripts)
├── Docker Services
│   ├── PostgreSQL (5432)
│   ├── Redis (6379)
│   ├── RabbitMQ (5672)
│   ├── Behavior Analyzer (8009) [Optional - on demand]
│   └── Auth Service (8001) [Optional - on demand]
└── Project Code
    ├── shared/utils/feature_library.py
    ├── shared/models/ (ORM models)
    ├── backend/behavior_analyzer_service/
    └── backend/auth_service/
```

---

## 🔧 Troubleshooting

### Port Already in Use

If you get "port is already allocated" errors:

```powershell
# Check what's using the port (e.g., 5432 for PostgreSQL)
netstat -ano | findstr :5432

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or just change the port in docker-compose.yml
```

### Database Connection Error

```powershell
# Make sure PostgreSQL container is healthy
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

### Python Import Errors

```powershell
# Reinstall packages
C:\Python313\python.exe -m pip install --force-reinstall fastapi uvicorn pydantic --user

# Check installed packages
C:\Python313\python.exe -m pip list
```

---

## ✅ Verification Checklist

Run these commands in order to verify everything is set up:

```powershell
# 1. Check Docker
✔️ docker --version

# 2. Check Python
✔️ C:\Python313\python.exe --version

# 3. Check services running
✔️ docker-compose ps

# 4. Test database connection
✔️ C:\Python313\python.exe test_database.py

# 5. Check behavior analyzer service (if started)
✔️ curl http://localhost:8009/health
```

---

## 🎯 You're Now Ready To

- ✅ Run Python scripts and tests locally
- ✅ Connect to PostgreSQL, Redis, RabbitMQ
- ✅ Start any microservice on demand
- ✅ Test behavior analyzer endpoints
- ✅ Develop and debug locally
- ✅ Run the full test suite

---

## 📖 Getting Started with Development

### Run Database Tests

```powershell
cd "d:\Marketing tool"
C:\Python313\python.exe test_database.py
```

### Run Behavior Analyzer Tests

```powershell
cd "d:\Marketing tool"
pytest backend/behavior_analyzer_service/test_behavior_analyzer.py -v
```

### Start All Services (for integration testing)

```powershell
cd "d:\Marketing tool"
docker-compose up -d
# Services start in background
```

### Clean Up and Reset

```powershell
cd "d:\Marketing tool"
docker-compose down  # Stops all services but keeps data
docker-compose down -v  # Stops and deletes all data
```

---

**Setup Date**: February 23, 2026  
**Status**: ✅ Ready for Development  
**Next**: Initialize database and start testing!
