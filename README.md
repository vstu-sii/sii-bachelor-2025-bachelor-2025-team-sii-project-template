# Development Environment (Docker Compose) — Updated

Run everything locally with **one command**, keeping your original goal.
Services included:
- Frontend: placeholder (nginx) on ${FRONTEND_PORT:-3000}
- Backend: placeholder (python http.server) on ${API_PORT:-8000}
- Database: PostgreSQL on host 5432 (service `db` internally)
- Jupyter Lab: for experiments on ${JUPYTER_PORT:-8888}
- (Optional) Monitoring: Prometheus + Grafana

## Quickstart
```powershell
copy .env.example .env
cd infra
docker compose -f .\docker-compose.dev.yml up -d
```
Then (optional):
```powershell
cd ..\monitoring
docker compose up -d
```

## Replace placeholders with real apps
Switch `image:` to `build:` and point to your `frontend/` and `backend/` dirs with Dockerfiles.

## Troubleshooting
- Port busy → change left side only: e.g., `5433:5432`, `8001:8000`, `3002:80`.
- Windows paths with spaces/Arabic → use quotes.
