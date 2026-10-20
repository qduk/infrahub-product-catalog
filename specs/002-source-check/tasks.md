---

description: "Task list for the source check on catalog changes"
---

# Tasks: Source Check for Catalog Changes

**Input**: Design documents from `specs/002-source-check/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/check-results.md](./contracts/check-results.md),
[quickstart.md](./quickstart.md)

**Tests**: included. The checks skill requires tests for every check, constitution Principle V
requires the skills' conventions, and research R6 defines the tests.

**Organization**: tasks are grouped by user story. Phase 5 connects the repository so that
Infrahub runs the check on proposed changes (FR-009). Both stories depend on it for that, but each
story can be checked by hand before it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: the user story the task belongs to (US1 or US2)

## Conventions for every task

- Read the `infrahub-managing-checks` skill before editing `checks/`, `queries/` or `tests/`
  (constitution Principle V).
- Run `infrahubctl` through uv. Set
  `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec` before any command that changes
  data.
- Test data goes on throwaway Infrahub branches, never on `main`. Delete each test branch when
  the task is done.
- Do not push to GitHub without the user's go-ahead in the same session (task T024).
- Report every failed command with its output. Do not mark a task done after a failure.

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Add `pytest` to the `dev` dependency group with `uv add --group dev pytest`, which
  updates `pyproject.toml` and `uv.lock`, then confirm `uv run pytest --version` works
- [X] T002 Create the directories `checks/`, `queries/`, `tests/fixtures/` and `bootstrap/` at
  the repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the query, the check class with no rules yet, and its registration. Both stories add
rules to this class.

**⚠️ CRITICAL**: no user story work can begin until this phase is complete.

- [X] T003 Write `queries/catalog_source_check.gql` with the query `catalog_source_check`, which
  selects, for every `CatalogProduct`: `id`, `__typename`, `full_name { value }`,
  `license_model { value }` and `license_model_sources { count }`; and for every `CatalogSource`:
  `id`, `__typename`, `title { value }`, `url { value }` and `last_checked { value }`
- [X] T004 Write `checks/catalog_source_check.py` with class `CatalogSourceCheck(InfrahubCheck)`,
  `query = "catalog_source_check"`, and a `validate(self, data)` that reads
  `data["CatalogProduct"]["edges"]` and `data["CatalogSource"]["edges"]` and logs nothing yet
- [X] T005 Replace `.infrahub.yml` with the content given in
  `specs/002-source-check/contracts/check-results.md`, keeping only `queries` and
  `check_definitions`, with no `query:` key under `check_definitions`
- [X] T006 Write `tests/test_checks.yml` (`version: "1.0"`, `infrahub_tests:`) with resource
  `Check`, resource_name `catalog_source_check` and a `check-smoke` test, then run
  `uv run pytest tests/` and `uv run infrahubctl check --list`, and confirm the smoke test passes
  and the check is listed with target `-global-`

**Checkpoint**: the check loads and runs, and reports nothing.

---

## Phase 3: User Story 1 - Find a license model with no source (Priority: P1) 🎯 MVP

**Goal**: a product with a license model and no license model source fails the check, with a
message that names the product and says what to do.

**Independent Test**: on a throwaway Infrahub branch, add such a product, run the check by hand,
and confirm it fails and names the product.

### Tests for User Story 1

> Write these tests first and confirm they fail before adding the rule in T010.

- [X] T007 [P] [US1] Write the fixture `tests/fixtures/license_model_missing_source/input.json`: a
  query result in the shape of `queries/catalog_source_check.gql` with one product that has
  `license_model` `commercial` and `license_model_sources.count` 0, and one source with
  `last_checked` `2026-10-20T00:00:00Z` (once this date is more than 6 months old, the source is
  only reported as information, so the expected result does not change)
- [X] T008 [P] [US1] Write the fixtures
  `tests/fixtures/license_model_with_source/input.json` (license model `open_source`, count 1) and
  `tests/fixtures/license_model_empty/input.json` (license model `null`, count 0), each with the
  same single source as T007
- [X] T009 [US1] Add three `check-unit-process` tests to `tests/test_checks.yml`: the T007
  fixture with `expect: FAIL`, and both T008 fixtures with `expect: PASS`; run
  `uv run pytest tests/` and confirm the FAIL test does not yet pass

### Implementation for User Story 1

- [X] T010 [US1] In `checks/catalog_source_check.py`, for each product whose
  `license_model.value` is set and whose `license_model_sources.count` is 0, call `log_error` with
  the message
  `<full name>: the license model has no source. Add a license model source or remove the license model.`
  and the product's `id` and `__typename`, as given in
  `specs/002-source-check/contracts/check-results.md`
- [X] T011 [US1] Run `uv run pytest tests/` and confirm all tests pass
- [X] T012 [US1] Create the Infrahub branch `test-us1`, add a `CatalogProduct` with a license
  model and no license model source (publisher OpsMill, the existing source
  `https://docs.infrahub.app/overview` for publisher and description), run
  `uv run infrahubctl check catalog_source_check --branch test-us1 --format-json`, and confirm the
  exit status is 1 and the error names the product (spec User Story 1, scenarios 1 and 4); then
  run the check with `--branch main` and confirm it passes (scenarios 2 and 3), and delete
  `test-us1`; record the output in a "Results" section at the end of
  `specs/002-source-check/quickstart.md`

