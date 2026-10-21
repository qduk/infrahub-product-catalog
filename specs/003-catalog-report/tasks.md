---

description: "Task list for the catalog coverage report"
---

# Tasks: Catalog Coverage Report

**Input**: Design documents from `specs/003-catalog-report/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/report.md](./contracts/report.md),
[quickstart.md](./quickstart.md)

**Tests**: included. The transforms skill requires tests for every transform, and research R8
defines them. Each story adds Python tests for its section of the report first. Task T019 adds
tests that compare the complete report with expected files.

**Organization**: one phase per user story. The report is built in sections, one for each of the
first three stories: table, bar chart, diagram. User Story 4 delivers the report on proposed
changes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: the user story the task belongs to (US1 to US4)

## Conventions for every task

- Read the `infrahub-managing-transforms` skill before editing `transforms/`, `queries/` or
  `tests/`. Read the `infrahub-managing-schemas` skill before editing `schemas/`, and the
  `infrahub-managing-objects` skill before editing `objects/` (constitution Principle V).
- Run `infrahubctl` through uv, with
  `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec` for commands that change data.
- Schema and data changes go on the Infrahub branch `catalog-report`, and reach `main` only
  through a proposed change (constitution 1.1.0, Principle II).
- Do not push to GitHub without the user's go-ahead in the same session (tasks T022 and T027).
- Report every failed command with its output. Do not mark a task done after a failure.

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create `transforms/__init__.py` (empty) and the directories
  `tests/fixtures/catalog_report_current/`, `tests/fixtures/catalog_report_empty/`,
  `tests/fixtures/catalog_report_no_claims/` and `tests/fixtures/catalog_report_special_names/`
- [X] T002 Create the Infrahub branch with `uv run infrahubctl branch create catalog-report`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the report object, the query and the transform with no sections yet.

**⚠️ CRITICAL**: no user story work can begin until this phase is complete.

- [X] T003 Add the node `CatalogReport` to `schemas/catalog.yml` as specified in
  `specs/003-catalog-report/data-model.md`: `inherit_from: [CoreArtifactTarget]`, attributes
  `name` (Text, unique) and `description` (TextArea, optional), `human_friendly_id: [name__value]`,
  `display_label: name__value`, `generate_profile: false`, `include_in_menu: true`, icon
  `mdi:chart-bar`; then run `uv run infrahubctl schema format schemas/catalog.yml` and fix any blank
  line the formatter misplaces (feature 001 found one)
- [X] T004 Run `uv run infrahubctl schema check --branch catalog-report schemas/catalog.yml`,
  confirm the only change is the added `CatalogReport`, then load it with
  `uv run infrahubctl schema load --branch catalog-report schemas/catalog.yml`
- [X] T005 Write `objects/05_reports.yml` with two documents: a `CoreStandardGroup` named
  `catalog_reports` (label "Catalog reports"), then a `CatalogReport` named
  "Catalog coverage report" with a one-sentence description and
  `member_of_groups: [catalog_reports]`; validate it and load it with
  `uv run infrahubctl object load --branch catalog-report objects/05_reports.yml`, and confirm the
  report is a member of the group
- [X] T006 [P] Write `queries/catalog_report.gql` with query `catalog_report($report: String!)` that
  selects: `CatalogReport(name__value: $report)` with `id`, `__typename` and `name { value }`;
  every `CatalogBuildingBlock` with `id`, `__typename` and `name { value }`; and every
  `CatalogProduct` with `id`, `__typename`, `full_name { value }` and
  `coverage_claims { edges { node { id __typename extent { value } building_block { node { id name { value } } } } } }`
- [X] T007 Write `transforms/catalog_report.py` with class `CatalogReportTransform(InfrahubTransform)`,
  `query = "catalog_report"`, and an async `transform(self, data) -> str` that reads the report
  name, sorts building blocks by name and products by full name (case-insensitive, research R5),
  and returns only the heading `# <report name>` and the summary line
  `<n> products, <n> building blocks, <n> coverage claims.` as given in
  `specs/003-catalog-report/contracts/report.md`
- [X] T008 Add the query and the transform (not yet the artifact definition) to `.infrahub.yml`
  under `queries` and `python_transforms`, as given in
  `specs/003-catalog-report/contracts/report.md`; add a `tests/test_transforms.yml` with a
  `python-transform-smoke` test for resource `PythonTransform` named `catalog_report`; run
  `uv run pytest tests/` and
  `uv run infrahubctl transform catalog_report --branch catalog-report report="Catalog coverage report"`,
  and confirm the heading and summary line "3 products, 6 building blocks, 5 coverage claims."
