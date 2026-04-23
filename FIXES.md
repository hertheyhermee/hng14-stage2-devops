## FIXES

### Issue 1 - Broken Redis env lookup and client initialization
- File: `api/main.py`
- Lines: `8-12`
- Problem: Redis client was used before initialization and env lookup was incorrect (`os.get_env`), causing startup failures.
- Fix: Read `REDIS_URL` using `os.getenv("REDIS_URL", "redis://localhost:6379")`, initialize client with `redis.from_url(redis_url)`, and validate with `ping()` in guarded startup logic.
- Why this matters: The API must boot reliably in both local and container environments where Redis host is provided via environment variables.

### Issue 2 - Missing dotenv dependency for `uvicorn --env-file`
- File: `api/requirements.txt`
- Lines: `1-5`
- Problem: Running `uvicorn main:app --env-file .env` failed with `ModuleNotFoundError: No module named 'dotenv'`.
- Fix: Added `python-dotenv` to requirements.
- Why this matters: Environment-driven configuration is required by the task, and this command path is used during local verification and CI.

### Issue 3 - Worker hardcoded to localhost Redis
- File: `worker/worker.py`
- Line: `6`
- Problem: Worker used `redis.Redis(host="localhost", port=6379)`, which fails inside Docker because Redis is a separate service container.
- Fix: Switched to env-based connection: `redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))`.
- Why this matters: Service-to-service communication in Compose must use environment-driven config and container DNS names.

### Issue 4 - Frontend hardcoded API URL
- File: `frontend/app.js`
- Line: `6`
- Problem: API base URL was hardcoded to `http://localhost:8000`, which breaks when frontend runs in a container.
- Fix: Replaced with `process.env.API_URL || "http://localhost:8000"`.
- Why this matters: Frontend must be deployable across environments without code changes.

### Issue 5 - Incorrect Axios timeout placement
- File: `frontend/app.js`
- Line: `13`
- Problem: `timeout` was passed as request body in `axios.post`, so timeout was not actually applied.
- Fix: Changed call to `axios.post(url, {}, { timeout: 5000 })`.
- Why this matters: Prevents hanging API requests and improves service resilience during integration tests.