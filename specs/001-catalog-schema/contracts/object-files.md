# Contract: Catalog Object Files

Maintainers record catalog data in object files and load them with
`uv run infrahubctl object load objects/`. This contract fixes the file layout and the shape of
each entry. Field rules are in [data-model.md](../data-model.md).

## File layout and load order

Files load in name order. Each file only references nodes that earlier files create.

| File | Kind | References |
|------|------|------------|
| `objects/01_building_blocks.yml` | `CatalogBuildingBlock` | none |
| `objects/02_sources.yml` | `CatalogSource` | none |
| `objects/03_publishers.yml` | `CatalogPublisher` | none |
| `objects/04_products.yml` | `CatalogProduct`, with nested `CatalogCoverageClaim` | building blocks, sources, publishers |

## How entries reference each other

| Reference to | Written as | Example |
|--------------|-----------|---------|
| Building block | its name | `building_block: Executor` |
| Source | its URL | `sources: [https://example.org/docs]` |
| Publisher | its name | `publisher: Example Corp` |

## Entry shapes

```yaml
# objects/01_building_blocks.yml
---
apiVersion: infrahub.app/v1
kind: Object
spec:
  kind: CatalogBuildingBlock
  data:
    - name: Executor
      description: "Encompasses the actual tasks applied to the network to drive changes"
      definition_url: https://reference.networkautomation.forum/Framework/Framework/#executor
```

```yaml
# objects/04_products.yml
---
apiVersion: infrahub.app/v1
kind: Object
spec:
  kind: CatalogProduct
  data:
    - name: <product name>
      publisher: <publisher name>
      description: <neutral description>
      homepage_url: <link>
      license_model: open_source          # omit when no source states it
      publisher_sources: [<source URL>]
      description_sources: [<source URL>]
      license_model_sources: [<source URL>]
      status: discontinued              # omit for active products (feature 004)
      status_date: "2025-02-24T00:00:00Z"   # omit when no source states it
      status_sources: [<source URL>]    # required when status is not active
      coverage_claims:
        data:
          - building_block: Executor
            extent: partial
            note: <optional>
            sources: [<source URL>]
```

## Rules for maintainers

- Every source URL used in `04_products.yml` must be an entry in `02_sources.yml`.
- Leave `license_model` out when no source states it. When it is set, list its sources in
  `license_model_sources`.
- Rename a node in the web interface first, then change the file (research R8).
- `status` is `active`, `discontinued` or `acquired` (feature 004). Leave it out for active
  products. A discontinued or acquired product needs at least one `status_sources` entry, or the
  source check fails.
- Loading a file twice changes nothing.
