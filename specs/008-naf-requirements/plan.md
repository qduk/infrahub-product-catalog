# Implementation Plan: Framework Requirements and Coverage Assessments

**Branch**: `015-naf-requirements` | **Date**: 2026-10-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/008-naf-requirements/spec.md`

## Summary

The catalog records the framework's MUST, SHOULD and MAY requirements as `CatalogRequirement` nodes,
and one `CatalogRequirementVerdict` per claim and requirement. The stored `extent` is removed: the
catalog service and the coverage report compute it from the verdicts ([research.md](./research.md)
section 1). A new check enforces sources and block matching. The web app's details card lists the
requirements with their verdicts. The 97 existing claims are researched by one agent per block and
approved by the user before loading.

## Technical Context

**Language/Version**: Python 3.13 (checks, transform, service), TypeScript and React 19 (web app).

**Primary Dependencies**: none added.

**Storage**: Infrahub 1.11.8 schema change ([data-model.md](./data-model.md)).

**Testing**: pytest for checks, transform and service; Vitest for the web app; `infrahubctl` on the
local instance; the walkthrough in [quickstart.md](./quickstart.md).

**Target Platform**: local instance first, then the GCP beta after the user approves the push.

**Project Type**: schema, object data, checks, transform, service and web app.

**Performance Goals**: the catalog response grows by about 850 verdicts; it is cached 60 seconds, as
before.

**Constraints**:
- No list of building blocks in code (Principle IV): requirements and their blocks are data.
- Every verdict other than not shown has a source (Principle III).

**Scale/Scope**: about 36 requirements, about 850 verdicts, 97 claims.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | Starts with the schema change; object files and code follow `schema check`. | Pass |
| II. Validation on the local instance | Schema, data and checks are loaded on a branch and merged through a proposed change locally first. | Pass |
| III. Sourced product records | Every verdict except "not shown" needs a source, enforced by a check. | Pass |
| IV. Framework terms recorded as data | Requirements are records quoted from the framework, loaded from object files. | Pass |
| V. Infrahub conventions | Skills read; HFIDs on both new nodes; identifiers on every paired relationship; `state: absent` for the removed attribute. | Pass |

Re-checked after Phase 1 design: all pass.

## Project Structure

### Documentation (this feature)

```text
specs/008-naf-requirements/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/catalog-api.md
└── tasks.md
```

### Source Code (repository root)

```text
schemas/catalog.yml                       # two nodes, claim name, extent removed
objects/01_building_blocks.yml            # requirements added
objects/04_products.yml                   # extent removed
objects/06_requirement_verdicts.yml       # new, approved verdicts
queries/catalog_records.gql               # verdicts and requirements added, extent removed
queries/catalog_verdict_check.gql         # new
queries/catalog_report.gql                # verdicts instead of extent
checks/catalog_record_checks.py           # submission and unused-source rules updated
checks/catalog_verdict_check.py           # new
transforms/catalog_report.py              # computed extent
frontend/api/catalog_web/catalog.py       # requirements, verdicts, computed extent
frontend/api/catalog_web/submissions.py   # extent removed
frontend/web/src/                         # details card requirements; form without extent
dev/knowledge/naf-requirements-2026-10-23/  # research output and review page source
```

## Complexity Tracking

No constitution violations to justify.
