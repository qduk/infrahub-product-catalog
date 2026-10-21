# Data Model: Product Status

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Changes to `CatalogProduct` (`schemas/catalog.yml`)

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `status` | Dropdown | yes | Choices `active` (Active), `discontinued` (Discontinued), `acquired` (Acquired). `default_value: active`. |
| `status_date` | DateTime | no | When the status took effect, if a source states it (research R4). |
| `status_sources` | relationship to `CatalogSource`, many | no | Identifier `product__status_sources`. Required by the source check when `status` is not `active`. |

## Changes to `CatalogSource`

| Field | Kind | Rules |
|-------|------|-------|
| `status_of_products` | relationship to `CatalogProduct`, many | Inverse of `CatalogProduct.status_sources`. Identifier `product__status_sources`. |

## Status values

| Value | Meaning |
|-------|---------|
| `active` | The publisher sells or develops the product under its current name. |
| `discontinued` | The product is no longer developed or sold. |
| `acquired` | The product was absorbed into another company and is no longer offered on its own under its own name. |
