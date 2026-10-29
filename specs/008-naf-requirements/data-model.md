# Data Model: Framework Requirements and Coverage Assessments

Changes to `schemas/catalog.yml`. Namespace `Catalog`.

## New node `CatalogRequirement`

| Field | Kind | Notes |
|-------|------|-------|
| `identifier` | Text, unique | `intent-must-1`, `framework-should-2`. HFID and display label. |
| `level` | Dropdown: `must`, `should`, `may` | |
| `position` | Number | Order on the reference page. `order_by` uses it. |
| `summary` | Text | Short title in the catalog's own words; tells apart two requirements recorded from one sentence. |
| `statement` | TextArea | Quoted from the reference. |
| `reference_url` | URL | Link to the section of the reference page. |
| `building_block` | relationship, cardinality one, optional, peer `CatalogBuildingBlock`, identifier `building_block__requirements` | None for framework-wide requirements. |
| `verdicts` | relationship, cardinality many, peer `CatalogRequirementVerdict`, identifier `requirement__verdicts` | Inverse. |

`CatalogBuildingBlock` gains the inverse `requirements`.

## New node `CatalogRequirementVerdict`

| Field | Kind | Notes |
|-------|------|-------|
| `verdict` | Dropdown: `met`, `partly_met`, `not_met`, `not_shown` | Labels: Met, Partly met, Not met, Not shown by any source. |
| `note` | TextArea, optional | What the source says, in neutral words. |
| `claim` | Parent, cardinality one, peer `CatalogCoverageClaim`, identifier `coverage_claim__verdicts` | |
| `requirement` | Attribute, cardinality one, peer `CatalogRequirement`, identifier `requirement__verdicts` | |
| `sources` | Attribute, cardinality many, optional, peer `CatalogSource`, identifier `verdict__sources` | Required by `catalog_verdict_check` unless `not_shown`. |

- `uniqueness_constraints`: `[["claim", "requirement"]]`.
- `human_friendly_id`: `[claim__name__value, requirement__identifier__value]`.
- `display_label`: `"{{ claim__name__value }} - {{ requirement__identifier__value }}"`.

`CatalogSource` gains the inverse `verdicts`.

## Changed node `CatalogCoverageClaim`

- `extent`: `state: absent`.
- New `name`: Text, computed (Jinja2 `{{ product__full_name__value }} - {{ building_block__name__value }}`),
  `read_only: true`, unique.
- New `verdicts`: Component, cardinality many, peer `CatalogRequirementVerdict`, identifier
  `coverage_claim__verdicts`, `on_delete: cascade`.

## Computed extent (FR-007)

For a claim of block B, the requirements that apply are those with `building_block` = B or no
building block, and each gets a verdict. The claim is `full` when every requirement of block B of
level `must` or `should` has a verdict `met`; otherwise `partial`. Framework-wide verdicts are shown
but do not count (user decision, 2026-10-27). A claim is "not assessed" when it has no verdicts.

## Object files

| File | Change |
|------|--------|
| `objects/01_building_blocks.yml` | Second document: the 34 `CatalogRequirement` records, generated from `dev/knowledge/naf-requirements-2026-10-23/requirements.json`. |
| `objects/04_products.yml` | `extent` removed from every claim. |
| `objects/06_requirement_verdicts.yml` | New: approved verdicts. |
