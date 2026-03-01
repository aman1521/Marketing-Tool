FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and install postgres dev dependencies for psycopg2 if migrating sync scripts later
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy logic structure
COPY . /app/backend/services/atlas

# Allow top-level package resolution execution wrapper for python
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.services.atlas.main:app", "--host", "0.0.0.0", "--port", "8003"]
