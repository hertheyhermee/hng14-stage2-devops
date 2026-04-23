from fastapi import FastAPI
import redis
import uuid
import os

app = FastAPI()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    r = redis.from_url(redis_url)
    r.ping()
except Exception as e:
    raise Exception(f"Failed to connect to Redis: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        return {"error": "not found"}
    return {"job_id": job_id, "status": status.decode()}
