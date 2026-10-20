# Data Model: Source Check for Catalog Changes

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

This feature changes no schema. It reads two node types from `schemas/catalog.yml` (feature 001)
and adds one repository registration.

## Data the check reads

| Node | Field | Used for |
|------|-------|----------|
| `CatalogProduct` | `id`, `__typename` | Linking each message to the product. |
| `CatalogProduct` | `full_name` | Naming the product in the message (FR-001). |
| `CatalogProduct` | `license_model` | The rule applies only when this is set. |
| `CatalogProduct` | `license_model_sources` (count) | 0 means no source (FR-001). |
| `CatalogSource` | `id`, `__typename` | Linking each message to the source. |
| `CatalogSource` | `title`, `url` | Naming the source in the message (FR-003). |
| `CatalogSource` | `last_checked` | Comparing with the review age and with today (FR-003, FR-006). |

## Rules and results

| Condition | Result | Blocks the merge | Requirement |
|-----------|--------|------------------|-------------|
| Product has a license model and 0 license model sources | Error | Yes | FR-001, FR-002 |
| Source `last_checked` is later than today | Error | Yes | FR-006 |
| Source `last_checked` is earlier than today minus 6 calendar months | Information | No | FR-003, FR-004, FR-005 |
| Source `last_checked` is exactly today minus 6 calendar months, or later (up to today) | Nothing reported | No | Spec edge case |
| No products or no sources | Nothing reported, check passes | No | Spec edge case |

"Today" is the date, in UTC, on which the check runs.

## Repository registration

| Node | Field | Value |
|------|-------|-------|
| `CoreReadOnlyRepository` | `name` | `infrahub-product-catalog` |
| `CoreReadOnlyRepository` | `location` | `https://github.com/qduk/infrahub-product-catalog.git` |
| `CoreReadOnlyRepository` | `ref` | `main` |

No credential. Loaded once from `bootstrap/repository.yml` (research R7).
