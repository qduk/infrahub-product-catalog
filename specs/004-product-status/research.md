# Research: Product Status

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-21

## R1. How the status is stored

- **Decision**: add to `CatalogProduct`:
  - `status`: Dropdown with choices `active`, `discontinued` and `acquired`, required, with
    `default_value: active`;
  - `status_date`: DateTime, optional;
  - `status_sources`: relationship to `CatalogSource`, cardinality many, optional, identifier
    `product__status_sources`, with the inverse `status_of_products` on `CatalogSource`.
- **Rationale**:
  - A Dropdown limits the value to the three statuses in FR-001.
  - A required attribute with a default value can be added to nodes that are already loaded,
    because the default fills the existing products (schemas skill, `migration-state-absent` and
    `validation.md`). This meets FR-002 with no change to `objects/04_products.yml`.
    Implementation confirms on a branch that the three loaded products read `active`.
  - `status_sources` follows the pattern of `publisher_sources`, `description_sources` and
    `license_model_sources` (feature 001, research R3).
  - The schema skill's attribute reference lists no date-only kind, so `status_date` uses
    DateTime, like `CatalogSource.last_checked`.
- **Alternatives considered**: a separate status-history node with one row per change. Rejected,
  because the spec asks only for the current status.

## R2. Requiring a source for a non-active status (FR-005)

- **Decision**: add a rule to the existing `catalog_source_check`. The query reads
  `status { value }` and `status_sources { count }`, and the check logs an error when the status is
  `discontinued` or `acquired` and the count is 0.
- **Rationale**: the schema cannot make `status_sources` required only for some values of
  `status`, which is the same gap as the license model rule (feature 002, research R4).

## R3. Showing status in the report (FR-006)

- **Decision**: in the coverage table, write the status in brackets after the product name for
  products that are not active, for example `Skybox Security Skybox Firewall Assurance
  (discontinued)`. Active products keep their current row, so a catalog with only active products
  gives a report identical to today's (SC-003). The existing expected-output files stay unchanged.
- **Alternatives considered**: a "Status" column. Rejected because it changes every row of the
  report even when every product is active, and the user is building their own front end for
  richer views.

## R4. Dates known only to the month or year

- **Decision**: record the first day of the stated month or year, at 00:00 UTC. The status source
  says the real precision.
