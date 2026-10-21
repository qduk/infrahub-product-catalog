# Quickstart: Validate the Public Catalog Web App

**Feature**: [spec.md](./spec.md) | **Data model**: [data-model.md](./data-model.md) |
**Contract**: [contracts/api.md](./contracts/api.md)

## Prerequisites

- The local Infrahub instance is running with the catalog on `main`.
- The service account exists (`frontend/api/bootstrap_service_account.py`), and its token is in
  `frontend/api/.env`.
- `cd frontend/api && uv run uvicorn catalog_web.main:app --port 8200`, and
  `cd frontend/web && npm run dev`.

## Demo arc

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | Open the app | Six blocks in the framework layout, each listing active products marked full or partial. | ~30s | SC-002 |
| 2 | Find every product that fully covers Collector | Select Collector and "full" only; the list shows them. | ~30s | SC-001, SC-003 |
| 3 | Add "discontinued" to the status filter and copy the page address into a new tab | Skybox and System Initiative appear, marked discontinued; the new tab shows the same view. | ~45s | SC-003 |
| 4 | Submit an incomplete form | Each missing field and source is named; nothing is created in Infrahub. | ~60s | SC-005 |
| 5 | Submit a complete product with three claims | A confirmation with a reference; a branch and a proposed change exist in Infrahub; the public view does not show the product. | ~5m | SC-004, SC-005 |
| 6 | Open the proposed change in Infrahub and merge it, then reload the app after the cache expires | The source check passed without edits; the product appears in the app. | ~2m | SC-005, SC-006 |

Total time: about 9 minutes 45 seconds.

## Results

Run on 2026-10-21 with the service on port 8200 (the `catalog-web` account) and the web app on
port 5173.

| # | Outcome |
|---|---|
| 1 | Data checked, layout waiting for the user. The service returned 6 blocks, 46 publishers and 50 products through the web app's `/api` proxy. The production build has no TypeScript errors. The layout in a browser is task T028. |
| 2 | Filter logic checked by tests (`src/filters.test.ts`, 6 tests): a single block, extent and status combine. The browser check is task T028. |
| 3 | Page-address encoding checked by tests; the browser check is task T028. |
| 4 | Form rules checked by 9 tests in `src/submit/schema.test.ts` and 21 service tests in `frontend/api/tests/test_submissions.py`. |
| 5 | Pass. A submission through the web app's `/api` proxy returned `201` with the reference `submission-20261021-03e24d`, and created the proposed change "Submission: OpsMill Review Flow Demo". The integration test confirmed the product was not on `main` before review, and that an existing source was reused rather than copied. |
| 6 | Pass. All four checks on the proposed change passed in 15 seconds without edits (Data Integrity, Schema Integrity, the report artifact, `catalog_source_check`). After the merge, the product appeared in the app. A second proposed change then removed the demo product and its sources; `main` has 50 products again. |

Security checks:
- A test confirms that text with `<script>` and `<img onerror>` is shown as text in product details.
- No file to be committed contains a token or password.
- The service has FastAPI's interactive API pages switched off (`/docs` returns 404).
