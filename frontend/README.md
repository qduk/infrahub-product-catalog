# Catalog web app

A public web app that shows the catalog as the Network Automation Framework diagram and lets anyone
submit a product for review. Spec: [specs/005-catalog-web-app](../specs/005-catalog-web-app/spec.md).

## Not ready for the internet

Do not make this app reachable from the internet until both of these are resolved:

1. **Spam protection** (spec FR-019): add rate limits and human verification to
   `POST /api/submissions`. Not designed yet.
2. **The service account can merge its own proposed changes** (spec FR-020): on Infrahub 1.11.8,
   opening a proposed change needs `edit_default_branch`, and an account with it could merge
   proposed changes even with an explicit deny on `merge_proposed_change`. Wait for an Infrahub fix,
   or move proposed change creation to an internal process that is not reachable from the
   internet.

Also replace Infrahub's default admin password and API token before any deployment. They are
published in Infrahub's `docker-compose.yml`.

## Parts

| Part | What it does |
|------|--------------|
| `web/` | React and TypeScript app, built with Vite. Talks only to `/api`. |
| `api/` | Python service (FastAPI and the Infrahub SDK). The only part that talks to Infrahub. It offers `GET /api/catalog` (catalog on `main`, cached 60 seconds) and `POST /api/submissions` (creates a branch and a proposed change). |

The browser never receives an Infrahub token. Visitors see only data from `main`.

## Run locally

1. Start the local Infrahub instance from the repository root: `docker compose up -d`.
2. Create the service account once, with the admin token:

   ```bash
   cd frontend/api
   INFRAHUB_ADMIN_TOKEN=<admin token> uv run python bootstrap_service_account.py
   cp .env.example .env    # then paste the printed INFRAHUB_API_TOKEN into .env
   ```

   Running the script again resets the account's password and creates a new token.
3. Start the service on port 8200:

   ```bash
   cd frontend/api
   set -a; . ./.env; set +a
   uv run uvicorn catalog_web.main:app --port 8200
   ```

4. Start the web app on port 5173. Vite forwards `/api` to port 8200:

   ```bash
   cd frontend/web
   npm install
   npm run dev
   ```

5. Open <http://localhost:5173>.

## Tests

| Command | Covers |
|---------|--------|
| `cd frontend/api && uv run pytest` | Submission rules and steps, catalog reshaping (no Infrahub needed) |
| `cd frontend/api && INFRAHUB_ADMIN_TOKEN=<admin token> uv run pytest -m integration` | One real submission against the local instance, cleaned up afterwards; needs the service running |
| `cd frontend/web && npm test` | Filters, form rules, plain-text rendering |
| `cd frontend/web && npm run build` | Type check and production build |

## Reviewing submissions

Each submission is an Infrahub branch named `submission-<date>-<code>` with a proposed change named
"Submission: <publisher> <product>". The visitor gets the branch name as their reference. Check
each fact against its source, then merge the proposed change or close it. Delete the branch after
closing.

## Logos

Product logos are files in `web/public/logos/`, listed in `web/src/graph/logos.json` with the page each
logo came from (`source_page`), the address it was downloaded from (`file_url`) and the tile colour it
needs on the dark page (`tile`: `light` for dark logos, `dark` for white logos). A product without an
entry shows its initials.

To add a logo:

1. Take it from the publisher's own press kit, repository or website, not from logo aggregator sites.
2. Save it as `web/public/logos/<slug>.<svg|png|webp>`. The slug is the product's full name in lower
   case, with other characters replaced by `-` (see `slugify` in `web/src/graph/logos.ts`).
3. Add an entry to `logos.json` with its source page.
4. Run `npm test` in `web/`: it fails if a file has no manifest entry, an entry has no source, or an
   SVG contains scripts, event handlers, embedded content or external links.

Logos are shown only with `<img>`, and the page states that names and logos are trademarks of their
owners. Visitors cannot upload logos.
