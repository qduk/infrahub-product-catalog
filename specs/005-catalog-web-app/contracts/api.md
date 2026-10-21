# Contract: Catalog Web Service API

Base path `/api`. JSON only. No authentication, so the service exposes nothing else.

| Method | Path | Purpose | Responses |
|--------|------|---------|-----------|
| GET | `/api/catalog` | The catalog on `main` ([data-model.md](../data-model.md)) | `200`, `503` when Infrahub is unreachable |
| POST | `/api/submissions` | Submit a product | `201`, `409`, `422`, `502`, `503` |
| GET | `/api/health` | Liveness for deployment | `200` |

Configuration (environment variables, never committed):

| Variable | Meaning |
|----------|---------|
| `INFRAHUB_ADDRESS` | Infrahub URL, `http://localhost:8100` in development |
| `INFRAHUB_API_TOKEN` | The `catalog-web` service account token |
| `CATALOG_CACHE_SECONDS` | Catalog cache lifetime, default 60 |
