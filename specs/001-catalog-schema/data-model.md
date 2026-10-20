# Data Model: Network Automation Product Catalog Schema

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

Namespace: `Catalog`. Schema file: `schemas/catalog.yml`. Every node sets
`generate_profile: false` and uses the default menu.

## CatalogBuildingBlock

One building block of the Network Automation Framework (FR-001, FR-002).

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `name` | Text | yes | Unique. Written exactly as the framework writes it. |
| `description` | TextArea | yes | Quoted from the framework. |
| `definition_url` | URL | yes | Link to the framework's definition of the block. |
| `coverage_claims` | relationship to `CatalogCoverageClaim`, many | no | Inverse of `CatalogCoverageClaim.building_block`. Identifier `building_block__coverage_claims`. |

- Human-friendly ID: `[name__value]`. Display label: `name__value`. Ordered by `name__value`.

## CatalogPublisher

The company, foundation or open-source project that publishes products (FR-004).

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `name` | Text | yes | Unique. |
| `homepage_url` | URL | yes | |
| `products` | relationship to `CatalogProduct`, many | no | Inverse of `CatalogProduct.publisher`. Identifier `publisher__products`. |

- Human-friendly ID: `[name__value]`. Display label: `name__value`.

## CatalogSource

A document that supports facts in the catalog (FR-008).

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `title` | Text | yes | |
| `url` | URL | yes | Unique. |
| `last_checked` | DateTime | yes | When the maintainer last confirmed the source. |
| `coverage_claims` | relationship to `CatalogCoverageClaim`, many | no | Inverse of `CatalogCoverageClaim.sources`. Identifier `coverage_claim__sources`. |
| `publisher_of_products` | relationship to `CatalogProduct`, many | no | Inverse of `CatalogProduct.publisher_sources`. Identifier `product__publisher_sources`. |
| `description_of_products` | relationship to `CatalogProduct`, many | no | Inverse of `CatalogProduct.description_sources`. Identifier `product__description_sources`. |
| `license_model_of_products` | relationship to `CatalogProduct`, many | no | Inverse of `CatalogProduct.license_model_sources`. Identifier `product__license_model_sources`. |

- Human-friendly ID: `[url__value]`. Display label: `title__value`.

## CatalogProduct

A network automation product (FR-003, FR-009, FR-012).

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `name` | Text | yes | Unique per publisher. |
| `full_name` | Text, computed | yes | Read-only. Template `{{ publisher__name__value }} {{ name__value }}`. Unique. |
| `description` | TextArea | yes | Neutral wording (constitution Principle III). |
| `homepage_url` | URL | yes | Needs no separate source. |
| `license_model` | Dropdown | no | Choices: `open_source`, `open_core`, `commercial`. Left empty when no source states it. |
| `publisher` | relationship to `CatalogPublisher`, one | yes | Kind Attribute. Identifier `publisher__products`. |
| `publisher_sources` | relationship to `CatalogSource`, many | yes, at least 1 | Identifier `product__publisher_sources`. |
| `description_sources` | relationship to `CatalogSource`, many | yes, at least 1 | Identifier `product__description_sources`. |
| `license_model_sources` | relationship to `CatalogSource`, many | no | Identifier `product__license_model_sources`. |
| `coverage_claims` | relationship to `CatalogCoverageClaim`, many | no | Kind Component, `on_delete: cascade`. Identifier `product__coverage_claims`. |

- Uniqueness: `["publisher", "name__value"]`.
- Human-friendly ID: `[publisher__name__value, name__value]`. Display label: `full_name__value`.

## CatalogCoverageClaim

A statement that one product covers one building block (FR-005 to FR-007).

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `extent` | Dropdown | yes | Choices: `full`, `partial`. |
| `note` | TextArea | no | |
| `product` | relationship to `CatalogProduct`, one | yes | Kind Parent. Identifier `product__coverage_claims`. |
| `building_block` | relationship to `CatalogBuildingBlock`, one | yes | Kind Attribute. Identifier `building_block__coverage_claims`. |
| `sources` | relationship to `CatalogSource`, many | yes, at least 1 | Kind Attribute. Identifier `coverage_claim__sources`. |

- Uniqueness: `["product", "building_block"]`.
- Human-friendly ID: `[product__full_name__value, building_block__name__value]`.
- Display label: `{{ product__full_name__value }} - {{ building_block__name__value }}`.

## Rules that Infrahub enforces

| Requirement | Enforced by | Tested |
|-------------|-------------|--------|
| A claim needs at least one source (FR-006) | `sources` required, `min_count: 1` | yes (R4) |
| One claim per product and building block (FR-007) | uniqueness constraint | yes (R5) |
| A building block or source linked to a claim cannot be deleted (FR-011) | required relationships on the claim | yes (R6) |
| Same product name under two publishers (FR-012) | uniqueness per publisher, computed `full_name` | yes (R7) |
| Publisher and description need a source (FR-009) | required relationships, `min_count: 1` | yes (R3) |

## Rule that the schema cannot enforce

- A product with a `license_model` needs at least one `license_model_sources` entry. This needs a
  check, which is a separate feature. Until then, people who review data files check it.

## Lifecycle

- Deleting a product deletes its coverage claims.
- Deleting a publisher should be refused while products reference it, because `publisher` is
  required. This follows the same rule as research R6 but was not tested.
- Renaming a building block, publisher or product is done in the web interface first, then copied
  into the object files (research R8).
