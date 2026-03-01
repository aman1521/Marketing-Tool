# Contributing Guide

## How to Contribute to AI Growth Operating System

Thank you for your interest in contributing! This guide will help you get started.

## Setting Up Your Development Environment

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Marketing tool"
```

### 2. Install Dependencies
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Add API keys, database credentials, etc.
```

### 4. Start Services
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Verify services
docker-compose ps
curl http://localhost:8000/health
```

## Development Workflow

### Creating a New Feature

1. **Create a feature branch**
   ```bash
   git checkout -b feature/description-of-feature
   ```

2. **Make your changes**
   - Follow the code structure in [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
   - Write code in the appropriate service directory
   - Add tests as you go

3. **Test your changes**
   ```bash
   # Run unit tests
   pytest backend/service_name/tests/
   
   # Run with coverage
   pytest --cov=backend/service_name --cov-report=html
   ```

4. **Check code quality**
   ```bash
   # Format code
   black backend/service_name/
   
   # Check for issues
   flake8 backend/service_name/
   
   # Type checking
   mypy backend/service_name/
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/description-of-feature
   ```

7. **Create a Pull Request**
   - Provide clear description
   - Reference any related issues
   - Ensure all tests pass

## Code Standards

### Python Code Style
- Follow PEP 8
- Use type hints
- Max line length: 88 characters
- Use `black` for formatting

### Naming Conventions
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Files**: `snake_case.py`

### API Endpoints
- Use RESTful conventions
- Version endpoints: `/api/v1/...`
- Use HTTP status codes correctly
- Include request/response documentation

### Database
- Use migrations for schema changes
- Write indexes for frequently queried fields
- Document foreign key relationships
- Add audit timestamps (`created_at`, `updated_at`)

## Working with Services

### Adding a New Endpoint

1. **Identify the correct service** - Which service should handle this?

2. **Create the endpoint in the service**
   ```python
   from fastapi import FastAPI
   from pydantic import BaseModel
   
   app = FastAPI()
   
   @app.post("/api/v1/resource")
   async def create_resource(data: ResourceCreate):
       # Implementation
       return ResourceResponse(...)
   ```

3. **Add request/response models** in `shared/models/shared_models.py`

4. **Test the endpoint**
   ```bash
   curl -X POST http://localhost:PORT/api/v1/resource \
     -H "Content-Type: application/json" \
     -d '{"key": "value"}'
   ```

5. **Document in API docs** - FastAPI auto-generates from docstrings

### Modifying Database Schema

1. **Update `database/schema.sql`** - Add/modify table definitions

2. **Create migration** (when Alembic is set up)
   ```bash
   alembic revision --autogenerate -m "Add new table"
   alembic upgrade head
   ```

3. **Update ORM models** in `shared/models/` if using SQLAlchemy

4. **Update Pydantic models** for new fields

## Testing

### Writing Tests

Create test files in `backend/service_name/tests/`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_endpoint_success():
    response = client.post("/api/v1/resource", json={"data": "value"})
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_endpoint_not_found():
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest backend/service_name/tests/test_main.py

# Run with coverage
pytest --cov=backend/ --cov-report=html

# Run with verbose output
pytest -v
```

## Docker Development

### Building and Testing Locally

```bash
# Build specific service
docker-compose build service_name

# Run specific service
docker-compose up service_name

# View logs
docker-compose logs -f service_name

# Run command in container
docker-compose exec service_name bash
```

### Debugging

```bash
# View detailed logs
docker-compose logs -f --tail=50 service_name

# Inspect container
docker-compose exec service_name bash

# Check environment variables
docker-compose exec service_name env | grep VARIABLE
```

## Git Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code refactoring without feature changes
- **perf**: Performance improvements
- **test**: Test additions or changes
- **chore**: Dependency updates, build script changes

### Examples
```
feat(auth): add JWT refresh token support
fix(ml-service): correct ROAS calculation
docs(api): update endpoint documentation
refactor(business-service): simplify constraint logic
```

## Pull Request Process

1. **Fork the repository** on GitHub

2. **Create a feature branch** with a descriptive name

3. **Make your changes** following code standards

4. **Write tests** for new functionality

5. **Update documentation** if adding features

6. **Push to your fork**

7. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots if UI changes
   - Test results

8. **Address review feedback**

9. **Ensure CI/CD passes** (when set up)

10. **Merge when approved**

## Code Review Guidelines

When reviewing code:
- Check code follows style guidelines
- Verify tests are included
- Ensure no breaking changes
- Verify documentation is updated
- Look for potential bugs or security issues

When requesting changes:
- Be respectful and constructive
- Explain why changes are needed
- Suggest improvements, not demands
- Approve once issues are resolved

## Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Docker version, etc.)

### Feature Requests
Include:
- Clear description of desired feature
- Use case and why it's needed
- Potential implementation approach
- Examples if applicable

## Communication

- **Issues**: Use GitHub Issues for bugs and features
- **Discussions**: Use GitHub Discussions for questions
- **Pull Requests**: Use PR comments for code discussion
- **Email**: For security issues, email security@aios.dev

## Development Tips

### Hot Reload
Services are configured for hot reload during development:
```bash
# Changes to code automatically reload
docker-compose up -d service_name
# Edit files, they'll auto-reload
```

### Quick Testing
```bash
# Test API endpoint quickly
curl -X GET http://localhost:8000/health

# Use Swagger UI
http://localhost:8000/docs
```

### Database Access
```bash
# Connect to PostgreSQL
psql -U aios_user -d aios_database -h localhost

# View tables
\dt

# Exit
\q
```

## FAQ

**Q: How do I set up a new environment?**
A: Follow "Setting Up Your Development Environment" above and use docker-compose.

**Q: How do I test my changes?**
A: Write tests in `backend/service_name/tests/` and run with `pytest`.

**Q: How do I handle database migrations?**
A: Update `database/schema.sql` and create Alembic migrations when ready.

**Q: Can I work on multiple features at once?**
A: Yes, use separate branches for each feature and manage them independently.

**Q: What if I need to add a new service?**
A: Create a new directory in `backend/`, add `main.py`, `Dockerfile`, and tests.

## Resources

- [ROADMAP.md](ROADMAP.md) - Implementation phases
- [README.md](README.md) - Project overview
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Directory structure
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- FastAPI Docs: https://fastapi.tiangolo.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Docker Docs: https://docs.docker.com/

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Create an issue or email support@aios.dev

**Thank you for contributing!** 🙏