- [X] T009 Save the query result for the `catalog-report` branch as
  `tests/fixtures/catalog_report_current/input.json`, and write the other three fixtures by hand
  in the same shape:
  - `catalog_report_empty/input.json`: six building blocks, no products.
  - `catalog_report_no_claims/input.json`: two blocks and one product with no claims.
  - `catalog_report_special_names/input.json`: a product named `Tool "X" [beta] | (v2)` with one
    full claim on a block named `Block (A)`.

**Checkpoint**: the transform runs on the branch and returns the heading and summary.

---

## Phase 3: User Story 1 - View which products cover which building blocks (Priority: P1) 🎯 MVP

**Goal**: the report shows the coverage table.

**Independent Test**: run the transform and compare each table cell with the coverage claims.

### Tests for User Story 1

- [X] T010 [US1] Write `tests/test_catalog_report.py` with a helper that runs
  `CatalogReportTransform` on a fixture, and tests that:
  - `catalog_report_current` gives the table in `specs/003-catalog-report/contracts/report.md`
    exactly;
  - `catalog_report_empty` gives the header row with all six blocks and the line
    "No products are recorded.";
  - `catalog_report_no_claims` gives a row of `—` cells;
  - `catalog_report_special_names` writes the `|` in the product name as `\|`.
  Run `uv run pytest tests/` and confirm the new tests fail.

### Implementation for User Story 1

- [X] T011 [US1] In `transforms/catalog_report.py`, add the `## Coverage by product` section with
  the table (`Full`, `Partial` or `—` per cell), the empty-catalog line, and the line "Each claim's
  sources are listed on the claim in the catalog." (FR-002, FR-009)
- [X] T012 [US1] Run `uv run pytest tests/` and confirm all tests pass, then run
  `uv run infrahubctl transform catalog_report --branch catalog-report report="Catalog coverage report"`
  and compare the table with the contract

**Checkpoint**: User Story 1 works when the transform is run by hand.

---

## Phase 4: User Story 2 - View how many products cover each building block (Priority: P2)

**Goal**: the report shows the bar chart of products per building block.

**Independent Test**: compare each bar's values with the claim counts per block.

### Tests for User Story 2

- [X] T013 [US2] Add tests to `tests/test_catalog_report.py` that:
  - `catalog_report_current` gives the `xychart-beta` block in
    `specs/003-catalog-report/contracts/report.md` exactly, with `bar [2, 1, 1, 1, 0, 0]` and
    `bar [1, 1, 1, 1, 0, 0]`;
  - `catalog_report_empty` gives all zeros and a y-axis of `0 --> 1`;
  - `catalog_report_special_names` writes a `"` in a block name as `#quot;` inside the x-axis
    label.
  Confirm the new tests fail.

### Implementation for User Story 2

- [X] T014 [US2] In `transforms/catalog_report.py`, add the `## Products per building block`
  section: a fenced `mermaid` block with `xychart-beta`, the title, the x-axis of block names in
  report order, the y-axis from 0 to the number of products (at least 1), the total series then
  the full series, and the explanation line from the contract (FR-003)
- [X] T015 [US2] Run `uv run pytest tests/` and confirm all tests pass

**Checkpoint**: User Stories 1 and 2 work when the transform is run by hand.

---

## Phase 5: User Story 3 - View the map from products to building blocks (Priority: P3)

**Goal**: the report shows the flowchart from products to building blocks.

**Independent Test**: confirm that each claim appears as one line with the right style.

### Tests for User Story 3

- [X] T016 [US3] Add tests to `tests/test_catalog_report.py` that:
  - `catalog_report_current` gives the `flowchart LR` block in
    `specs/003-catalog-report/contracts/report.md` exactly, with `==>` for full and `-.->` for
    partial claims;
  - `catalog_report_no_claims` declares the product and block nodes and has no lines;
  - `catalog_report_special_names` writes the label as `"Tool #quot;X#quot; [beta] | (v2)"`
    under a generated ID.
  Confirm the new tests fail.

### Implementation for User Story 3

- [X] T017 [US3] In `transforms/catalog_report.py`, add the `## Map of products to building
  blocks` section: product nodes `p1…` and block nodes `b1…` in report order, with quoted labels
  escaped as in research R7, one line per claim in product then block order, and the explanation
  line from the contract (FR-004)
- [X] T018 [US3] Run `uv run pytest tests/` and confirm all tests pass, then run the transform on
  the `catalog-report` branch and confirm the full output matches
  `specs/003-catalog-report/contracts/report.md`

**Checkpoint**: the report text is complete when run by hand.

---

## Phase 6: User Story 4 - Review how a change affects the report (Priority: P2)

**Goal**: Infrahub builds the report as an artifact and rebuilds it on every proposed change.

