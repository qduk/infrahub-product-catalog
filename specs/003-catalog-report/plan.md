# Implementation Plan: Catalog Coverage Report

**Branch**: `003-catalog-report` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-catalog-report/spec.md`

## Summary

Engineers get one report in Infrahub that shows the whole catalog:
- a coverage table of products against building blocks;
- a bar chart of products per building block;
- a diagram from products to the blocks they cover.

The report is a Markdown artifact with Mermaid charts, built by a Python transform from the
catalog data. Infrahub attaches each artifact to an object, so the plan adds one schema node,
`CatalogReport`, and one instance of it. Infrahub rebuilds the report on every proposed change
through the read-only repository connection from feature 002. The Mermaid build in Infrahub
1.11.8 includes bar charts and flowcharts ([research.md](./research.md) R1).

## Technical Context

**Language/Version**: Python 3.13 for the transform, GraphQL for its query, YAML for schema,
objects, tests and configuration.

**Primary Dependencies**: infrahub-sdk[ctl] 1.23.2 (`InfrahubTransform`, `infrahubctl`, pytest
plugin). No new dependency.

**Storage**: the local Infrahub instance (1.11.8) and the GitHub repository.

**Testing**:
- `python-transform-unit-process` tests that compare output with fixed expected files;
- `uv run infrahubctl transform catalog_report --branch <branch>`;
- the artifact on a proposed change ([quickstart.md](./quickstart.md)).

**Target Platform**: Infrahub's web interface, which draws the Mermaid charts.

**Project Type**: Infrahub transform and artifact in a schema and data repository.

**Performance Goals**: the report is rebuilt on a proposed change within 5 minutes (SC-003). The
catalog holds tens of products, so one query covers it.

**Constraints**:
- The report text depends only on the catalog data, so that unchanged data gives an unchanged
  report (research R6).
- Infrahub reads only pushed code, and each push needs the user's go-ahead.

**Scale/Scope**: one schema node, one object file, one query, one transform, one artifact
definition, and tests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | `CatalogReport` is added to `schemas/catalog.yml` and passes `schema check` before the object file, query or transform is written. | Pass |
| II. Validation on the local instance | The schema and object file load on an Infrahub branch and merge through a proposed change. The transform runs with `infrahubctl transform` before it is pushed, and the artifact is checked on a proposed change. | Pass |
| III. Sourced product records | The report adds no facts. It points readers to the sources on each claim (FR-009). | Pass |
| IV. Framework terms recorded as data | The report reads building blocks from the catalog and holds no fixed list (FR-006). Quickstart row 5 tests this. | Pass |
| V. Infrahub conventions | The transforms and schemas skills were loaded. `CoreArtifactTarget` is on the concrete node, `content_type` is `text/markdown`, the transform name matches the artifact definition, and tests compare full output. | Pass |

Post-design re-check: all gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/003-catalog-report/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── report.md
├── checklists/
│   └── requirements.md
└── tasks.md             # created by /speckit-tasks
```

### Source Code (repository root)

```text
schemas/catalog.yml              # adds CatalogReport
objects/05_reports.yml           # group catalog_reports and the report object
queries/catalog_report.gql
transforms/
├── __init__.py
└── catalog_report.py            # CatalogReportTransform
tests/
├── test_transforms.yml          # smoke and expected-output tests
└── fixtures/catalog_report_*/   # input.json and output.md per case
.infrahub.yml                    # adds the query, transform and artifact definition
dev/guides/record-a-product.md   # where to view the report
```

**Structure Decision**: follows the transforms skill layout (`transforms/`, `queries/`). The
report object goes in `objects/` because it is catalog data, loaded on a branch like the rest.

## Order of work

1. Add `CatalogReport` to the schema and load it on an Infrahub branch.
2. Add `objects/05_reports.yml` and load it on the same branch.
3. Write the query, transform and tests. Run them with `pytest` and `infrahubctl transform` on
   the branch.
4. Merge the branch into `main` through a proposed change.
5. Commit, merge into Git `main`, push with the user's go-ahead, and run **Import latest commit**.
6. Run the quickstart arc. Row 1 needs a person to view the charts in a browser.

## Decisions made during planning

- The report text leaves out the build time and branch (research R6). The user confirmed this on
  2026-10-21, and spec FR-008 was rewritten to match.

## Complexity Tracking

No constitution violations to justify.
