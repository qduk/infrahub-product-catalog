---

description: "Task list for the network automation product catalog schema"
---

# Tasks: Network Automation Product Catalog Schema

**Input**: Design documents from `specs/001-catalog-schema/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/object-files.md](./contracts/object-files.md),
[quickstart.md](./quickstart.md)

**Tests**: the spec does not ask for automated tests. Each story ends with validation tasks that
load data into the local Infrahub instance and run the matching rows of the quickstart demo arc,
as constitution Principle II requires.

**Organization**: tasks are grouped by user story, so each story can be built and checked on its
own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: the user story the task belongs to (US1 to US4)

## Conventions for every task

- Run `infrahubctl` through uv: `uv run infrahubctl ...`. Set
  `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec` before any command that changes
  data.
- Load into the Infrahub branch `catalog-schema` (created in T003), never directly into `main`.
  Pass `--branch catalog-schema` to every `schema check`, `schema load` and `object load`.
- Before editing `schemas/` or `objects/`, read the `infrahub-managing-schemas` or
  `infrahub-managing-objects` skill (constitution Principle V).
- Report any failed load with its full output. Do not mark a task done after a failed load.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: prepare the repository and the local Infrahub instance.

- [X] T001 Create the directories `schemas/` and `objects/` at the repository root, each with no
  placeholder files
- [X] T002 Update `.infrahub.yml` so `schemas:` lists `schemas/catalog.yml` and a new `objects:`
  key lists the directory `objects`, keeping the existing header comments
- [X] T003 Confirm the instance answers with `uv run infrahubctl info` (address
  `http://localhost:8100`, Infrahub 1.11.8), then create the Infrahub branch with
  `uv run infrahubctl branch create catalog-schema`; record the result in
  `specs/001-catalog-schema/quickstart.md` only if a command differs from the one written there

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the whole data model. Every story reads or writes these nodes, and constitution
Principle I requires the schema to pass `schema check` before any object file is written.

**⚠️ CRITICAL**: no user story work can begin until this phase is complete.

- [X] T004 Write `schemas/catalog.yml` with the `# yaml-language-server` schema comment,
  `version: "1.0"` and the five nodes `CatalogBuildingBlock`, `CatalogPublisher`, `CatalogSource`,
  `CatalogProduct` and `CatalogCoverageClaim`, exactly as listed in
  `specs/001-catalog-schema/data-model.md`. Include for each node:
  - every attribute with its kind, `optional`, `unique` and dropdown `choices` (as objects with
    `name` and `label`);
  - every relationship with `peer` as the full kind, `kind`, `cardinality`, `optional`,
    `min_count` where the data model says "at least 1", and the `identifier` from the data model
    on both sides;
  - `on_delete: cascade` only on `CatalogProduct.coverage_claims`;
  - `human_friendly_id`, `display_label`, `uniqueness_constraints` and `generate_profile: false`;
  - on `CatalogProduct.full_name`: `computed_attribute` of kind `Jinja2` with template
    `{{ publisher__name__value }} {{ name__value }}`, `read_only: true`, `unique: true`;
  - a short `description` on each node and field, kept under the Infrahub length limits.
- [X] T005 Run `uv run infrahubctl schema format schemas/catalog.yml` and keep the reordered file
  in `schemas/catalog.yml`
- [X] T006 Run `uv run infrahubctl schema check --branch catalog-schema schemas/catalog.yml` and
  fix every error in `schemas/catalog.yml` until the check passes
- [X] T007 Load the schema with
  `uv run infrahubctl schema load --branch catalog-schema schemas/catalog.yml`, and confirm in the
  web interface on branch `catalog-schema` that the five `Catalog` node types appear in the menu
  (quickstart row 1, `specs/001-catalog-schema/quickstart.md`)

**Checkpoint**: the data model is loaded. User stories can begin.

---

## Phase 3: User Story 1 - Record the framework's building blocks (Priority: P1) 🎯 MVP

**Goal**: the six building blocks of the Network Automation Framework are in the catalog, each with
the framework's name, description and definition link, loaded from a data file.

**Independent Test**: load `objects/01_building_blocks.yml` into the catalog and view the building
block list. Six blocks appear, each with a working definition link.

### Implementation for User Story 1

- [X] T008 [US1] Open https://reference.networkautomation.forum/Framework/Framework/ and confirm,
  for each of Intent, Observability, Orchestrator, Executor, Collector and Presentation, that the
  section anchor in `specs/001-catalog-schema/research.md` R1 exists and the quoted description
  matches the page word for word; correct R1 in `specs/001-catalog-schema/research.md` where it
  does not, and stop and ask the user if the page lists different blocks
