# Data Model: Public Catalog Web App

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

No schema change. The app reads and writes the existing `Catalog` nodes.

## Catalog response (`GET /api/catalog`)

```text
Catalog
├── blocks: [ { name, description, definition_url } ]
├── publishers: [ { name, homepage_url } ]
└── products: [ {
      id, name, full_name, publisher, description, homepage_url,
      license_model (or null), status, status_date (or null),
      sources: { publisher: [Source], description: [Source], license_model: [Source], status: [Source] },
      claims: [ { block, extent, note (or null), sources: [Source] } ]
    } ]
Source = { title, url }
```

## Submission request (`POST /api/submissions`)

| Field | Rules |
|-------|-------|
| `product.name` | Required, 1–100 characters. Unique with the publisher on `main`. |
| `product.description` | Required, 1–1,000 characters. |
| `product.homepage_url` | Required, `http(s)` URL, up to 500 characters. |
| `product.license_model` | Optional: `open_source`, `open_core` or `commercial`. |
| `product.status` | `active` (default), `discontinued` or `acquired`. |
| `product.status_date` | Optional date. |
| `publisher` | Either `{existing: name}` or `{new: {name, homepage_url}}`. |
| `sources` | List of `{key, title, url}`, at most 20, URLs distinct. `key` is a local reference used by the fields below. |
| `fact_sources.publisher` | Required, at least one source key. |
| `fact_sources.description` | Required, at least one source key. |
| `fact_sources.license_model` | Required when a license model is set. |
| `fact_sources.status` | Required when the status is not `active`. |
| `claims` | At least one, at most one per building block. Each: `block` (an existing building block name), `extent` (`full` or `partial`), optional `note` up to 1,000 characters, at least one source key. |

## Submission response

| Case | Response |
|------|----------|
| Accepted | `201` with `{reference: "submission-20261021-a1b2c3"}` |
| Invalid | `422` with a list of `{field, message}` |
| Product already exists | `409` with a message |
| Saving failed | `502` with a message; no branch or proposed change is left |
