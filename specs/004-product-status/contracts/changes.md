# Contract: Changes to the Check, the Report and the Object Files

## Source check (`checks/catalog_source_check.py`, `queries/catalog_source_check.gql`)

The query adds `status { value }` and `status_sources { count }` to each product. New error:

| Level | Message |
|-------|---------|
| Error | `<full name>: the status is <status> but has no source. Add a status source.` |

## Coverage report (`transforms/catalog_report.py`, `queries/catalog_report.gql`)

The query adds `status { value }` to each product. In the table, a product that is not active is
written as `<full name> (<status>)`. Active products are unchanged.

## Object files (`objects/04_products.yml`)

```yaml
- name: <product name>
  publisher: <publisher name>
  ...
  status: discontinued              # omit for active products
  status_date: "2025-02-24T00:00:00Z"   # omit when no source states it
  status_sources: [<source URL>]
```
