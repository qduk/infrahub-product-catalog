# AGENTS.md

Portable, vendor-neutral instructions for AI coding agents working in this repository.
This file is the **single source of truth**; each agent adapter (CLAUDE.md, .codex/)
routes back to it.

## Local Infrahub instance

This repository runs its own Infrahub instance with Docker Compose.

- `docker-compose.yml` is the file from <https://infrahub.opsmill.io>, unchanged. It sets the Infrahub version (1.11.8).
- `docker-compose.override.yml` sets the project name `infrahub-product-catalog` and publishes only the Infrahub web server, on port 8100. Set `INFRAHUB_PORT` to use another port. Other Infrahub instances on this machine can then keep port 8000.
- Start the instance with `docker compose up -d`, and stop it with `docker compose stop`. Do not pass `-p infrahub`: other stacks on this machine use that project name.

## Running infrahubctl

`infrahubctl` comes from the `infrahub-sdk[ctl]` package in the `dev` dependency group. Always run it through uv: `uv run infrahubctl <command>`. It is not installed on the PATH, so a bare `infrahubctl` command fails. This includes the `infrahubctl info` check in the Spec Kit Infrahub routing steps: run `uv run infrahubctl info` there.

- `infrahubctl.toml` sets the address to `http://localhost:8100`.
- Commands that change data need an API token. For the local instance, use the default admin token from `docker-compose.yml`: `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec`.
- Load files from this working copy with commands such as `uv run infrahubctl schema load schemas/`, `uv run infrahubctl menu load`, `uv run infrahubctl object load`, `uv run infrahubctl transform <name>`, `uv run infrahubctl render <name>`, `uv run infrahubctl generator <name>` and `uv run infrahubctl check <name>`.
- Load schema and object files on an Infrahub branch, for example `uv run infrahubctl schema load --branch <branch> schemas/` and `uv run infrahubctl object load --branch <branch> objects/`. Merge the branch into `main` through a proposed change, never with a direct branch merge, so that the source check runs.

## Git repository connection

The instance reads this repository from GitHub as a read-only repository (`CoreReadOnlyRepository`, location `https://github.com/qduk/infrahub-product-catalog.git`, ref `main`). The registration is in `bootstrap/repository.yml`. See `dev/adr/0002-connect-repository-read-only.md`.

- `.infrahub.yml` lists only checks and their queries. Infrahub runs `catalog_source_check` on every proposed change, and a failed check blocks the merge.
- Schemas and object files are not in `.infrahub.yml`, so the repository import never writes them to `main`. Load them with `infrahubctl` as described above.
- Infrahub reads only what is pushed to `main` on GitHub. After a change to `checks/`, `queries/` or `.infrahub.yml` is pushed, open the repository in the Infrahub web interface and run **Import latest commit**.
- To run the check by hand before opening a proposed change: `uv run infrahubctl check catalog_source_check --branch <branch> --format-json`. Without `--format-json`, sources that are due for review are not shown when the check passes.
- Run the check's tests with `uv run pytest tests/`.

## Web app

`frontend/` holds the public catalog web app: a React app in `frontend/web/` and a Python service in
`frontend/api/` that is the only part talking to Infrahub. See `frontend/README.md` for how to run
it and for the two problems that must be fixed before it is reachable from the internet. Never
commit `frontend/api/.env`: it holds the service account token.

<!-- TODO: author the rest of the project instructions here. -->
