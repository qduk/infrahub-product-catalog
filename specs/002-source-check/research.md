# Research: Source Check for Catalog Changes

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-20

Findings marked "tested" come from a test check run with `infrahubctl check` against the throwaway
Infrahub branch `spike-002` of the local instance (Infrahub 1.11.8, infrahub-sdk 1.23.2). The
branch was deleted after the tests. Findings marked "docs" quote the Infrahub documentation in the
`opsmill/infrahub` repository, branch `stable`, which describes the current release and is not
pinned to 1.11.

## R1. How the repository is connected to Infrahub

- **Decision**: register the GitHub repository as a read-only repository
  (`CoreReadOnlyRepository`), location `https://github.com/qduk/infrahub-product-catalog.git`,
  `ref: main`, with no credential.
- **Rationale**:
  - A read-only repository "guarantees no modifications to the external repository"
    (docs, `git-integration/overview.mdx`), so Infrahub needs no write token for GitHub.
  - The repository is public. The docs ask for credentials only "for private repositories and or
    Read-Write repositories" (`git-integration/connect-repository.mdx`).
  - The only code that Infrahub needs from Git is the check. Data changes are made on Infrahub
    branches, not on Git branches, so Infrahub has no reason to mirror Git branches.
- **Consequence**: Infrahub "does not poll a read-only repository; you update it by changing the
  `ref` or using the **Import latest commit** action" (docs, `git-integration/overview.mdx`).
  After a change to the check is pushed to `main` on GitHub, a maintainer runs **Import latest
  commit**. This step goes in `AGENTS.md`.
- **Alternatives considered**: a read-write repository (`CoreRepository`). Rejected because it
  needs a GitHub token with write access, polls GitHub several times a minute, creates an Infrahub
  branch for every Git branch, and pushes merges back to GitHub. None of this is needed for one
  check.
- **Confirmed during implementation (task T026)**: the docs do not say which commit of a
  read-only repository's checks Infrahub uses for a proposed change whose source branch does not
  sync with Git. On 2026-10-20, a proposed change from such a branch ran `catalog_source_check`
  from the commit imported on `main` (`43f1779`) and blocked the merge (quickstart results,
  rows 4 and 5).

## R2. What the repository import loads

- **Decision**: `.infrahub.yml` lists only the check and its query. Remove the `schemas:` and
  `objects:` keys added in feature 001.
- **Rationale**: the docs list schemas, object files and menus among the resources Infrahub
  imports from `.infrahub.yml` (`git-integration/infrahub-yml.mdx`). A read-only repository with
  `ref: main` imports into the Infrahub branch `main`. If `objects:` stayed in the file, every
  import would write the object files straight into `main` and skip the proposed change, which is
  the step where this check runs. Schemas would skip review in the same way.
- **Consequence**: schema and object files are still loaded with
  `uv run infrahubctl schema load schemas/` and `uv run infrahubctl object load objects/` on an
  Infrahub branch, then merged through a proposed change. These commands take paths and do not
  read the `schemas:` or `objects:` keys. Feature 001's `contracts/object-files.md` already uses
  explicit paths.
- **Alternatives considered**: keep `objects:` so that Git becomes the way data reaches
  Infrahub. Rejected because data would then reach `main` without the check.

## R3. Whether a failed check blocks the merge

- **Decision**: report problems that must block with `log_error`, and sources due for review with
  `log_info`.
- **Rationale**:
  - Docs: "If a check does not complete successfully, the proposed change cannot be merged"
    (`checks/overview.mdx`) and "A failing check blocks the merge, except **Data Integrity**"
    (`proposed-changes/overview.mdx`).
  - Only `log_error` fails a check. `log_info` messages do not change the result
    (checks skill, `python-validate`).
- **Known gap**: a direct branch merge "skips the Proposed Change pipeline"
  (docs, `branches/merge.mdx`). FR-009 holds only when changes are merged through a proposed
  change. `AGENTS.md` and the maintainer guide already tell maintainers to merge that way.

## R4. Check logic