**Checkpoint**: User Story 1 works when the check is run by hand.

---

## Phase 4: User Story 2 - Find sources that are due for review (Priority: P2)

**Goal**: sources last checked more than 6 months ago are listed without blocking, and a
last-checked date in the future fails the check.

**Independent Test**: on a throwaway Infrahub branch, set one source's date back more than 6
months and another into the future, run the check by hand, and confirm the old one is listed as
information and the future one as an error.

### Tests for User Story 2

> Write these tests first and confirm the FAIL test fails before adding the rules in T016.

- [X] T013 [P] [US2] Write the fixture `tests/fixtures/source_old/input.json`: one product with
  license model `null`, and one source with `last_checked` `2000-01-01T00:00:00Z` (research R6)
- [X] T014 [P] [US2] Write the fixture `tests/fixtures/source_future/input.json`: one product with
  license model `null`, and one source with `last_checked` `2099-01-01T00:00:00Z`
- [X] T015 [US2] Add two `check-unit-process` tests to `tests/test_checks.yml`: `source_old` with
  `expect: PASS` (information only) and `source_future` with `expect: FAIL`; run
  `uv run pytest tests/` and confirm `source_future` does not yet pass

### Implementation for User Story 2

- [X] T016 [US2] In `checks/catalog_source_check.py`:
  - Add `REVIEW_AGE_MONTHS = 6` and a function that returns the same day a given number of
    calendar months earlier, using the last day of the month when that day does not exist.
  - For each source, parse `last_checked` and take its UTC date. Compare it with today's UTC date.
  - Call `log_error` when the date is later than today, and `log_info` when it is earlier than
    the cutoff. Use the exact messages in `specs/002-source-check/contracts/check-results.md`, with
    the source's `id` and `__typename`.
  - Report nothing for a source dated exactly on the cutoff or later.
- [X] T017 [US2] Run `uv run pytest tests/` and confirm all tests pass
- [X] T018 [US2] Create the Infrahub branch `test-us2`. Set one source's `last_checked` to
  today's date minus 6 months minus 1 day, another to exactly today minus 6 months, and a third to
  2099-01-01. Run
  `uv run infrahubctl check catalog_source_check --branch test-us2 --format-json` and confirm:
  - the first source is listed at level `INFO`;
  - the second is not listed;
  - the third is listed at level `ERROR`, and the exit status is 1.
  Reset the third date to today, run again, and confirm the check passes with the first source
  still listed (spec User Story 2, scenarios 1 to 3). Delete `test-us2`, and record the output in
  the "Results" section of `specs/002-source-check/quickstart.md`.

**Checkpoint**: both user stories work when the check is run by hand.

---

## Phase 5: Connect the repository so the check runs on proposed changes (FR-009)

**Purpose**: Infrahub runs the check by itself on every proposed change. This phase changes how
the instance is set up, so it also updates the governing documents.

- [X] T019 [P] Write `bootstrap/repository.yml` with the `CoreReadOnlyRepository` entry given in
  `specs/002-source-check/contracts/check-results.md` (name `infrahub-product-catalog`, location
  `https://github.com/qduk/infrahub-product-catalog.git`, ref `main`, no credential)
