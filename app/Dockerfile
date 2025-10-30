# Étape 1 : base image
FROM python:3.10-slim

# Étape 2 : installer uv
RUN pip install --no-cache-dir uv

# Étape 3 : créer un cache volume pour uv
ENV UV_CACHE_DIR=/root/.cache/uv

WORKDIR /app

COPY requirements.txt .

RUN uv pip install -r requirements.txt --system

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
