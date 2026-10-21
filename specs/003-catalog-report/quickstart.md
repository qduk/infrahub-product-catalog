# Quickstart: Validate the Catalog Coverage Report

**Feature**: [spec.md](./spec.md) | **Data model**: [data-model.md](./data-model.md) |
**Contract**: [contracts/report.md](./contracts/report.md)

## Prerequisites

- The local instance is running and `uv run infrahubctl info` shows it as connected.
- `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec`
- `CatalogReport` and `objects/05_reports.yml` are loaded and merged into `main` through a
  proposed change.
- The transform, query and artifact definition are pushed to `main` on GitHub, and **Import
  latest commit** has been run on the repository.

## Demo arc

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | In the web interface, open **Catalog Report** > "Catalog coverage report" > **Artifacts** > `catalog-coverage-report` | The table shows 3 products × 6 building blocks with 5 filled cells. The bar chart and the flowchart are drawn, not shown as code. A person confirms how the second bar series is drawn (research R2). | ~60s | SC-001 |
| 2 | Find which products cover Collector | Read the Collector column: Red Hat Ansible (Partial), Stardust Systems SuzieQ (Full). | ~30s | SC-002 |
| 3 | `uv run pytest tests/` | All transform and check tests pass, including the expected-output comparisons. | ~20s | SC-001 |
| 4 | Create the Infrahub branch `demo-report`, add a coverage claim for OpsMill Infrahub on Orchestrator (partial, with a source), and open a proposed change | Within 5 minutes the proposed change lists the report artifact as changed. The Orchestrator column, bar and diagram line include the new claim. The report on `main` does not. | ~4m | SC-003 |
| 5 | On `demo-report`, add a building block "Test Block" with a definition link, then view the report on the proposed change after it is rebuilt | The report has a seventh column, bar and diagram node for "Test Block", with no change to any file in the repository. | ~2m | SC-004 |
| 6 | Close the proposed change and delete `demo-report` | `main` and its report are unchanged. | ~30s | SC-003 |

Total time: about 8 minutes 20 seconds.

## Results

### Setup (tasks T021 to T024)

- **T021, 2026-10-21**: the proposed change "Catalog report object (feature 003)" merged
  `CatalogReport`, the group `catalog_reports` and the report object into `main`. Data Integrity
  and `catalog_source_check` passed. While the proposed change was running, the database
  container restarted once (restart count 1, not killed for memory, exit code 0, cause unknown).
  The checks were run again and passed. No Schema Integrity result appeared on this proposed
  change within 5 minutes, although one appeared on the proposed change in feature 002.
- **T023**: **Import latest commit** brought the repository to commit `a63ec0d` (`in-sync`,
  `online`). Infrahub listed the transform `catalog_report` and the artifact definition
  `catalog_coverage_report` (`text/markdown`).
- **T024**: the artifact `catalog-coverage-report` was built on `main` (status `Ready`). Its content
  is identical to `tests/fixtures/catalog_report_current/output.md`.

### Demo arc (task T025)

Run on 2026-10-21 on the Infrahub branch `demo-report`, through Infrahub's GraphQL API and
`infrahubctl`. Row 1 needs a person at a browser and is recorded under task T026.

| # | Outcome | Time |
|---|---|---|
| 2 | Pass. The Collector column of the report on `main` reads Red Hat Ansible: Partial and Stardust Systems SuzieQ: Full. | under 1s |
| 3 | Pass. 34 tests passed (`uv run pytest tests/`). | under 1s |
| 4 | Pass. A partial claim for OpsMill Infrahub on Orchestrator was added and a proposed change opened. 20 seconds later, "Artifact Validator: catalog_coverage_report" had completed with `success`, along with Data Integrity, Schema Integrity and `catalog_source_check`. The report on the branch read "6 coverage claims", showed `Partial` in the Orchestrator column, `bar [2, 1, 1, 1, 1, 0]` and the line `p1 -.-> b5`. The report on `main` was unchanged. | 24s |
| 5 | Pass. After "Test Block" was added on the branch and the artifact check was run again, the report read "7 building blocks" and had a seventh table column, a seventh bar and the node `b7["Test Block"]`. No file in the repository changed. | 13s |
| 6 | Pass. The proposed change was closed and the branch deleted. `main` has 6 building blocks and 5 claims, and its report is identical to `tests/fixtures/catalog_report_current/output.md`. | 6s |

### Row 1 and scope change (task T026)

- 2026-10-21: the user opened the artifact in a browser. The bar chart drew the full-coverage
  series over the total series, as research R2 expected. After viewing it, the user decided to
  keep only the coverage table and to build interactive charts in a separate front end later. The
  bar chart and the product map were removed from the transform, the tests and the expected
  outputs (spec, "Scope change"). Rows 4 and 5 above were run with both charts present. Their
  table results still apply.
