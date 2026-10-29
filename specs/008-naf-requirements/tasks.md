---

description: "Task list for framework requirements and coverage assessments"
---

# Tasks: Framework Requirements and Coverage Assessments

**Input**: Design documents from `specs/008-naf-requirements/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/catalog-api.md](./contracts/catalog-api.md),
[quickstart.md](./quickstart.md)

**Tests**: included for the extent rule, the verdict check and the web app card.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Save the framework page and extract the 34 requirements word for word in
  `dev/knowledge/naf-requirements-2026-10-23/` (`extract_requirements.py`, `requirements.json`)
- [X] T002 Build one research input per block in `dev/knowledge/naf-requirements-2026-10-23/research-input/`
  and start the research agents (US4)

## Phase 2: Foundational (schema)

- [X] T003 Add `CatalogRequirement` and `CatalogRequirementVerdict`, the claim's computed `name` and
  `verdicts`, the inverse relationships, and `extent` with `state: absent` in `schemas/catalog.yml`;
  run `uv run infrahubctl schema check`
- [X] T004 Add the requirements document to `objects/01_building_blocks.yml` and remove `extent` from
  `objects/04_products.yml`
- [X] T005 Load schema and objects on a local branch and confirm every claim has a `name`

## Phase 3: User Story 1 and 2 - requirements, verdicts and the computed extent (P1)

- [X] T006 [US2] Write `checks/catalog_verdict_check.py`, `queries/catalog_verdict_check.gql` and tests;
  register them in `.infrahub.yml`
- [X] T007 [US2] Update `queries/catalog_records.gql` and `checks/catalog_record_checks.py`: requirements
  and verdicts in the submission check, verdicts count as use in the unused source check, no extent
- [X] T008 [US2] Compute the extent in `transforms/catalog_report.py` with `queries/catalog_report.gql`;
  update fixtures and tests

## Phase 4: User Story 3 - the web app shows requirements (P1)

- [X] T009 [US3] Service: requirements, verdicts, computed `extent` and `assessed` in
  `frontend/api/catalog_web/catalog.py`, with tests
- [X] T010 [US3] Web app: types in `src/api.ts`, requirements section in `components/ProductDetails.tsx`
  (shortfalls first, MUST warning, not assessed), with tests

## Phase 5: User Story 5 - submissions without an extent (P2)

- [X] T011 [US5] Remove the extent from the form (`submit/SubmitForm.tsx`, `submit/schema.ts`) and the
  service (`submissions.py`), accepting and ignoring an old `extent` field; update tests

## Phase 6: User Story 4 - assess and approve the 97 claims (P2)

- [X] T012 [US4] Merge the research outputs, validate them (one verdict per claim and requirement,
  sources), compute before and after extents, and publish a review page for the user
- [X] T013 [US4] After approval, generate `objects/06_requirement_verdicts.yml` (and any new sources in
  `objects/02_sources.yml`)

## Phase 7: Validation and rollout

- [X] T014 Load everything on a local branch, open a proposed change, confirm all checks pass, merge
- [X] T015 Run the quickstart walkthrough; update `AGENTS.md`, `frontend/README.md` and
  `dev/guides/record-a-product.md`
- [X] T016 Commit and merge; ask the user before pushing and before updating the GCP beta

## Dependencies

- T003 → T004 → T005 → everything else. T012 needs the research agents. T013 needs the user's approval.
- T006 to T011 can be written while the research runs.