- [X] T020 [P] Update `AGENTS.md`:
  - Replace the statement that the repository is not connected with a description of the
    read-only connection.
  - Say that schemas and object files are still loaded with `infrahubctl` on an Infrahub branch
    and merged through a proposed change.
  - Say that after a change to `checks/` or `queries/` is pushed to `main`, a maintainer runs
    **Import latest commit** on the repository.
  - Add the by-hand check command with `--format-json`.
- [X] T021 [P] Write `dev/adr/0002-connect-repository-read-only.md` in MADR format for research
  R1 and R2 (read-only repository; `.infrahub.yml` lists only the check), linking to
  `specs/002-source-check/research.md`
- [X] T022 [P] Update `dev/guides/record-a-product.md`: merge through a proposed change (never a
  direct branch merge, research R3), and before opening it, run
  `uv run infrahubctl check catalog_source_check --branch <branch> --format-json`
- [X] T023 Run `/speckit-constitution` to amend Principle II in
  `.specify/memory/constitution.md` from 1.0.0 to 1.1.0. The amendment says checks also run on
  every proposed change through the read-only repository connection, and keeps the requirement to
  validate on the local instance (research R8).
- [X] T024 Commit all work on the Git branch `002-source-check`, merge it into `main` with
  `git merge --ff-only`, then ask the user for the go-ahead to push `main` to
  `origin` (`git@github.com:qduk/infrahub-product-catalog.git`); push only after they agree,
  and stop here if they do not
- [X] T025 Register the repository with
  `uv run infrahubctl object load bootstrap/repository.yml`. If the import fails with a uniqueness
  error, run `docker compose up -d --scale task-worker=1`, delete the failed registration, load
  the file again and then run `docker compose up -d` to restore two workers (research R7). Confirm
  that the repository reaches a synced state and that `catalog_source_check` is listed under the
  instance's check definitions, and record the result in `specs/002-source-check/quickstart.md`.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T026 Run every row of the demo arc in `specs/002-source-check/quickstart.md` on the
  Infrahub branch `demo-source-check`, and record the outcome and time of each row in its
  "Results" section. Row 4 settles the open question in research R1. If Infrahub does not run the
  check on the proposed change, stop and report this to the user with the proposed change's
  check output; do not mark the feature done.
- [X] T027 Confirm that `main` on the local instance is unchanged after the arc: no test products
  remain, and every source's last-checked date is still 2026-10-20 (use
  `uv run infrahubctl check catalog_source_check --branch main --format-json`, which should pass
  and list nothing)
- [X] T028 Mark the completed tasks in `specs/002-source-check/tasks.md` and record any task
  left open, with the reason, under it

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup.
- **User Story 1 (Phase 3)** and **User Story 2 (Phase 4)**: depend on Phase 2. They edit the
  same files (`checks/catalog_source_check.py` and `tests/test_checks.yml`), so run them one after
  the other, US1 first.
- **Phase 5**: T019 to T022 can start after Phase 2. T023 can start at any time. T024 needs both
  stories and T019 to T023. T025 needs T024.
- **Polish (Phase 6)**: needs T025.

### Task order inside the phases

- T003 → T004 → T005 → T006.
- (T007 and T008 in parallel) → T009 → T010 → T011 → T012.
- (T013 and T014 in parallel) → T015 → T016 → T017 → T018.
- (T019, T020, T021 and T022 in parallel) and T023 → T024 → T025.
- T026 → T027 → T028.

## Parallel Opportunities

- T007 and T008, and T013 and T014, write separate fixture files.
- T019 to T022 write separate files and can be written while the stories are in progress.

### Parallel example: Phase 5

```text
Task: "T019 [P] Write bootstrap/repository.yml"
Task: "T020 [P] Update AGENTS.md"
Task: "T021 [P] Write dev/adr/0002-connect-repository-read-only.md"
Task: "T022 [P] Update dev/guides/record-a-product.md"
```

## Implementation Strategy

### First increment (User Story 1 by hand)

1. Phases 1 and 2: the check loads and runs.
2. Phase 3: the license model rule works by hand. This already closes the gap left by feature 001.

### Further increments

1. Phase 4 adds the review-age rules.
2. Phase 5 connects the repository so that Infrahub runs the check on every proposed change. This
   is the step that needs a push to GitHub.
3. Phase 6 runs the full arc, including the proposed change.
