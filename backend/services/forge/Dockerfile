FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/backend/services/forge

ENV PYTHONPATH=/app

# No specific runtime as Forge exists dynamically as an orchestrator dependency 
# However, providing standard placeholder access or Celery endpoint structurally mapping 
CMD ["tail", "-f", "/dev/null"]