**Independent Test**: on a branch, add a claim, open a proposed change and confirm the report on
the proposed change includes it while the report on `main` does not.

- [X] T019 [US4] Save the transform's output for each fixture as `output.md` next to its
  `input.json` in `tests/fixtures/catalog_report_*/`, check each file by eye against the
  contract, and add a `python-transform-unit-process` test per fixture with `output: output.md`
  to `tests/test_transforms.yml`; run `uv run pytest tests/` and confirm the tests pass, then
  change one character in one `output.md`, confirm that test fails, and restore it
- [X] T020 [US4] Add the `artifact_definitions` entry `catalog_coverage_report` to `.infrahub.yml`
  exactly as given in `specs/003-catalog-report/contracts/report.md`
  (`content_type: text/markdown`, `targets: catalog_reports`, `transformation: catalog_report`,
  `parameters: {report: name__value}`)
- [X] T021 [US4] Run `uv run infrahubctl check catalog_source_check --branch catalog-report --format-json`
  and confirm it passes, then open a proposed change from `catalog-report` to `main` for the
  schema and report object, confirm all checks pass, and merge it
- [ ] T022 [US4] Commit all work on the Git branch `003-catalog-report`, merge it into `main` with
  `git merge --ff-only`, then ask the user for the go-ahead to push `main` to `origin`; push only
  after they agree, and stop here if they do not
- [ ] T023 [US4] In the Infrahub web interface (or through the API), run **Import latest commit**
  on the repository `infrahub-product-catalog`, wait until it is in sync at the new commit, and
  confirm Infrahub lists the transform `catalog_report` and the artifact definition
  `catalog_coverage_report`
- [ ] T024 [US4] Generate the artifact on `main` for the definition `catalog_coverage_report`,
  poll `CoreArtifact` until it exists (transforms skill, `artifacts-async-regen-polling`), and
  confirm its content matches `tests/fixtures/catalog_report_current/output.md`; record the result
  in the "Results" section of `specs/003-catalog-report/quickstart.md`

**Checkpoint**: the report is an artifact in Infrahub.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T025 Run quickstart rows 2 to 6 in `specs/003-catalog-report/quickstart.md` on the
  Infrahub branch `demo-report`, and record each row's outcome and time in its "Results" section.
  Row 4 confirms that the report is rebuilt on a proposed change (FR-007), and row 5 that a new
  building block appears with no change to any file (SC-004). Close the proposed change and delete
  the branch afterwards.
- [ ] T026 Ask the user to run quickstart row 1 in a browser (view the table, bar chart and
  diagram on the artifact, and say how the two bar series are drawn), and record their answer in
  `specs/003-catalog-report/quickstart.md`; if the bars are drawn side by side, update the
  explanation line in `transforms/catalog_report.py`, the expected outputs and
  `specs/003-catalog-report/contracts/report.md` (research R2)
- [ ] T027 Update `dev/guides/record-a-product.md` with a step that says where to view the report
  and that a proposed change shows the updated report; commit the results on a new Git branch,
  merge it into `main`, and ask the user before pushing
- [ ] T028 Mark the completed tasks in `specs/003-catalog-report/tasks.md` and record any task
  left open, with the reason, under it

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup. T003 → T004 → T005 must finish before T008 runs
  the transform on the branch.
- **User Stories 1 to 3 (Phases 3 to 5)**: depend on Phase 2. They all edit
  `transforms/catalog_report.py` and `tests/test_catalog_report.py`, so they run one after the
  other: US1, then US2, then US3.
- **User Story 4 (Phase 6)**: depends on US1 to US3, because the expected outputs in T019 are the
  complete report.
- **Polish (Phase 7)**: depends on Phase 6. T026 needs the user.

### Task order inside the phases

- T003 → T004 → T005; T006 → T007 → T008 → T009.
- T010 → T011 → T012; T013 → T014 → T015; T016 → T017 → T018.
- T019 → T020 → T021 → T022 → T023 → T024.

## Parallel Opportunities

Most tasks change the same two files, so there is little parallel work.

- T006 (query) can be written while T003 to T005 run, because it touches a different file.
- T027's guide update can be written while T025 runs.

## Implementation Strategy

### First increment (User Story 1 by hand)

1. Phases 1 and 2: the report object exists on a branch and the transform runs.
2. Phase 3: the coverage table is correct when the transform is run by hand.

### Further increments

1. Phases 4 and 5 add the bar chart and the diagram.
2. Phase 6 turns the transform into an artifact that Infrahub rebuilds on proposed changes. This
   is the step that needs a push to GitHub.
3. Phase 7 checks the report on a proposed change and, with the user, in a browser.
