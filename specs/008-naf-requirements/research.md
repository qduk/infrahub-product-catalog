# Research: Framework Requirements and Coverage Assessments

## 1. Where the extent is computed

**Decision**: remove `extent` from `CatalogCoverageClaim` (`state: absent`). Compute it where it is
read, from the claim's verdicts and the requirements that apply:
- the catalog service (`frontend/api/catalog_web/catalog.py`), which gives it to the web app;
- the coverage report transform (`transforms/catalog_report.py`).

Both use the same rule (FR-007), each with its own tests.

**Rationale**:
- With no field, the extent cannot be set by hand anywhere (FR-008).
- Jinja2 computed attributes read only attributes of the node and of cardinality-one peers, so they
  cannot count a claim's verdicts (`infrahub-managing-schemas`, attribute-computed-jinja2).
- Python-transform computed attributes run on the task workers from the connected repository. That
  is the path where Infrahub 1.11.8 fails for read-only repositories (`run_user_check` looks the
  repository up as `CoreRepository`; found in feature 007's deployment). The same risk applies.

**Alternatives considered**:
- Python-transform computed attribute: rejected for the risk above, and because it recomputes
  asynchronously, so a reader could see a stale value.
- Keep `extent` and add a check that it matches the verdicts: rejected because a maintainer would
  still set it by hand, against FR-008.

## 2. Identity of verdicts

**Decision**: add a computed, unique `name` to `CatalogCoverageClaim`
(`{{ product__full_name__value }} - {{ building_block__name__value }}`, the current display label).
A verdict's `human_friendly_id` is `[claim__name__value, requirement__identifier__value]`.

**Rationale**: constitution Principle V requires a `human_friendly_id` on every node. An HFID cannot
go through two relationships (found in feature 001), so the claim needs its own attribute.
`CatalogProduct.full_name` already uses the same Jinja2 pattern.

## 3. Requirement records

**Decision**: one `CatalogRequirement` per keyword (34 in total), identified as `<block>-<level>-<n>` (for example
`intent-should-2`) or `framework-should-<n>` for framework-wide ones. `position` keeps the order of
the reference page. The text is quoted from the page as of 2026-10-23.

Splits (FR-002):
- Executor: "It MAY support both imperative approaches ... In both cases, the operation SHOULD be
  idempotent" becomes `executor-may-1` and `executor-should-5`.
- Observability: "It SHOULD expose relevant insights ... These events MAY be processed by humans or
  connected to the Orchestration block" becomes `observability-should-2` and `observability-may-1`.
- Framework-wide: "All components SHOULD follow modern software engineering practices ... and expose
  machine-friendly APIs" becomes `framework-should-1` (practices) and `framework-should-2` (APIs).

Not recorded: "all the blocks MAY be implemented by one or more components" (spec edge cases), and
the Presentation sentence "It is designed to interface with any of the other building blocks",
which has no keyword.

## 4. Object files

**Decision**:
- Requirements: a second document in `objects/01_building_blocks.yml`, so they load right after the
  blocks they reference.
- Verdicts: a new `objects/06_requirement_verdicts.yml`, generated from the approved research data,
  referencing claims by `name` and requirements by `identifier`.
- `extent` is removed from every claim in `objects/04_products.yml`.

## 5. Checks

**Decision**:
- One verdict per requirement per claim: a uniqueness constraint `[claim, requirement]` in the
  schema (cheaper layer, `infrahub-managing-checks`).
- New check `catalog_verdict_check` with its own query: a verdict other than `not_shown` needs a
  source, and its requirement must have no block or the claim's block.
- `catalog_submission_check`: add requirements (like building blocks, may not be added or changed on a
  submission branch) and verdicts (records on `main` may not change); remove `extent`.
- `catalog_unused_source_check`: a source that supports only verdicts counts as used.

## 6. Research method for the 97 claims

**Decision**: one research agent per building block (two each for Intent and Observability, the
largest), and one for the two framework-wide requirements. A block agent gets the block's
requirements and claims, with each product's existing sources. The framework-wide agent assesses each
product once; its verdicts are copied to each of the product's claims. Each agent returns one verdict per requirement and claim with a note and source links, and "not_shown" when no
source states the fact. Verdicts are merged, the extent is computed, and the result is published as
a review page for the user's approval (FR-016).

**Rationale**: the same method produced the 47 products of the Network Automation Map load, which the
user approved. Splitting by block keeps each agent's requirement list short.
