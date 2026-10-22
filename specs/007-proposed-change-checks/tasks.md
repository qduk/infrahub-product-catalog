---

description: "Task list for the proposed change checks for catalog submissions"
---

# Tasks: Proposed Change Checks for Catalog Submissions

**Input**: Design documents from `specs/007-proposed-change-checks/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/check-results.md](./contracts/check-results.md),
[quickstart.md](./quickstart.md)

**Tests**: included, because the success criteria count findings in test data (SC-001 to SC-003).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Write `queries/catalog_records.gql` with the fields in data-model.md, and register it
  under `queries:` in `.infrahub.yml`
- [X] T002 Run the query on `main` with `uv run infrahubctl graphql` or the GraphQL endpoint, and
  confirm that it returns every record with no error

## Phase 2: Foundational

- [X] T003 Write the shared helpers in `checks/catalog_record_checks.py`: name and link
  normalisation (research.md section 5), record labels, and pair grouping
- [X] T004 Write the test fixture builder in `tests/test_catalog_record_checks.py`, which produces
  query results in the shape of `catalog_records`, plus tests for normalisation

## Phase 3: User Story 1 - Block a submission that changes existing records (Priority: P1)

**Goal**: `catalog_submission_check` fails when a submission branch deletes or changes a record on
`main`, or adds a building block.

**Independent Test**: quickstart rows 3 and 7.

- [X] T005 [US1] Add tests to `tests/test_catalog_record_checks.py` for the acceptance scenarios
  of User Story 1: only additions pass; links from new records to existing records pass; a changed
  fact, a changed source list, a moved product, a deleted record and an added building block each
  fail with the contract message; a branch without the `submission-` prefix passes with the INFO
  message
- [X] T006 [US1] Write `CatalogSubmissionCheck` in `checks/catalog_record_checks.py`: in an async
  `validate()`, run `catalog_records` on `main` and compare it with the branch's data
- [X] T007 [US1] Register `catalog_submission_check` under `check_definitions` in `.infrahub.yml`

## Phase 4: User Story 2 - Catch near-duplicate names and links (Priority: P1)

**Goal**: `catalog_duplicate_check` fails once for each near-duplicate pair.

**Independent Test**: quickstart row 4.

- [X] T008 [US2] Add tests for the acceptance scenarios of User Story 2, including same-named
  products of different publishers and names made only of punctuation
- [X] T009 [US2] Write `CatalogDuplicateCheck` in `checks/catalog_record_checks.py` and register
  `catalog_duplicate_check` in `.infrahub.yml`

## Phase 5: User Story 3 - Warn about a product that covers no building block (Priority: P2)

**Goal**: `catalog_coverage_check` lists products with no claim as warnings.

**Independent Test**: quickstart row 5.

- [X] T010 [US3] Add tests for the acceptance scenarios of User Story 3
- [X] T011 [US3] Write `CatalogCoverageCheck` in `checks/catalog_record_checks.py` and register
  `catalog_coverage_check` in `.infrahub.yml`

## Phase 6: User Story 4 - Block a source that supports nothing (Priority: P2)

**Goal**: `catalog_unused_source_check` fails for each source that supports nothing.

**Independent Test**: quickstart row 4.

- [X] T012 [US4] Add tests for the acceptance scenarios of User Story 4
- [X] T013 [US4] Write `CatalogUnusedSourceCheck` in `checks/catalog_record_checks.py` and register
  `catalog_unused_source_check` in `.infrahub.yml`

## Phase 7: Validation on the local instance and polish

- [X] T014 Run `uv run pytest tests/` (ruff is not configured in this repository)
- [X] T015 Run each new check by hand on `main` (quickstart row 2). Correct any finding on `main`
  through a branch and a proposed change before pushing
- [X] T016 Run quickstart rows 3 to 5 on test branches with `uv run infrahubctl check`
- [X] T017 Update the list of checks in `AGENTS.md`
- [ ] T018 Commit, merge into `main`, and ask the user before pushing. After the push, run
  **Import latest commit** and quickstart rows 6 to 8

## Dependencies

- T001 → T002 → T003 → T004 → every user story phase.
- User stories 1 to 4 are independent of each other once Phase 2 is done. They all edit
  `checks/catalog_record_checks.py` and `.infrahub.yml`, so their implementation tasks run in
  order.
- Phase 7 needs every story.

## Parallel Opportunities

- None. Every task edits `checks/catalog_record_checks.py`, `tests/test_catalog_record_checks.py`
  or `.infrahub.yml`, so the tasks run one after another.

## Implementation Strategy

- MVP: Phases 1 to 3 (the submission check), because it guards the catalog against submissions
  that change existing records.
- Then add User Stories 2, 3 and 4, each tested on its own.