- [X] T009 [US1] Write `objects/01_building_blocks.yml` with one `CatalogBuildingBlock` entry for
  each of the six blocks, using the names, quoted descriptions and definition links confirmed in
  T008, in the shape given in `specs/001-catalog-schema/contracts/object-files.md`
- [X] T010 [US1] Load the file with
  `uv run infrahubctl object load --branch catalog-schema objects/01_building_blocks.yml`, run the
  same command a second time, and confirm that the second run creates no new building blocks
  (spec User Story 1, scenarios 1 and 2; quickstart row 2)
- [X] T011 [US1] Copy `objects/01_building_blocks.yml` to a scratch file outside the repository,
  remove `definition_url` from one entry, load the scratch file on branch `catalog-schema`, and
  confirm that Infrahub rejects the entry (spec User Story 1, scenario 3); delete the scratch file
  afterwards and leave `objects/01_building_blocks.yml` unchanged

**Checkpoint**: User Story 1 works on its own. The catalog lists the framework's building blocks.

---

## Phase 4: User Story 2 - Record a product and the building blocks it covers (Priority: P1)

**Goal**: products are recorded with their publisher, description, optional license model and
coverage claims, each fact linked to its source.

**Independent Test**: with the building blocks loaded, record one product with two coverage claims
and view it. The product shows its publisher, its covered building blocks with their extents, and
the sources for each claim and each product fact.

### Implementation for User Story 2

- [X] T012 [US2] Ask the user which products to record first. Ask for at least three products,
  including one building block that one product covers fully and another covers partly, as
  `specs/001-catalog-schema/quickstart.md` requires. For each product, ask for the sources of its
  publisher, description, license model and coverage claims. Record the answers as a list in
  `specs/001-catalog-schema/research.md` under a new heading "R10. First products". Do not choose
  products or invent sources without the user's answer.
- [X] T013 [P] [US2] Write `objects/02_sources.yml` with one `CatalogSource` entry (`title`, `url`,
  `last_checked`) for every source listed in R10 of `specs/001-catalog-schema/research.md`, each URL
  once, with `last_checked` set to the date the source was opened
- [X] T014 [P] [US2] Write `objects/03_publishers.yml` with one `CatalogPublisher` entry (`name`,
  `homepage_url`) for every publisher listed in R10 of `specs/001-catalog-schema/research.md`
- [X] T015 [US2] Write `objects/04_products.yml` with one `CatalogProduct` entry per product in
  R10 of `specs/001-catalog-schema/research.md`, in the shape given in
  `specs/001-catalog-schema/contracts/object-files.md`:
  - `publisher_sources` and `description_sources` with at least one source URL each;
  - `license_model` only when a source states it, with that source in `license_model_sources`;
  - a description that states what the product does, without marketing language (constitution
    Principle III);
  - nested `coverage_claims` with `building_block`, `extent`, optional `note` and at least one
    source each.
- [X] T016 [US2] Load all object files with
  `uv run infrahubctl object load --branch catalog-schema objects/`, run it a second time, and
  confirm that the second run creates nothing new (quickstart row 3)
- [X] T017 [US2] On branch `catalog-schema`, try to create a coverage claim with no source and a
  product with no description source through the web interface, and confirm that Infrahub refuses
  both and names the missing field (spec User Story 2, scenario 2; quickstart row 5)
- [X] T018 [US2] Open one product in the web interface on branch `catalog-schema` and confirm that
  it shows its publisher, its building blocks with extents, the sources of each claim and the
  sources of its publisher and description (spec User Story 2, scenarios 1 and 4); confirm that a
  product without a sourced license model shows an empty license model (scenario 3)

**Checkpoint**: User Stories 1 and 2 work on their own.

---

## Phase 5: User Story 3 - Compare products by building block (Priority: P2)

**Goal**: an engineer goes from a building block to every product that covers it, and from a
product to every building block it covers.

**Independent Test**: with three products loaded, open one building block and confirm that the
list of products matches the coverage claims in `objects/04_products.yml`.

### Implementation for User Story 3

- [X] T019 [US3] On branch `catalog-schema`, open the building block that one product covers
  fully and another partly, and confirm that its coverage claims list both products with their
  extents and sources (spec User Story 3, scenario 1; quickstart row 6); compare the list against
  `objects/04_products.yml`
- [X] T020 [US3] Open a building block that no product in `objects/04_products.yml` covers and
  confirm that its coverage claims list is empty (spec User Story 3, scenario 2)
