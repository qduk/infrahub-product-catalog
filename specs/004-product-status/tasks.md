---

description: "Task list for product status"
---

# Tasks: Product Status

**Input**: Design documents from `specs/004-product-status/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/changes.md](./contracts/changes.md),
[quickstart.md](./quickstart.md)

**Tests**: included, following the checks and transforms skills. Tests come before each change.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: the user story the task belongs to (US1 to US3)

## Conventions for every task

- Read the schemas, checks or transforms skill before editing `schemas/`, `checks/` and
  `queries/`, or `transforms/` (constitution Principle V).
- Run `infrahubctl` through uv, with
  `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec` for commands that change data.
- Schema changes go on the Infrahub branch `product-status` and reach `main` through a proposed
  change.
- Do not push to GitHub without the user's go-ahead (task T015).

---

## Phase 1: Setup

- [X] T001 Create the Infrahub branch with `uv run infrahubctl branch create product-status`

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T002 In `schemas/catalog.yml`, add to `CatalogProduct` the attributes `status` (Dropdown,
  choices `active`/`discontinued`/`acquired` with labels, `default_value: active`, description
  under the length limit) and `status_date` (DateTime, optional), and the relationship
  `status_sources` (peer `CatalogSource`, kind Attribute, cardinality many, identifier
  `product__status_sources`); add to `CatalogSource` the inverse `status_of_products` with the same
  identifier; run `uv run infrahubctl schema format schemas/catalog.yml` and fix any misplaced blank
  line
- [X] T003 Run `uv run infrahubctl schema check --branch product-status schemas/catalog.yml` and
  confirm only these fields change, load it with `schema load --branch product-status`, then
  confirm through GraphQL that the three existing products read `status` = `active` and that
  `objects/04_products.yml` is unchanged (quickstart row 1)

**Checkpoint**: the status exists on the branch, and existing products are active.

---

## Phase 3: User Story 1 - Record that a product is no longer sold (Priority: P1) 🎯 MVP

**Goal**: a product can carry a status, a date and status sources.

**Independent Test**: on a test branch, set a product to `discontinued` with a date and a source,
and read all three back.

- [X] T004 [US1] Create the Infrahub branch `test-status`, set Red Hat Ansible to `discontinued`
  with `status_date` 2025-02-24 and the source `https://github.com/ansible/ansible` as a status
  source through the SDK, read the three fields back, confirm they match, then delete the branch
  (spec User Story 1, scenarios 1 to 3)
- [X] T005 [P] [US1] Update `specs/001-catalog-schema/contracts/object-files.md` with the
  `status`, `status_date` and `status_sources` keys from
  `specs/004-product-status/contracts/changes.md`, and add a step to
  `dev/guides/record-a-product.md` on recording a status and its source

---

## Phase 4: User Story 2 - Flag a status that has no source (Priority: P1)

**Goal**: the source check blocks a non-active status with no source.

**Independent Test**: on a branch, mark a product discontinued with no status source, run the
check, and confirm it fails and names the product.

- [X] T006 [US2] Add `status` and `status_sources.count` to every product in the five
  `tests/fixtures/license_model_*` and `tests/fixtures/source_*` input files (status `active`,
  count 0), and add the fixtures `tests/fixtures/status_missing_source/input.json` (status
  `discontinued`, count 0) and `tests/fixtures/status_with_source/input.json` (status `acquired`,
  count 1)
- [X] T007 [US2] Add tests to `tests/test_catalog_source_check.py`: `status_missing_source` fails
  with the message in `specs/004-product-status/contracts/changes.md`, and `status_with_source`
  and every existing fixture logs no status error; add matching `check-unit-process` entries to
  `tests/test_checks.yml`; run `uv run pytest tests/` and confirm the new failing test fails
- [X] T008 [US2] Add `status { value }` and `status_sources { count }` to the products in
  `queries/catalog_source_check.gql`, and the status rule to `checks/catalog_source_check.py`;
  run `uv run pytest tests/` and confirm all tests pass
- [X] T009 [US2] On a throwaway Infrahub branch, set a product to `discontinued` with no status
  source, run `uv run infrahubctl check catalog_source_check --branch <branch> --format-json`,
  confirm the error and exit status 1, add a status source, confirm the check passes, and delete
  the branch (quickstart rows 3 and 4)

---

## Phase 5: User Story 3 - See status in the coverage report (Priority: P2)

**Goal**: the report writes the status after the name of any product that is not active.

**Independent Test**: with one discontinued product, the report row shows it; with only active
products, the report is unchanged.

- [X] T010 [US3] Add `"status": {"value": "active"}` to every product in the four
  `tests/fixtures/catalog_report_*/input.json` files, and add the fixture
  `tests/fixtures/catalog_report_status/input.json` with one active and one discontinued product
- [X] T011 [US3] Add tests to `tests/test_catalog_report.py`: the discontinued product's row reads
  `| <full name> (discontinued) |`, and the active product's row has no bracket; confirm the new
  test fails; confirm the four existing `output.md` files still match
- [X] T012 [US3] Add `status { value }` to the products in `queries/catalog_report.gql`, and the
  bracket to the product cell in `transforms/catalog_report.py`; save
  `tests/fixtures/catalog_report_status/output.md` and add its `python-transform-unit-process`
  test to `tests/test_transforms.yml`; run `uv run pytest tests/` and confirm all tests pass and
  the four earlier `output.md` files are unchanged
- [X] T013 [US3] Run `uv run infrahubctl transform catalog_report --branch product-status
  report="Catalog coverage report"` and confirm the output equals
  `tests/fixtures/catalog_report_current/output.md` (quickstart row 5 is covered by T012's
  fixture)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T014 Open a proposed change from `product-status` to `main`, confirm its checks pass, and
  merge it
- [ ] T015 Commit on the Git branch `004-product-status`, merge into `main` with
  `git merge --ff-only`, and ask the user for the go-ahead to push; push only if they agree
- [ ] T016 Run **Import latest commit** on the repository, rebuild the report on `main`, confirm it
  equals `tests/fixtures/catalog_report_current/output.md`, record the results in
  `specs/004-product-status/quickstart.md`, and mark the completed tasks in
  `specs/004-product-status/tasks.md`

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phases 3, 4 and 5. Phases 4 and 5 touch different files and can run in
  either order. T005 can run alongside them.
- T014 needs Phases 2 to 5. T015 needs T014. T016 needs T015 and the user's go-ahead.

## Parallel Opportunities

- T005 (documentation) can run alongside any task in Phases 4 and 5.

## Implementation Strategy

1. Phases 1 to 3: the status field works on a branch.
2. Phase 4: the check enforces the status source.
3. Phase 5: the report shows the status.
4. Phase 6: merge, push with the user's go-ahead, and import.
