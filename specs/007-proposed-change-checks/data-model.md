# Data Model: Proposed Change Checks for Catalog Submissions

No schema change. The checks read the catalog schema in `schemas/catalog.yml`.

## Query `catalog_records`

One stored query, used by all four checks. For each kind it returns `id`, `__typename` and the
fields below.

| Kind | Attributes | Own relationships (peer IDs) | Counts |
|------|------------|------------------------------|--------|
| `CatalogPublisher` | `name`, `homepage_url` | none | none |
| `CatalogProduct` | `name`, `full_name`, `description`, `homepage_url`, `license_model`, `status`, `status_date` | `publisher`, `publisher_sources`, `description_sources`, `license_model_sources`, `status_sources` | `coverage_claims` |
| `CatalogSource` | `title`, `url`, `last_checked` | none | `publisher_of_products`, `description_of_products`, `license_model_of_products`, `status_of_products`, `coverage_claims` |
| `CatalogCoverageClaim` | `extent`, `note` | `product`, `building_block`, `sources` | none |
| `CatalogBuildingBlock` | `name`, `description`, `definition_url` | none | none |

`display_label` is also read for every record, so messages name records the way Infrahub's web
interface does.

## Record snapshot used by the submission check

For each record on a branch: `kind`, `id`, label, and a map of fact name to value. A single peer is
its ID, and a list of peers is a sorted list of IDs. Counts are not part of the snapshot.

Comparison of `main` with the branch:
- a record on `main` with no record of the same ID on the branch is **deleted** (FR-002);
- a record on both whose value differs for any fact is **changed**, and each changed fact is named
  (FR-003);
- a `CatalogBuildingBlock` on the branch with no record of the same ID on `main` is **added**
  (FR-005);
- any other record on the branch only is a new record and is allowed.

## Rules for the other checks

| Check | Records | Result |
|-------|---------|--------|
| `catalog_duplicate_check` | publishers by normalised name; products by publisher ID and normalised name; sources by normalised link | `log_error` once for each pair |
| `catalog_coverage_check` | products with a `coverage_claims` count of 0 | `log_info`, text starts with "Warning:" |
| `catalog_unused_source_check` | sources whose five counts are all 0 | `log_error` |

Normalisation is described in [research.md](./research.md) section 5.
