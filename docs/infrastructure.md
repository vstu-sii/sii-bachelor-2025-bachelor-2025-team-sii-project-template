# Infrastructure & Operations – Notes
- Compose stacks:
  - infra/docker-compose.dev.yml → db, api, frontend, jupyter
  - monitoring/docker-compose.yml → prometheus, grafana
- Inside Docker network, connect to DB as `db:5432`. From host: `localhost:5432`.
