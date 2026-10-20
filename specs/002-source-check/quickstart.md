# Quickstart: Validate the Source Check

**Feature**: [spec.md](./spec.md) | **Data model**: [data-model.md](./data-model.md) |
**Contract**: [contracts/check-results.md](./contracts/check-results.md)

## Prerequisites

- The local instance is running and `uv run infrahubctl info` shows `http://localhost:8100` as
  connected.
- `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec`
- The check, its query, its tests and the new `.infrahub.yml` are committed on `main` and pushed
  to GitHub.
- The repository is registered from `bootstrap/repository.yml`, and Infrahub lists
  `catalog_source_check` under **Actions > Check Definitions**.

## Demo arc

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | `uv run pytest tests/` | All smoke and unit tests pass, including the fixtures that must fail the check. | ~20s | SC-001, SC-002 |
| 2 | `uv run infrahubctl check catalog_source_check --branch main --format-json` | The check passes and lists no products or sources, because all sources were checked on 2026-10-20. | ~15s | SC-002 |
| 3 | Create the Infrahub branch `demo-source-check`. On it, add a product with a license model and no license model source, and set one source's last-checked date to 2026-01-01. | Both edits are saved on the branch. | ~90s | SC-001 |
| 4 | Open a proposed change from `demo-source-check` to `main` | Within 5 minutes the "User" check shows as failed. It names the product with the add-a-source message, and lists the old source as due for review. | ~3m | SC-001, SC-003, SC-004 |
| 5 | Try to merge the proposed change | Infrahub does not allow the merge while the check is failing. | ~15s | SC-005 |
| 6 | Add a license model source to the product, then select **Retry** on the check | The check passes. The old source is still listed as due for review, and the merge is allowed. | ~90s | SC-002, SC-004 |
| 7 | Close the proposed change without merging and delete the branch | `main` is unchanged. | ~30s | SC-005 |

Total time: about 7 minutes 20 seconds.

## Results

### Check run by hand (tasks T012 and T018)

- **T012, 2026-10-20, Infrahub branch `test-us1`**: a product "Test License Without Source" with
  license model `commercial` and no license model source. The check exited with status 1 and
  logged one `ERROR`: "OpsMill Test License Without Source: the license model has no source. Add
  a license model source or remove the license model." The same command on `main` exited with
  status 0 and logged no errors. The branch was deleted.
- **T018, 2026-10-20, Infrahub branch `test-us2`**: sources set to 2026-04-19 (6 months and 1 day
  earlier), 2026-04-20 (exactly 6 months earlier) and 2099-01-01. The check exited with status 1.
  It logged an `ERROR` for the source dated 2099-01-01 and an `INFO` "Due for review" for the
  source dated 2026-04-19. It did not mention the source dated 2026-04-20. After the 2099 date was
  reset to 2026-10-20, the check exited with status 0 and still listed the 2026-04-19 source as
  due for review. The branch was deleted.

### Repository registration (task T025)

- 2026-10-20: `uv run infrahubctl object load bootstrap/repository.yml` created the read-only
  repository with one load. No uniqueness error, so the task workers were not scaled down. The
  repository reached `sync_status` `in-sync` and `operational_status` `online` at commit
  `43f1779`, and Infrahub listed the check definition `catalog_source_check`.

### Demo arc (task T026)

Run on 2026-10-20. The proposed change was opened, checked, merged and closed through Infrahub's
GraphQL API, which applies the same rules as the web interface.

| # | Outcome | Time |
|---|---|---|
| 1 | Pass. 18 tests passed. | under 1s |
| 2 | Pass. The check passed on `main` and listed nothing. | 1s |
| 3 | Pass. On `demo-source-check`, the product "Demo Product" (license model `commercial`, no license model source) was added and the Ansible README source was set to 2026-01-01. | 3s |
| 4 | Pass. 20 seconds after the proposed change opened, "Check: catalog_source_check" completed with conclusion `failure`. It showed the license model error for "OpsMill Demo Product" and the "Due for review" message for the Ansible README. Data Integrity and Schema Integrity passed. | 22s |
| 5 | Pass. The merge was refused: "Unable to merge proposed change containing failing checks". | under 5s |
| 6 | Pass. After a license model source was added and the check was run again, it completed with conclusion `success` and still listed the Ansible README as due for review. The change was not merged, as row 7 requires. | 17s |
| 7 | Pass. The proposed change was closed and the branch deleted. `main` still has 3 products, and the check on `main` passes with nothing listed. | 4s |

Observation: the proposed change showed no separate validator for the repository's `pytest`
tests. Run them with `uv run pytest tests/` before pushing.
