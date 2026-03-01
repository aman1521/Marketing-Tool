# Quick Start Guide - AI Growth Operating System

## Getting Started (5 minutes)

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate
cd Marketing\ tool

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Verify services are running
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Option 2: Local Development

**Prerequisites:**
```bash
python 3.11
pip install -r requirements.txt
```

**Start services individually:**

```bash
# Terminal 1: API Gateway
cd backend/api_gateway
python main.py

# Terminal 2: Auth Service
cd backend/auth_service
python main.py

# Terminal 3: Business Service
cd backend/business_service
python main.py

# ... and so on for other services
```

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 8000 | http://localhost:8000 |
| Auth Service | 8001 | http://localhost:8001 |
| Business Service | 8002 | http://localhost:8002 |
| Platform Integration | 8003 | http://localhost:8003 |
| ML Service | 8004 | http://localhost:8004 |
| Attribution Engine | 8005 | http://localhost:8005 |
| Intelligence Orchestrator | 8006 | http://localhost:8006 |
| Decision Engine | 8007 | http://localhost:8007 |
| Execution Engine | 8008 | http://localhost:8008 |
| Frontend | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| RabbitMQ | 5672 | localhost:5672 |
| RabbitMQ UI | 15672 | http://localhost:15672 |

## First Steps

### 1. Check Health Status
```bash
curl http://localhost:8000/health
```

### 2. View API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Access PostgreSQL
```bash
# Using psql
psql -U aios_user -d aios_database -h localhost

# Or using Docker
docker-compose exec postgres psql -U aios_user -d aios_database
```

### 4. View RabbitMQ Management
- URL: http://localhost:15672
- Username: admin
- Password: admin

### 5. Redis CLI
```bash
docker-compose exec redis redis-cli
```

## Sample API Calls

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### Create Business
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/v1/businesses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Business",
    "industry": "E-commerce",
    "business_type": "ecommerce",
    "margin_percentage": 25.5,
    "sales_cycle_days": 5,
    "subscription_model": false
  }'
```

## Common Issues

### Services won't start
```bash
# Check logs
docker-compose logs -f service_name

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database initialization
docker-compose logs postgres
```

### Port already in use
```bash
# Change port in docker-compose.yml
# Or kill process using port:
# Linux/Mac: lsof -i :8000
# Windows: netstat -ano | findstr :8000
```

## Database

### Initialize Schema
```bash
docker-compose exec postgres pg_restore \
  -U aios_user \
  -d aios_database \
  < database/schema.sql
```

### View Database
```bash
docker-compose exec postgres psql -U aios_user -d aios_database -c "\dt"
```

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api_gateway

# Follow in real-time
docker-compose logs -f --tail=100
```

### Service Health
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose logs auth_service
```

## Development Workflow

### 1. Make Code Changes
Edit files in `backend/*/main.py` (hot-reload enabled)

### 2. Test Endpoints
Use Swagger UI or curl commands

### 3. Check Logs
```bash
docker-compose logs -f service_name
```

### 4. Testing
```bash
# Run unit tests
pytest backend/api_gateway/tests/

# Run with coverage
pytest --cov=backend/ --cov-report=html
```

## Next Steps

1. **Explore the Database**: View schema in `database/schema.sql`
2. **Read the Architecture**: Check [ROADMAP.md](ROADMAP.md)
3. **Check the Code**: Start with `backend/api_gateway/main.py`
4. **Join Development**: Pick a task from Phase 1 in ROADMAP.md

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop service_name
```

## Production Deployment

See [infrastructure/README.md](infrastructure/README.md) for Kubernetes deployment.

---

**Need Help?**
- Check logs: `docker-compose logs`
- Read docs: `http://localhost:8000/docs`
- See issues: Check GitHub Issues
