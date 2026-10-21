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

To be filled in when the arc is run.
