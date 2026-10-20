# Implementation Plan: Source Check for Catalog Changes

**Branch**: `002-source-check` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-source-check/spec.md`

## Summary

Catalog maintainers get one check that Infrahub runs on every proposed change. It blocks the merge
when a product has a license model with no source or when a source has a last-checked date in the
future. It lists, without blocking, every source last checked more than 6 months ago. To run on
proposed changes, the GitHub repository is registered in Infrahub as a read-only repository that
provides only the check. Schema and data keep reaching `main` through Infrahub branches and
proposed changes ([research.md](./research.md) R1, R2). A test of the check logic on a throwaway
Infrahub branch matched every rule in the spec (R4).

## Technical Context

**Language/Version**: Python 3.13 for the check, GraphQL for its query, YAML for tests and
configuration.

**Primary Dependencies**: infrahub-sdk[ctl] 1.23.2 (`InfrahubCheck`, `infrahubctl`, pytest plugin).
`pytest` is added to the `dev` dependency group.

**Storage**: the local Infrahub instance (Infrahub 1.11.8) and the public GitHub repository
<https://github.com/qduk/infrahub-product-catalog>.

**Testing**: YAML-driven smoke and unit tests with `uv run pytest tests/`, `infrahubctl check` on
an Infrahub branch, and a proposed change on the local instance ([quickstart.md](./quickstart.md)).

**Target Platform**: the local Infrahub instance. Its task worker clones the repository from
GitHub.

**Project Type**: Infrahub check in a schema and data repository.

**Performance Goals**: the check result appears on a proposed change within 5 minutes (SC-003).
The catalog holds tens of products and sources, so one query covers all of them.

**Constraints**:
- Infrahub reads only committed and pushed code, so the check must be on `main` on GitHub before
  the repository is registered.
- Pushing to GitHub publishes the code. Each push needs the user's go-ahead.

**Scale/Scope**: one check, one query, one repository registration, plus updates to
`.infrahub.yml`, `AGENTS.md`, the constitution and the maintainer guide.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | No schema change. The check reads only fields defined in `schemas/catalog.yml`. | Pass |
| II. Validation on the local instance | The check runs on the local instance by hand and in a proposed change before the feature is done. The principle's wording about running checks with `infrahubctl` "because this repository is not connected" becomes out of date, so this feature amends it (research R8). | Pass, with an amendment in this feature |
| III. Sourced product records | This feature enforces the license model rule that the schema could not enforce, and flags sources that are due for review. | Pass |
| IV. Framework terms recorded as data | Not affected. | Pass |
| V. Infrahub conventions | The `infrahub-managing-checks` skill was loaded for specify and plan. The query selects `id` and `__typename`, `check_definitions` has no `query:` key, and the check ships with tests. | Pass |

Post-design re-check: the only change to governance is the Principle II amendment, which is a
task in this feature. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/002-source-check/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── check-results.md
├── checklists/
│   └── requirements.md
└── tasks.md             # created by /speckit-tasks
```

### Source Code (repository root)

```text
checks/
└── catalog_source_check.py      # CatalogSourceCheck
queries/
└── catalog_source_check.gql
tests/
├── test_checks.yml              # smoke and unit tests
└── fixtures/                    # saved query results, one directory per case
bootstrap/
└── repository.yml               # CoreReadOnlyRepository, loaded once by hand
.infrahub.yml                    # queries and check_definitions only
pyproject.toml                   # pytest added to the dev group
AGENTS.md                        # how the repository is connected and updated
.specify/memory/constitution.md  # Principle II amended to 1.1.0
dev/adr/0002-connect-repository-read-only.md
dev/guides/record-a-product.md   # merge through a proposed change; run the check by hand
```

**Structure Decision**: the layout follows the checks skill (`checks/`, `queries/`, `tests/`). The
repository registration lives in `bootstrap/`, outside `objects/` (research R7).

## Order of work

1. Write the check, query and tests. Run them with `pytest` and `infrahubctl check` on an
   Infrahub branch.
2. Update `.infrahub.yml`, `AGENTS.md`, the guide, the decision record and the constitution.
3. Merge `002-source-check` into `main` in Git and, with the user's go-ahead, push `main` to
   GitHub.
4. Register the repository and confirm Infrahub lists the check.
5. Run the quickstart arc. Row 4 settles the open question in research R1. If Infrahub does not
   run the check on a proposed change from a branch that does not sync with Git, stop and report
   it before marking the feature done.

## Complexity Tracking

No constitution violations to justify.
