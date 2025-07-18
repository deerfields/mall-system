# --- Base image for dependencies ---
FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --- Development image ---
FROM base AS dev
ENV ENV=development
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Production image ---
FROM base AS prod
ENV ENV=production
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 