# Research: Proposed Change Checks for Catalog Submissions

## 1. How a check reads `main` while it runs on another branch

**Decision**: `validate()` in the submission check is `async`. It receives the branch's data like any
check, then reads `queries/catalog_records.gql` from `self.root_directory` and runs it on `main`
with `self.client.execute_graphql(..., branch_name="main")`.

**Rationale**:
- In Infrahub 1.11.8, the task worker creates the check with `branch=<branch name>`,
  `root_directory=<copy of the repository at the commit>` and an `InfrahubClient`, then calls
  `check.run()` (`backend/infrahub/git/integrator.py`, read in the local task worker container).
- `infrahubctl check` runs the query from the local file and passes the branch's data to
  `check.run(data)`, so it never calls `collect_data()`. A first version that overrode
  `collect_data()` failed under `infrahubctl` for this reason.
- Reading the query file from the repository copy works in both cases and does not depend on the
  stored query on `main` being up to date.

**Alternatives considered**:
- Overriding `collect_data()`: skipped by `infrahubctl`, see above.
- Reading the branch diff from Infrahub's diff API: the diff shape is not documented for checks
  and would tie the check to an internal format.
- Comparing in the web service before it opens the proposed change: a branch changed by other means
  after the submission would not be compared.

## 2. One check definition for each rule

**Decision**: four check definitions, each with its own class:
- `catalog_submission_check`;
- `catalog_duplicate_check`;
- `catalog_coverage_check`;
- `catalog_unused_source_check`.

They share one query, `catalog_records`, and live in one file, `checks/catalog_record_checks.py`.

**Rationale**: Infrahub shows one result for each check definition in a proposed change, so a
reviewer views which rule failed (FR-011). One file avoids imports between check files, which
Infrahub loads from a separate working copy for each commit.

**Alternatives considered**: one check with four groups of messages. A reviewer would have to read
every message to find which rule failed.

## 3. One shared query

**Decision**: `queries/catalog_records.gql` returns every publisher, product, source, coverage claim
and building block, with:
- every attribute the submission check compares;
- the IDs of the peers of each relationship the record owns;
- the counts of what each source supports;
- the count of each product's coverage claims.

**Rationale**: the catalog holds about 50 products, 110 claims and 100 sources, so one query is
small. The existing `catalog_source_check` query also reads every product and source without
paging.

## 4. Which relationships count as a record's own facts

**Decision**: the submission check compares only the relationships a record states about itself:
- product: `publisher`, `publisher_sources`, `description_sources`, `license_model_sources`,
  `status_sources`;
- coverage claim: `product`, `building_block`, `sources`.

The reverse sides are not compared: a publisher's products, a building block's claims, a source's
products and claims, and a product's claims.

**Rationale**: a new product links to an existing publisher, building blocks and sources, which
adds peers to the reverse side of those records (FR-004). A change to a record's own side, such as a
new source for an existing product's description, changes a fact of that record (FR-003).

## 5. Normalising names and links

**Decision**:
- Names: lower case, then keep only letters and digits. When nothing is left, use the name as
  written (spec edge case).
- Links: trim, lower case, remove a leading `http://` or `https://`, and remove trailing `/`.

Pairs are found by grouping records by the normalised value. Each group of two or more is reported
once for each pair, in name order.

## 6. "Warning" results

**Decision**: the coverage check uses `log_info()` with a message that starts with "Warning:".

**Rationale**: `InfrahubCheck` has `log_error()` and `log_info()` only. `log_info()` does not
affect the result.

## 7. Findings already on `main`

**Decision**: before the checks are pushed, run checks 2 to 4 by hand on `main`, and correct any
finding through a proposed change (spec edge case, SC-004).
