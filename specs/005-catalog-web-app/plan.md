# Implementation Plan: Public Catalog Web App

**Branch**: `005-catalog-web-app` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-catalog-web-app/spec.md`

## Summary

A public web app shows the catalog as the Network Automation Framework diagram, with filters by
status, extent and building block, and lets anyone submit a product through a form. It has two
parts:
- a React app in `frontend/web/`;
- a small Python service in `frontend/api/`, the only part that talks to Infrahub.

The service reads the catalog from `main` and turns each submission into an Infrahub branch and a
proposed change, using a service account with limited permissions. A test on the local instance
found that the account can merge its own proposed change, because opening one needs
`edit_default_branch`. The user accepted this for development, and it blocks going live (spec
FR-020, [research.md](./research.md) R1).

## Technical Context

**Language/Version**:
- `frontend/web`: TypeScript 5 with React 19, built with Vite.
- `frontend/api`: Python 3.13 with FastAPI.

**Primary Dependencies**:
- `frontend/web`: TanStack Query, React Hook Form, Zod.
- `frontend/api`: FastAPI, Uvicorn, Pydantic, infrahub-sdk 1.23.2.

**Storage**: none of its own. Infrahub is the only store.

**Testing**:
- pytest for the service, with a fake Infrahub client, plus one integration test against the local
  instance.
- Vitest and Testing Library for the web app.
- A browser walkthrough ([quickstart.md](./quickstart.md)).

**Target Platform**: current desktop and mobile browsers. The service runs anywhere Python 3.13
runs, next to Infrahub.

**Project Type**: web application: frontend plus a backend service.

**Performance Goals**: filter changes under 1 second (SC-003); catalog response cached for 60
seconds.

**Constraints**:
- No Infrahub credential in the browser (FR-018).
- Submissions are atomic: no partial branch is left after a failure (FR-012).
- Spam protection (FR-019) and the merge-permission gap (FR-020) block going live.

**Scale/Scope**: about 50 products and 100 claims today; two API operations; one page with a form.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | No schema change. The app uses only fields defined in `schemas/catalog.yml`. | Pass |
| II. Validation on the local instance | The service and app run against the local instance; submissions arrive as proposed changes, where the source check runs, and are merged only through them. | Pass |
| III. Sourced product records | The form requires a source for every fact, with the same rules as the source check (FR-010, SC-006). | Pass |
| IV. Framework terms recorded as data | Building blocks come from the catalog; only the layout positions are fixed in the app, keyed by block name, and an unknown block is shown in an extra row. | Pass |
| V. Infrahub conventions | The schemas skill was loaded; the service uses the SDK with branch-first writes and proposed changes. | Pass |

Post-design re-check: all gates pass. FR-020 is a security limit of Infrahub 1.11.8, accepted by
the user for development, not a constitution violation.

## Project Structure

### Documentation (this feature)

```text
specs/005-catalog-web-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
frontend/
├── README.md                         # how to run both parts; go-live blockers
├── api/
│   ├── pyproject.toml                # its own uv project
│   ├── .env.example                  # variable names only
│   ├── bootstrap_service_account.py  # creates the role, group and account; prints a token
│   ├── catalog_web/
│   │   ├── main.py                   # FastAPI app and routes
│   │   ├── catalog.py                # catalog query and cache
│   │   ├── submissions.py            # validation models and the submission steps
│   │   └── infrahub.py               # client setup
│   └── tests/
└── web/
    ├── package.json
    ├── vite.config.ts                # /api proxy to port 8200
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts                    # catalog and submission calls, types
        ├── filters.ts                # filter logic and page-address encoding
        ├── components/               # Diagram, Block, ProductCard, ProductDetails, Filters
        ├── submit/                   # SubmitForm and its validation schema
        └── styles.css
```

**Structure Decision**: two parts under `frontend/`, as the user asked, because the credential must
stay on the server.

## Complexity Tracking

No constitution violations to justify.
