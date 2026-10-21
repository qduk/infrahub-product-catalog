# Data Model: Catalog Coverage Report

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## New node: CatalogReport

Added to `schemas/catalog.yml` (research R3). It stands for a report about the whole catalog, so
that Infrahub has an object to attach the report to.

| Field | Kind | Required | Rules |
|-------|------|----------|-------|
| `name` | Text | yes | Unique. |
| `description` | TextArea | no | What the report shows. |

- `inherit_from: [CoreArtifactTarget]`.
- Human-friendly ID `[name__value]`. Display label `name__value`.
- `generate_profile: false`, `include_in_menu: true`, icon `mdi:chart-bar`.
- No relationships to other catalog nodes. The report reads the whole catalog through its query.

## Data loaded

| File | Content |
|------|---------|
| `objects/05_reports.yml` | A `CoreStandardGroup` named `catalog_reports`, then one `CatalogReport` named "Catalog coverage report", a member of that group through `member_of_groups`. |

## Data the transform reads

| Node | Fields |
|------|--------|
| `CatalogReport` | `name` (the target, selected with the query variable `$report`) |
| `CatalogBuildingBlock` | `name` |
| `CatalogProduct` | `full_name`, and its `coverage_claims` with each claim's `extent` and `building_block.name` |

## Derived values

| Value | Rule |
|-------|------|
| Block order | Building block names, sorted case-insensitively (research R5). |
| Product order | Product full names, sorted case-insensitively. |
| Cell in the table | "Full", "Partial" or "—" for each product and block. |
| Bar chart values | For each block: number of claims (all products) and number of full claims. |
| Diagram lines | One per claim: `==>` for full, `-.->` for partial. |
