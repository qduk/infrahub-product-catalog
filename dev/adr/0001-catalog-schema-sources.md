---
status: accepted
date: 2026-10-20
---

# Link each product fact to its own sources, and identify products by a computed full name

## Context and problem statement

The catalog records network automation products and the building blocks of the Network Automation
Framework that they cover. Constitution Principle III requires every fact to link to its source,
and the feature spec ([FR-009](../../specs/001-catalog-schema/spec.md)) requires each fact on a
product (publisher, description, license model) to link to its own source.

Two products from different publishers can have the same name (FR-012). Coverage claims need a
human-friendly ID so that object files and the web interface can refer to them.

Both decisions were tested on a throwaway Infrahub branch. The evidence is in
[research.md](../../specs/001-catalog-schema/research.md), sections R3 and R7.

## Decision drivers

- A reader can tell which source supports which product fact.
- Infrahub enforces the rule that a fact has a source, without a separate check.
- Maintainers can record everything in object files.
- A coverage claim has a unique, readable identifier even when two publishers use the same
  product name.

## Considered options for product fact sources

1. One relationship from `CatalogProduct` to `CatalogSource` for each fact: `publisher_sources`,
   `description_sources` and `license_model_sources`.
2. The `source` property on each attribute.
3. A separate "fact" node for each product fact, with its own sources.

## Decision outcome for product fact sources

Chosen option: 1. Infrahub refuses a product without `publisher_sources` or `description_sources`,
because both are required with `min_count: 1`. Object files fill them by source URL.

Option 2 holds one value, is meant for data lineage (accounts and repositories), and it is not
known whether object files can set it. Option 3 turns every product attribute into a node, which
makes products harder to record and read.

### Consequences

- Each new product fact that needs a source needs its own relationship and a schema change.
- The schema cannot require `license_model_sources` only when `license_model` is set. Reviewers
  check this rule until a check is built.

## Considered options for identifying claims

1. A claim ID of product name and building block name.
2. A claim ID that reaches from the claim through the product to the publisher name.
3. A computed, read-only, unique `full_name` on the product ("publisher name" + "product name"),
   and a claim ID of `full_name` and building block name.

## Decision outcome for identifying claims

Chosen option: 3. Infrahub rejected option 1 because the product name is not unique, and rejected
option 2 because an ID can reach through only one relationship.

### Consequences

- When a product moves to another publisher, its `full_name` and the IDs of its claims change.
- Object files refer to products by `[publisher name, product name]` and to claims by
  `[full name, building block name]`.
