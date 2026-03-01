# Quick Commands Reference

## 🚀 Essential Commands

### Start Development Environment

```powershell
# Start all infrastructure (one-time or after docker-compose down)
docker-compose up -d

# View running services
docker-compose ps

# View service logs
docker-compose logs -f <service_name>
```

### Initialize Database

```powershell
# Create tables and schema
C:\Python313\python.exe init_database.py

# Test the connection
C:\Python313\python.exe test_database.py
```

### Run Services

```powershell
# Auth Service
docker-compose up auth_service

# Behavior Analyzer Service
docker-compose up behavior_analyzer_service

# All services in background
docker-compose up -d
```

### Run Tests

```powershell
# Behavior analyzer tests
pytest backend/behavior_analyzer_service/test_behavior_analyzer.py -v

# All tests with coverage
pytest --cov=backend --cov=shared -v

# Specific test class
pytest backend/behavior_analyzer_service/test_behavior_analyzer.py::TestEngagementAnalyzer -v
```

### Database Access

```powershell
# Query users via Python
C:\Python313\python.exe -c "
from shared.models.database import DatabaseConfig
from shared.models.orm_models import User
s = DatabaseConfig.get_session()
print(f'Users: {len(s.query(User).all())}')
s.close()
"

# Using psql (if PostgreSQL client installed)
psql -h localhost -U aios_user -d aios_database
```

### API Testing

```powershell
# Health check (behavior analyzer)
curl http://localhost:8009/health

# Engagement analysis
curl -X POST http://localhost:8009/api/v1/analyze/engagement \
  -H "Content-Type: application/json" \
  -d '{"platform":"tiktok","watch_retention":0.85,"save_rate":0.08,"share_rate":0.15,"comment_rate":0.12,"view_count":120000}'

# Intent classification
curl -X POST http://localhost:8009/api/v1/classify/intent \
  -H "Content-Type: application/json" \
  -d '{"scroll_depth":0.85,"pages_visited":3.2,"time_on_site":245,"has_added_to_cart":true,"is_previous_purchaser":false,"email_opens":0,"abandoned_carts":0}'
```

### Docker Management

```powershell
# Stop all services (keeps data)
docker-compose down

# Remove everything (reset)
docker-compose down -v

# Restart a service
docker-compose restart postgres

# View specific service logs
docker-compose logs postgres

# Build a service
docker-compose build behavior_analyzer_service

# Push to remove volumes and recreate
docker-compose up --force-recreate --build behavior_analyzer_service
```

### Python Development

```powershell
# Check installed packages
C:\Python313\python.exe -m pip list

# Install additional package
C:\Python313\python.exe -m pip install <package_name> --user

# Create a virtual environment (optional)
C:\Python313\python.exe -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

---

## 🌐 Access URLs

| Service | URL | Debug |
|---------|-----|-------|
| Behavior Analyzer API | http://localhost:8009 | /docs |
| Auth Service | http://localhost:8001 | /docs |
| API Gateway | http://localhost:8000 | /docs |
| RabbitMQ UI | http://localhost:15672 | admin/admin |
| PostgreSQL | localhost:5432 | User: aios_user |
| Redis | localhost:6379 | - |

---

## 📝 Common Workflows

### Local Development Cycle

```powershell
# 1. Start services
docker-compose up -d postgres redis rabbitmq

# 2. Initialize database
C:\Python313\python.exe init_database.py

# 3. Run tests
pytest backend/behavior_analyzer_service/test_behavior_analyzer.py -v

# 4. Start service locally (in new terminal)
docker-compose up behavior_analyzer_service

# 5. Test endpoint
curl http://localhost:8009/health

# 6. Make changes to code

# 7. Restart service to see changes
# (Press Ctrl+C in service terminal, then run again)
```

### Database Debugging

```powershell
# 1. Check connection
C:\Python313\python.exe test_database.py

# 2. Query directly
psql -h localhost -U aios_user -d aios_database -c "SELECT COUNT(*) FROM users;"

# 3. Reset database
docker-compose restart postgres
C:\Python313\python.exe init_database.py
```

### Testing New Code

```powershell
# 1. Write test in test_behavior_analyzer.py

# 2. Run just that test
pytest backend/behavior_analyzer_service/test_behavior_analyzer.py::TestYourClass::test_your_method -v

# 3. Run all related tests
pytest backend/behavior_analyzer_service/ -v

# 4. Once working, run full suite
pytest --cov=backend --cov=shared
```

---

## ⚡ Performance Tips

```powershell
# Run pytest in parallel (faster)
pytest -n auto

# Run only tests that failed last time
pytest --lf

# Run most recently modified tests
pytest --ff

# Stop after first failure
pytest -x

# Show slowest tests
pytest --durations=10
```

---

## 🔍 Monitoring

```powershell
# Watch service logs in real-time
docker-compose logs -f behavior_analyzer_service

# Check resource usage
docker stats

# Inspect container
docker inspect aios_postgres

# Check network connectivity between containers
docker exec -it aios_postgres ping aios_redis
```

---

**Created**: February 23, 2026  
**For**: Marketing Tool Development