- [X] T021 [US3] Try to delete a building block that has a coverage claim, and confirm that
  Infrahub refuses and names the claim (spec edge cases; quickstart row 9)

**Checkpoint**: User Story 3 works with the data from User Stories 1 and 2.

---

## Phase 6: User Story 4 - Trace a fact to its source (Priority: P2)

**Goal**: a reader opens the source behind any fact and views when it was last checked.

**Independent Test**: open any coverage claim, follow its source and confirm the source shows a
title, a link and a last-checked date.

### Implementation for User Story 4

- [X] T022 [US4] On branch `catalog-schema`, open a coverage claim, follow its source, and confirm
  the source shows its title, link and last-checked date (spec User Story 4, scenario 1;
  quickstart row 7)
- [X] T023 [US4] Open a product's license model sources and confirm they are listed separately
  from its publisher and description sources (spec User Story 4, scenario 2)
- [X] T024 [US4] Open a source from `objects/02_sources.yml` that supports claims for two products
  and confirm that both claims are listed on the source (spec User Story 4, scenario 3); if no
  source in R10 of `specs/001-catalog-schema/research.md` supports two products, record that this
  scenario could not be checked with the current data

**Checkpoint**: all four user stories work.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T025 Run every row of the demo arc in `specs/001-catalog-schema/quickstart.md`, including
  rows 4 and 8, which no earlier task covers, and record the time and outcome of each row in a
  "Results" section at the end of `specs/001-catalog-schema/quickstart.md`
  - Open on 2026-10-20: rows 1 to 3 and 5 to 9 pass (see the Results section). Row 4 still needs
    a person to enter a product in the web interface and time it.
- [X] T026 [P] Write a decision record `dev/adr/0001-catalog-schema-sources.md` in MADR format for
  the decisions in research R3 (one source relationship for each product fact) and R7 (the
  computed `full_name` that identifies products and claims), linking to
  `specs/001-catalog-schema/research.md`
- [X] T027 [P] Write `dev/guides/record-a-product.md` with the steps a maintainer follows to add a
  product: add its sources, add its publisher, add the product and its claims, load with
  `uv run infrahubctl object load`, and rename nodes in the web interface first (research R8); link
  to `specs/001-catalog-schema/contracts/object-files.md` for the file format
- [X] T028 Merge the Infrahub branch `catalog-schema` into `main` on the local instance through a
  proposed change in the web interface at http://localhost:8100, then confirm with
  `uv run infrahubctl object load objects/` against `main` that nothing new is created
- [X] T029 Run `uv run infrahubctl schema check schemas/catalog.yml` against `main` one last time
  and confirm it reports no changes; then mark the completed tasks in
  `specs/001-catalog-schema/tasks.md`

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup. Blocks all user stories.
- **User Story 1 (Phase 3)**: depends on Foundational.
- **User Story 2 (Phase 4)**: depends on Foundational and on User Story 1, because claims
  reference building blocks by name. T012 needs an answer from the user before T013 to T015 can
  start.
- **User Story 3 (Phase 5)** and **User Story 4 (Phase 6)**: depend on the data from User Stories 1
  and 2. They add no files and can run in either order.
- **Polish (Phase 7)**: depends on all user stories. T026 and T027 can start as soon as Phase 2 is
  done.

### Task order inside the phases

- T004 → T005 → T006 → T007.
- T008 → T009 → T010 → T011.
- T012 → (T013 and T014 in parallel) → T015 → T016 → T017 → T018.

## Parallel Opportunities

- T013 and T014 write different files and depend only on T012.
- T026 and T027 write different files in `dev/` and can be written while user story validation is
  running.
- Phases 5 and 6 only read data, so two people can check them at the same time.

### Parallel example: User Story 2

```text
After T012 is answered:
  Task: "T013 [P] [US2] Write objects/02_sources.yml"
  Task: "T014 [P] [US2] Write objects/03_publishers.yml"
Then: T015 (needs the source URLs and publisher names from both files)
```

## Implementation Strategy

### First increment (User Story 1 only)

1. Phase 1 and Phase 2: the schema is loaded on branch `catalog-schema`.
2. Phase 3: the six building blocks are loaded and checked.
3. Stop and check: the catalog lists the framework's building blocks with working links.

### Further increments

1. User Story 2 adds products once the user has named them in T012.
2. User Stories 3 and 4 check how readers compare products and trace sources, with no new files.
3. Polish runs the full demo arc, records the decisions and merges the Infrahub branch.
