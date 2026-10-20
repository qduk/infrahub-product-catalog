# Implementation Plan: Network Automation Product Catalog Schema

**Branch**: `001-catalog-schema` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-catalog-schema/spec.md`

## Summary

A network automation team records network automation products and maps each product to the six
building blocks of the Network Automation Framework, with a source behind every fact. The plan
adds one schema file with five nodes in the `Catalog` namespace:
- building block
- publisher
- source
- product
- coverage claim

It also adds object files for the six building blocks and the first products. Infrahub's own rules
on required relationships, minimum counts and uniqueness enforce the spec's rejection and
deletion rules. A test on a throwaway Infrahub branch confirmed each rule
([research.md](./research.md) R3 to R7).

## Technical Context

**Language/Version**: Infrahub schema YAML (`version: "1.0"`) and object files
(`apiVersion: infrahub.app/v1`). Python 3.13 runs `infrahubctl`.

**Primary Dependencies**: Infrahub 1.11.8, infrahub-sdk[ctl] 1.23.2 through uv.

**Storage**: the local Infrahub instance (Docker Compose project `infrahub-product-catalog`,
port 8100).

**Testing**: `uv run infrahubctl schema check`, then `schema load` and `object load` on an
Infrahub branch, then the demo arc in [quickstart.md](./quickstart.md).

**Target Platform**: the local Infrahub instance.

**Project Type**: Infrahub schema and data repository.

**Performance Goals**: none beyond the spec's success criteria. The catalog holds tens of
products, not thousands.

**Constraints**: the repository is not connected to Infrahub as a Git repository, so every load is
run with `uv run infrahubctl`. Schema string lengths must stay under the limits in the published
Infrahub JSON schema.

**Scale/Scope**: 6 building blocks. Tens of publishers, products and sources. Up to 6 claims per
product.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | The schema file is written and passes `schema check` before any object file. Object files use only fields in [data-model.md](./data-model.md). | Pass |
| II. Validation on the local instance | Schema and object files are loaded on an Infrahub branch of the local instance, and the demo arc runs there. | Pass |
| III. Sourced product records | Claims require a source. Publisher and description require their own sources. License model stays empty without a source. The rule that a license model needs a source cannot be enforced by the schema (research R3). It is checked in review until a check is built. | Pass, with one rule checked in review |
| IV. Framework terms recorded as data | Building blocks are nodes loaded from `objects/01_building_blocks.yml`, with names and links from the framework's reference page (research R1). No schema field lists the blocks. | Pass |
| V. Infrahub conventions | The `infrahub-managing-schemas` skill was loaded for specify and plan. PascalCase node names, snake_case fields, a human-friendly ID on every node, an identifier on every two-way relationship. No generic, because no two nodes share fields. | Pass |

Post-design re-check: the data model adds no exception. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/001-catalog-schema/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── object-files.md
├── checklists/
│   └── requirements.md
└── tasks.md             # created by /speckit-tasks
```

### Source Code (repository root)

```text
schemas/
└── catalog.yml                 # five Catalog nodes
objects/
├── 01_building_blocks.yml      # the six framework building blocks
├── 02_sources.yml
├── 03_publishers.yml
└── 04_products.yml             # products with nested coverage claims
.infrahub.yml                   # lists schemas/catalog.yml and the object files
```

**Structure Decision**: one schema file, because the five nodes form one small model. Object files
are numbered so that each file only references nodes from earlier files
([contracts/object-files.md](./contracts/object-files.md)).

## Open items for implementation

- Confirm each building block's definition link and quoted description on the framework's page
  before loading (research R1).
- Choose the first products to record and collect their sources. The spec does not name any
  products. The demo arc needs at least three, including one building block that one product
  covers fully and another covers partly.

## Complexity Tracking

No constitution violations to justify.
