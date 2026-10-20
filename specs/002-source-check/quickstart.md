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
