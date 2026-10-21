# Quickstart: Validate Product Status

**Feature**: [spec.md](./spec.md) | **Data model**: [data-model.md](./data-model.md) |
**Contract**: [contracts/changes.md](./contracts/changes.md)

## Prerequisites

- The local instance is running, and `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec`.
- The schema change is loaded on the Infrahub branch `product-status`.

## Demo arc

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | Load the schema on `product-status` and read the three existing products | Each reads `status: active` with no change to `objects/04_products.yml`. | ~60s | SC-003 |
| 2 | `uv run pytest tests/` | All tests pass, including the new status fixtures and the unchanged report outputs. | ~20s | SC-001, SC-003 |
| 3 | On a test branch, set a product to `discontinued` with no status source and run the source check by hand | The check fails and names the product. | ~60s | SC-001 |
| 4 | Add a status source and run the check again | The check passes. | ~30s | SC-001 |
| 5 | Run the report transform on that branch | The product's row reads `<full name> (discontinued)`. Other rows are unchanged. | ~30s | SC-004 |
| 6 | After merging and importing the new commit, rebuild the report on `main` | The report is identical to `tests/fixtures/catalog_report_current/output.md`. | ~2m | SC-003 |

Total time: about 5 minutes 20 seconds. SC-002 (recording the three known cases) is met when the
products from the Network Automation Map are loaded, which follows this feature.

## Results

To be filled in when the arc is run.
