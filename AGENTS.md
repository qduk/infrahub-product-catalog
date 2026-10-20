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
- This repository is not connected to the instance as a Git repository. Infrahub does not run its transforms, generators or checks by itself. Run them with `infrahubctl`.

<!-- TODO: author the rest of the project instructions here. -->
