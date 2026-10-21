# Implementation Plan: Product Status

**Branch**: `004-product-status` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-product-status/spec.md`

## Summary

Maintainers record whether each product is active, discontinued or acquired, with an optional date
and the sources that state it. The plan adds three fields to `CatalogProduct`:
- a `status` dropdown that defaults to `active`, so existing products need no edits;
- a `status_date`;
- a `status_sources` relationship.

The source check gains a rule that a non-active status needs a source. The coverage report writes
the status after the name of any product that is not active, so a catalog with only active
products gives the same report as today ([research.md](./research.md)).

## Technical Context

**Language/Version**: Infrahub schema YAML, Python 3.13 for the check and the transform, GraphQL.

**Primary Dependencies**: infrahub-sdk[ctl] 1.23.2. No new dependency.

**Storage**: the local Infrahub instance (1.11.8) and the GitHub repository.

**Testing**: the existing check and transform tests plus new fixtures, `infrahubctl check` and
`infrahubctl transform` on a branch, and the report rebuilt on `main`.

**Target Platform**: the local Infrahub instance.

**Project Type**: schema, check and transform change in the catalog repository.

**Performance Goals**: none beyond the spec.

**Constraints**:
- The existing report outputs must stay identical (SC-003).
- Changes to the check and the transform reach Infrahub only after a push, which needs the user's
  go-ahead.

**Scale/Scope**: three fields on one node, one inverse relationship, one check rule, one report
change.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | The schema change is loaded on a branch and checked before the check, transform or any data uses it. | Pass |
| II. Validation on the local instance | Schema on an Infrahub branch merged through a proposed change; check and transform run by hand on the branch, then in Infrahub after import. | Pass |
| III. Sourced product records | The status gets its own sources, and the check blocks a non-active status without one. | Pass |
| IV. Framework terms recorded as data | Not affected. | Pass |
| V. Infrahub conventions | Schemas skill loaded; default value for the new required attribute; identifiers on both sides of the new relationship; tests for the check and the transform. | Pass |

Post-design re-check: all gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/004-product-status/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── changes.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
schemas/catalog.yml                 # status, status_date, status_sources; inverse on CatalogSource
queries/catalog_source_check.gql    # adds status and status_sources count
checks/catalog_source_check.py      # status source rule
queries/catalog_report.gql          # adds status
transforms/catalog_report.py        # status after the product name
tests/                              # new fixtures for both
dev/guides/record-a-product.md      # how to record a status
```

**Structure Decision**: changes stay in the existing files. No new file except test fixtures.

## Complexity Tracking

No constitution violations to justify.
