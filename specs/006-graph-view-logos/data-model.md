# Data Model: Graph View with Logos

No change to the catalog or the service. The web app derives graph nodes and edges from
`GET /api/catalog` (feature 005).

| Graph element | From | Shown as |
|---------------|------|----------|
| Block node | each building block | Large rounded node in the block's colour, with its name and tagline |
| Product node | each product with at least one claim that passes the filters | Small node: logo tile (or initials), full name, status label when not active |
| Edge | each claim that passes the filters | Line from the product to the block: solid for full, dashed for partial |

## Logo manifest entry (`src/graph/logos.json`)

| Field | Meaning |
|-------|---------|
| `slug` | Product full name in lower case, with other characters replaced by `-` |
| `file` | File name in `public/logos/`, or null when no official logo was found |
| `logo_of` | `product` or `publisher` |
| `source_page` | The page the logo was found on |
| `file_url` | The address the file was downloaded from |
| `brand_guidelines_url` | The publisher's logo-use page, or null |
| `notes` | Anything a maintainer should know |
