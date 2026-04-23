FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk update && apk upgrade --no-cache

RUN addgroup -S app && adduser -S app -G app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

USER app

HEALTHCHECK --interval=15s --timeout=5s --retries=5 CMD python -c "import os, redis; redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379')).ping()"

CMD ["python", "worker.py"]
