---

description: "Task list for the public catalog web app"
---

# Tasks: Public Catalog Web App

**Input**: Design documents from `specs/005-catalog-web-app/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/api.md](./contracts/api.md),
[quickstart.md](./quickstart.md)

**Tests**: included for the service (validation and submission steps) and the web app (filters and
form validation), following research R7.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: the user story the task belongs to (US1 to US4)

## Conventions for every task

- Never commit a token or password. `frontend/api/.env` is ignored by Git.
- Test data goes on throwaway Infrahub branches. Close or delete them after each test.
- Do not push to GitHub without the user's go-ahead (task T030).

---

## Phase 1: Setup

- [X] T001 Create `frontend/api/` as a uv project (`pyproject.toml`, Python 3.13) with FastAPI,
  Uvicorn, Pydantic and infrahub-sdk, and a dev group with pytest and httpx; add
  `frontend/api/.env.example` listing `INFRAHUB_ADDRESS`, `INFRAHUB_API_TOKEN` and
  `CATALOG_CACHE_SECONDS`; add `frontend/api/.env`, `node_modules/` and `frontend/web/dist/` to
  `.gitignore`
- [X] T002 [P] Create `frontend/web/` as a Vite React TypeScript app with TanStack Query, React
  Hook Form, Zod and `@hookform/resolvers`, and Vitest with Testing Library; set the dev server proxy
  `/api` → `http://localhost:8200` in `frontend/web/vite.config.ts`
- [X] T003 Write `frontend/api/bootstrap_service_account.py`: using the admin token from the
  environment, upsert the permissions, role `Catalog submitter`, group `Catalog web service` and
  account `catalog-web` from research R1; set a random password, log in as the account, create an
  API token, and print the token once; run it and store the token in `frontend/api/.env`

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T004 Write `frontend/api/catalog_web/infrahub.py` (client from the environment) and
  `frontend/api/catalog_web/main.py` (FastAPI app with `GET /api/health`)
- [X] T005 Write `frontend/api/catalog_web/catalog.py`: one GraphQL query on `main` for blocks,
  publishers and products with every source and claim, reshaped to the response in
  `specs/005-catalog-web-app/data-model.md`, cached for `CATALOG_CACHE_SECONDS`; add
  `GET /api/catalog` (503 when Infrahub is unreachable); test it with a fake client in
  `frontend/api/tests/test_catalog.py`
- [X] T006 Run the service with the `catalog-web` token and confirm `GET /api/catalog` returns 6
  blocks, 46 publishers and 50 products
- [X] T007 Write `frontend/web/src/api.ts` with the response types and the catalog query hook

**Checkpoint**: the web app can load the catalog through the service.

---

## Phase 3: User Story 1 - Browse the catalog as a framework diagram (Priority: P1) 🎯 MVP

- [X] T008 [US1] Write `frontend/web/src/components/Diagram.tsx` and `Block.tsx`: the CSS grid
  layout from research R5, block colours, the products in each block marked full or partial and
  discontinued or acquired, "No products cover this block" when empty, and an Infrastructure footer
  bar; blocks are matched to positions by name, and any unknown block goes in an extra row
- [X] T009 [US1] Write `frontend/web/src/components/ProductDetails.tsx`: a panel with the product's
  publisher, description, home page, license model, status and claims, each fact with links to its
  sources, shown when a product is selected; all values rendered as text
- [X] T010 [US1] Write `frontend/web/src/App.tsx`, `main.tsx` and `styles.css` (dark background,
  responsive stacking under 900 pixels), and an "unavailable" message when the catalog fails to load

---

## Phase 4: User Story 2 - Filter the diagram (Priority: P1)

- [X] T011 [P] [US2] Write tests in `frontend/web/src/filters.test.ts`: defaults (active, both
  extents, all blocks); combinations of status and extent; a single block; reading and writing the
  page address; unknown values ignored
- [X] T012 [US2] Write `frontend/web/src/filters.ts` (filter state, applying filters to the catalog,
  page-address encoding from research R6) until the tests pass
- [X] T013 [US2] Write `frontend/web/src/components/Filters.tsx` (status and extent toggles, block
  selection, "Show all blocks") and connect the filters to the diagram and the page address; a block
  with no match says "No products match the filters"

---

## Phase 5: User Story 3 - Submit a new product (Priority: P2)

