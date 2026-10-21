# Research: products from the Network Automation Map (2026-10-21)

Research behind the 47 products added to `objects/02_sources.yml`, `03_publishers.yml` and
`04_products.yml` on 2026-10-21. The products come from the Network Automation Map screenshot the
user supplied, and are mapped to the six building blocks of the Network Automation Framework.

- `batch1.json` to `batch6.json`: one entry per product with the publisher, description, license
  model and coverage claims, each with the source URL and the exact quote that supports it, plus
  notes on judgment calls. Each research agent opened every page and checked that each quote
  appears in the page text, except where an entry's notes say otherwise.
- `merge.py`: the script that turned the batches into object file entries. It records the
  decisions made with the user:
  - publisher names without legal suffixes;
  - product names without the publisher's brand;
  - the status of Skybox Security (discontinued), System Initiative (discontinued) and Pliant
    (acquired).

The extents (full or partial) are the researchers' reading of each source. None of the sources uses
the framework's building block names.
