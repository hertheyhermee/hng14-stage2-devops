import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient

API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


class FakeRedis:
    def __init__(self):
        self.queues = {}
        self.hashes = {}

    def ping(self):
        return True

    def lpush(self, key, value):
        self.queues.setdefault(key, [])
        self.queues[key].insert(0, value)
        return len(self.queues[key])

    def hset(self, key, field, value):
        self.hashes.setdefault(key, {})
        self.hashes[key][field] = value
        return 1

    def hget(self, key, field):
        value = self.hashes.get(key, {}).get(field)
        if value is None:
            return None
        return value.encode()


def _build_client_with_fake_redis(monkeypatch):
    fake_redis = FakeRedis()

    if "main" in sys.modules:
        del sys.modules["main"]

    import redis as redis_lib

    monkeypatch.setattr(redis_lib, "from_url", lambda _: fake_redis)

    main = importlib.import_module("main")
    importlib.reload(main)

    return TestClient(main.app), fake_redis


def test_health_endpoint(monkeypatch):
    client, _ = _build_client_with_fake_redis(monkeypatch)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_queues_and_sets_status(monkeypatch):
    client, fake_redis = _build_client_with_fake_redis(monkeypatch)
    response = client.post("/jobs")
    payload = response.json()
    job_id = payload["job_id"]

    assert response.status_code == 200
    assert "job_id" in payload
    assert job_id in fake_redis.queues["job"]
    assert fake_redis.hashes[f"job:{job_id}"]["status"] == "queued"


def test_get_job_status_not_found(monkeypatch):
    client, _ = _build_client_with_fake_redis(monkeypatch)
    response = client.get("/jobs/missing-job")

    assert response.status_code == 200
    assert response.json() == {"error": "not found"}
