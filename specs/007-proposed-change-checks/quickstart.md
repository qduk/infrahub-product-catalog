# Quickstart: Proposed Change Checks for Catalog Submissions

Prerequisites:
- The local instance is running on port 8100.
- `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec` (local instance only).
- For rows 6 and 7: the checks are pushed to GitHub and **Import latest commit** has been run.

Expected messages are in [contracts/check-results.md](./contracts/check-results.md).

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | Run `uv run pytest tests/` | All tests pass, including the cases for the four new checks. | ~10s | SC-001, SC-002, SC-003 |
| 2 | Run each new check by hand on `main`: `uv run infrahubctl check <name> --branch main --format-json` | No ERROR entries; `catalog_submission_check` says it applies only to submission branches. | ~40s | SC-004 |
| 3 | Create branch `submission-qs-edit`, change the description of an existing product, and run `catalog_submission_check` on it | One ERROR naming the product and `description`. | ~60s | SC-001, SC-005 |
| 4 | On branch `qs-dupes`, add a publisher named like an existing one with other case and spacing, and a source that supports nothing; run `catalog_duplicate_check` and `catalog_unused_source_check` | One ERROR naming both publishers; one ERROR naming the source and its link. | ~90s | SC-002, SC-003 |
| 5 | On branch `qs-dupes`, add a product with no coverage claim and run `catalog_coverage_check` | One INFO entry starting with "Warning:" naming the product; the check passes. | ~45s | SC-003 |
| 6 | Submit a product through the web app and open its proposed change in Infrahub | The four new checks appear by name and pass. | ~90s | SC-001, SC-006 |
| 7 | Open a proposed change for `submission-qs-edit` | `catalog_submission_check` fails and the merge is blocked. | ~60s | SC-001, SC-005 |
| 8 | Delete the test branches | The branches are gone. | ~30s | none |

Total: about 7 minutes.
