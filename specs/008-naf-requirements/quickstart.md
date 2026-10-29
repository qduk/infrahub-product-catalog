# Quickstart: Framework Requirements and Coverage Assessments

Prerequisites: the local instance runs on port 8100, `INFRAHUB_API_TOKEN` is set to the local admin
token, and the catalog service and web app run as in `frontend/README.md`.

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | Run `uv run pytest tests/`, `cd frontend/api && uv run pytest` and `cd frontend/web && npm test` | All pass, including the extent rule and the verdict check. | ~30s | SC-004 |
| 2 | Compare the Intent, Executor and Observability requirements in Infrahub with the reference page | Same levels, text and order; split sentences appear as two records. | ~2m | SC-001 |
| 3 | Run `uv run infrahubctl check catalog_verdict_check --branch main --format-json` | No ERROR: every verdict other than not shown has a source. | ~20s | SC-002, SC-003 |
| 4 | Open the web app, click NetBox, read the Intent section | Each MUST and SHOULD not met is listed first with verdict, note and source. | ~30s | SC-005 |
| 5 | Set the coverage filter to "full" | Only claims whose MUST and SHOULD are all met remain; matches the coverage report. | ~45s | SC-004 |
| 6 | Submit a product through the form | No full or partial choice; the new claim shows as "not assessed" with a dashed line. | ~90s | SC-004 |
| 7 | On the submission branch, add verdicts that meet every MUST and SHOULD, and run the checks | The claim becomes full; all checks pass. | ~2m | SC-004 |

Total: about 8 minutes.
