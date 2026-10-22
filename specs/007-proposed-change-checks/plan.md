# Implementation Plan: Proposed Change Checks for Catalog Submissions

**Branch**: `007-proposed-change-checks` | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/007-proposed-change-checks/spec.md`

## Summary

Four Infrahub checks run on every proposed change, each reported under its own name:
- `catalog_submission_check`: on `submission-*` branches, compares every catalog record with `main`
  and fails on a deleted or changed record or an added building block;
- `catalog_duplicate_check`: fails on publishers, products of one publisher, or source links that
  are the same after normalisation;
- `catalog_coverage_check`: warns about products with no coverage claim;
- `catalog_unused_source_check`: fails on sources that support nothing.

All four share one query, `catalog_records`. The submission check also runs that query on `main`
([research.md](./research.md)).

## Technical Context

**Language/Version**: Python 3.13, infrahub-sdk 1.23.2 (existing `dev` group).

**Primary Dependencies**: none added.

**Storage**: none. The checks only read data (FR-014).

**Testing**: pytest unit tests with fixture data in `tests/`, run with `uv run pytest tests/`; each
check run by hand with `uv run infrahubctl check`; the walkthrough in
[quickstart.md](./quickstart.md).

**Target Platform**: Infrahub 1.11.8 task workers, through the read-only repository.

**Project Type**: Infrahub repository code (checks and a query).

**Performance Goals**: under 1 minute for all four checks on the current catalog (SC-006).

**Constraints**:
- No list of building blocks in code (Principle IV).
- No imports between check files.

**Scale/Scope**: one query file, one check file with four classes, one test file, four
`.infrahub.yml` entries.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | No schema change. The query uses only nodes, attributes and relationships in `schemas/catalog.yml`. | Pass |
| II. Validation on the local instance | Each check is run by hand on `main` and on test branches, then in a proposed change after **Import latest commit**. | Pass |
| III. Sourced product records | The unused source check removes sources that support no fact; the others leave sourcing rules to `catalog_source_check`. | Pass |
| IV. Framework terms recorded as data | The submission check finds an added building block by comparing with `main`, not by a list of names. | Pass |
| V. Infrahub conventions | `infrahub-managing-checks` read; query bound on the class, not in `check_definitions`; `log_info` used for the warning. | Pass |

Re-checked after Phase 1 design: all pass.

## Project Structure

### Documentation (this feature)

```text
specs/007-proposed-change-checks/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/check-results.md
└── tasks.md
```

### Source Code (repository root)

```text
queries/catalog_records.gql          # shared query
checks/catalog_record_checks.py      # four check classes
tests/test_catalog_record_checks.py  # unit tests with fixture data
.infrahub.yml                        # query and four check definitions added
AGENTS.md                            # list of checks updated
```

## Complexity Tracking

No constitution violations to justify.