- **Decision**: one global check, `catalog_source_check`, with one query that reads every product
  and every source.
  - **Products**: `full_name`, `license_model` and `license_model_sources { count }`. A product
    whose license model is set and whose count is 0 is an error.
  - **Sources**: `title`, `url` and `last_checked`.
    - A date later than the day the check runs is an error.
    - A date earlier than the same day 6 calendar months before is reported with `log_info`.
    - A date exactly 6 months before is not reported. When the earlier month has no such day
      (for example 31 August becomes 31 February), the last day of that month is used.
- **Rationale**: tested. With a product that had a license model and no source, a source dated
  2026-04-19, a source dated 2026-04-20 and a source dated 2027-01-01, the check:
  - failed;
  - named the product and the future-dated source as errors;
  - reported 2026-04-19 as due for review;
  - did not report 2026-04-20.
  After the two errors were removed, the check passed with the old source still reported.
- **Why not a schema rule**: the schema cannot require a relationship only when an attribute is
  set, and the review age depends on the day the check runs (feature 001, research R3).

## R5. Viewing the results when running the check by hand (FR-010)

- **Decision**: maintainers run
  `uv run infrahubctl check catalog_source_check --branch <branch> --format-json`.
- **Rationale**: tested.
  - Without `--format-json`, `infrahubctl` prints messages only when the check fails, and then
    prints every message as `ERROR`, including sources that are only due for review. A passing
    check prints no messages, so the review list stays hidden (`infrahub_sdk/ctl/check.py`).
  - With `--format-json`, each message is printed with its own level (`ERROR` or `INFO`), and
    sources due for review appear even when the check passes.

## R6. Tests for the check

- **Decision**: add `tests/test_checks.yml` with:
  - a smoke test;
  - unit tests (`check-unit-process`) that use saved query results in `tests/fixtures/`.
  Add `pytest` to the `dev` dependency group, and run the tests with `uv run pytest tests/`.
- **Rationale**: the checks skill requires tests for every check. Infrahub also runs `pytest`
  against the repository's test files in the proposed change pipeline (common skill rule
  `testing-resource-framework`).
- **Fixture dates**: because the check compares dates with the day it runs, fixtures use dates
  that stay on the same side of the limit for decades:
  - 2000-01-01 for an old source;
  - 2099-01-01 for a future date.
  A fixture with a recent date would change result after 6 months.
- **Found during implementation (task T009)**: in infrahub-sdk 1.23.2, a `check-unit-process`
  test with `expect: FAIL` passes even when the check passes. The plugin only reports a problem
  when a check fails while expected to pass (`infrahub_sdk/pytest_plugin/items/check.py`,
  `InfrahubCheckUnitProcessItem.runtest`). The YAML tests therefore cannot show that the check
  catches a problem. `tests/test_catalog_source_check.py` runs the check on the same fixtures and
  asserts the exact error and information messages. It also sets the date the check treats as
  today, so it can test the 6-month boundary.
- **No integration test**: a `check-integration` test needs a running server, and the pipeline's
  task worker would run it against whatever data is on the branch. Quickstart rows cover the live
  checks instead.

## R7. Registering the repository

- **Decision**: keep the repository registration in `bootstrap/repository.yml`, outside
  `objects/`, and load it once with `uv run infrahubctl object load bootstrap/repository.yml`.
- **Rationale**: the common skill rule `deployment-git-integration` says to keep the repository
  definition out of `objects/`, so that it is never loaded together with catalog data. The same
  rule says to register the repository only after every referenced file is committed and pushed,
  because Infrahub clones the committed state.
- **Setup risk**: the local instance runs two task workers. The same rule warns that two workers
  can import a new repository at the same time and hit uniqueness errors. If the first import
  fails this way, scale to one worker with `docker compose up -d --scale task-worker=1`, register
  the repository, then scale back.

## R8. Amendment to the constitution and AGENTS.md

- **Decision**: amend constitution Principle II and update `AGENTS.md` in this feature.
- **Rationale**: Principle II says transforms, generators and checks are run with `infrahubctl`
  "because this repository is not connected to the instance as a Git repository". `AGENTS.md`
  says the same. Both become wrong once the repository is connected.
- **Version**: 1.0.0 → 1.1.0. The rule is extended, because checks now also run on proposed
  changes, and no earlier work becomes non-compliant. The constitution's governance section
  classes this as MINOR. Run through `/speckit-constitution`, and record the decision in
  `dev/adr/0002-connect-repository-read-only.md`, because it changes how the instance is set up.