- [X] T014 [P] [US3] Write tests in `frontend/api/tests/test_submissions.py` for the validation
  model: every rule and limit in `specs/005-catalog-web-app/data-model.md`, including a status that
  is not active without a status source, a license model without a source, two claims on one
  block, unknown source keys, non-http URLs and over-long fields
- [X] T015 [US3] Write the Pydantic models in `frontend/api/catalog_web/submissions.py` until the
  tests pass
- [X] T016 [P] [US3] Write tests in `frontend/api/tests/test_submissions.py` for the submission
  steps with a fake client: existing sources and publishers are reused, new ones are created, the
  duplicate check returns 409, a failure after the branch exists deletes the branch, and the
  reference is returned
- [X] T017 [US3] Write the submission steps in `frontend/api/catalog_web/submissions.py` and
  `POST /api/submissions` in `main.py` until the tests pass
- [X] T018 [P] [US3] Write tests in `frontend/web/src/submit/schema.test.ts` for the form's Zod
  schema with the same rules and limits
- [X] T019 [US3] Write `frontend/web/src/submit/schema.ts` and
  `frontend/web/src/submit/SubmitForm.tsx`:
  - product fields;
  - an existing publisher picker or a new publisher;
  - a source list that every fact picks from;
  - claims added and removed per building block;
  - errors shown next to each field;
  - a confirmation with the reference.
  Add a "Submit a product" view to `App.tsx`.
- [X] T020 [US3] Run the integration test `frontend/api/tests/test_integration.py` (marked, run on
  demand): submit one product to the local instance through the service, confirm the branch,
  product, claims and proposed change exist and the product is not on `main`, then close the
  proposed change and delete the branch

---

## Phase 6: User Story 4 - Review a submission (Priority: P2)

- [X] T021 [US4] Submit a product through the web app, open the proposed change in Infrahub, and
  confirm the name "Submission: <publisher> <product>", the description that names the public form,
  and that the source check and report check passed
- [X] T022 [US4] Merge it, wait for the cache to expire, and confirm the product appears in the
  app; then remove it from `main` through a second proposed change, so the demo product does not stay
  in the catalog

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T023 [P] Write `frontend/README.md`: how to run both parts, the service account bootstrap,
  and the two go-live blockers (FR-019, FR-020)
- [X] T024 [P] Add `frontend/web` build and test commands, and confirm `npm run build` and
  `npm test` pass with no TypeScript errors
- [X] T025 Confirm that no Infrahub token, password or address other than `localhost` appears in
  any committed file under `frontend/`
- [X] T026 Confirm that submitted text containing `<script>` is shown as text in the app and in the
  product details
- [X] T027 Run quickstart rows 1 to 4 and record the results in
  `specs/005-catalog-web-app/quickstart.md`
- [ ] T028 Ask the user to open the app in a browser and confirm the layout, colours and filters
  match what they want (quickstart rows 1 to 3)
- [X] T029 Update `AGENTS.md` with a short "Web app" section that points to `frontend/README.md`
- [ ] T030 Commit on `005-catalog-web-app`, merge into `main`, and ask the user before pushing

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phases 3 and 4 (web) and Phase 5 (service and form).
- Phase 4 depends on Phase 3 (filters apply to the diagram).
- Phase 6 depends on Phase 5. Phase 7 depends on all.

## Parallel Opportunities

- T002 alongside T001; T011, T014, T016 and T018 are test files written before their code.
- T023 and T024 alongside T025 to T027.

## Implementation Strategy

1. Phases 1 to 3: the diagram shows the catalog.
2. Phase 4: filters.
3. Phase 5: the form and submissions.
4. Phases 6 and 7: review flow, checks, documentation and the user's look at the app.

## Notes from implementation

- T014 to T017: the service's submission code was written before its tests, not after. The tests
  cover every rule and step in the task descriptions and pass, but they did not fail first.
- T002: `@hookform/resolvers` could not be installed (peer dependency conflict in its version 6), so
  `src/submit/SubmitForm.tsx` connects the Zod rules to React Hook Form with a small resolver of its
  own.
- T020: the integration test is marked and runs only with `-m integration`, because it needs the
  running service and an admin token.
- T013: the filter controls are in `src/components/FilterBar.tsx`, not `Filters.tsx`.
- T028 (the user's look at the app in a browser) and T030 (push) are open until the user responds.
