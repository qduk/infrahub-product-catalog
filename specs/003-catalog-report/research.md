# Research: Catalog Coverage Report

> **Scope change, 2026-10-21**: the user kept only the coverage table. R1 (chart types), R2 (bar
> chart) and the Mermaid parts of R7 describe the removed charts and are kept as a record. The user
> confirmed that Infrahub drew the two bar series over each other, as R2 expected.

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-21

## R1. Chart format and the chart types Infrahub can show

- **Decision**: build the report as a Markdown artifact (`content_type: text/markdown`):
  - the coverage table as a plain Markdown table;
  - the bar chart as a Mermaid `xychart-beta` block;
  - the product map as a Mermaid `flowchart` block.
- **Rationale**:
  - Infrahub 1.11 renders Mermaid in Markdown artifacts. The
    [artifacts overview](https://github.com/opsmill/infrahub/blob/stable/docs/docs/artifacts/overview.mdx)
    says Markdown "renders as formatted text, including diagrams from fenced mermaid code blocks".
    The 1.11.0 release notes say "Markdown artifacts render Mermaid diagrams".
  - The web interface served by the local instance (1.11.8) loads Mermaid's chart modules on
    demand. Its Mermaid chunk lists, among others:
    - `flowDiagram`
    - `pieDiagram`
    - `xychartDiagram`
    - `quadrantDiagram`
    - `sankeyDiagram`
    - `blockDiagram`
    Bar charts (`xychart`) are therefore available.
- **Not confirmed**: no one has yet viewed a rendered chart from this catalog in the web
  interface. The quickstart's first row covers this, and needs a person at a browser.
- **Alternatives considered**: an SVG artifact drawn by Python. Rejected because it needs a
  drawing library and gives no text the reviewer can read in a diff. CSV was rejected because it
  shows no charts.

## R2. Showing full and partial counts in one bar chart (FR-003)

- **Decision**: draw two bar series in one `xychart-beta`:
  - "All products", the total for each block, first;
  - "Full coverage" second.
  Mermaid draws later series over earlier ones. Because the full count is never more than the
  total, the visible top of each bar is the partial count, which reads like a stacked bar. A line
  under the chart states the colours, and the table already gives exact numbers.
- **Not confirmed**: whether `xychart-beta` in this Mermaid build draws the second series over
  the first, or beside it. If it draws them beside each other, the chart still shows both numbers
  correctly, and only the note under the chart changes. Quickstart row 1 checks this.
- **Alternatives considered**: two separate charts (full and partial). Rejected because it
  doubles the reading. A pie chart was rejected because it shows shares, not counts per block.

## R3. The object the report attaches to (spec Assumptions, constitution Principle I)

- **Decision**: add one node, `CatalogReport`, to `schemas/catalog.yml` in this feature, with
  `inherit_from: [CoreArtifactTarget]`.
  - Attributes: `name` (Text, unique) and `description` (TextArea, optional).
  - Human-friendly ID `[name__value]`, and `generate_profile: false`.
  - One instance, "Catalog coverage report", in `objects/05_reports.yml`, which is a member of the
    standard group `catalog_reports`.
- **Rationale**:
  - Artifacts attach only to nodes that inherit `CoreArtifactTarget`, and the inheritance cannot
    be added through `extensions:` (transforms skill, `artifacts-definitions`).
  - Adding it to `CatalogBuildingBlock` or `CatalogProduct` would build one report per block or
    product. The spec asks for one report for the whole catalog (FR-001).
  - The change adds a node and changes no existing one, so no loaded data is migrated.
  - It is done in this feature, not in a separate schema cycle, because it has no use without the
    report. Principle I is still met: the schema change is written, checked and loaded before the
    transform (plan, order of work).
- **Alternatives considered**: a separate schema feature first. Rejected because a node with no
  report has nothing to validate on its own.

## R4. Python transform, not Jinja2

- **Decision**: a Python transform, `CatalogReportTransform`, in
  `transforms/catalog_report.py`, returning a `str`.
- **Rationale**: the transform does more than format text.
  - It pivots claims into a product × building block grid.
  - It counts full and partial claims per block.
  - It sorts products and blocks the same way in every section.
  - It escapes names for Mermaid.
  The transforms skill puts aggregation and reshaping on the Python side.
- **Alternatives considered**: Jinja2 alone, rejected because the pivot and counts are awkward in
  a template. Python with a Jinja2 template (hybrid) was rejected because it adds a file for little
  gain at this size.

## R5. Order of building blocks and products (FR-005, FR-006)

- **Decision**: sort building blocks by name and products by full name, both case-insensitive.
- **Rationale**: no field records the framework's own order, and FR-006 forbids a fixed list in
  the report. Sorting by name is stable and needs no schema change.
- **Alternatives considered**: add a `position` attribute to `CatalogBuildingBlock` that records
  the framework's order. Rejected for now because it is a schema change that the spec does not
  ask for. It can be added later.

## R6. Build date and branch in the report (FR-008)

- **Decision (confirmed by the user on 2026-10-21)**: leave the build time and branch name out of the
  report text. Infrahub records when each artifact node was last updated, and each artifact belongs
  to the branch it was built on, which the web interface's branch selector shows. Implementation
  confirms where the web interface shows the update time.
- **Rationale**:
  - Infrahub compares artifact content to decide whether an artifact changed. With a time stamp
    in the text, every proposed change would show the report as changed, even when no catalog data
    changed. That would hide the real changes that User Story 4 is meant to show.
  - The branch name would cause the same problem on every branch.
  - Content that depends only on the data can be tested against a fixed expected file
    (`python-transform-unit-process` with `output`).
- **Consequence**: spec FR-008 was rewritten to require report text that depends only on the
  catalog data.

## R7. Mermaid text escaping

- **Decision**:
  - In the flowchart, each node gets a generated ID (`p1`, `b1`) and a label in double quotes.
    Double quotes inside a name are written as `#quot;`.
  - In the bar chart, axis labels are quoted the same way.
  - In the Markdown table, a `|` in a name is written as `\|`.
- **Rationale**: Mermaid treats brackets, parentheses and quotes in unquoted labels as syntax (spec
  edge case). Generated IDs keep every name, whatever it contains, out of the syntax.

## R8. How the report is built and rebuilt

- **Decision**: register the transform, its query and the artifact definition in `.infrahub.yml`.
  The read-only repository connection from feature 002 then provides them to Infrahub.
  Artifacts are rebuilt in the proposed change pipeline (User Story 4, FR-007).
- **Consequence**: after the change is pushed to `main`, a maintainer runs **Import latest
  commit** on the repository (`AGENTS.md`).
- **Tests**: `tests/test_transforms.yml` with:
  - a `python-transform-smoke` test;
  - `python-transform-unit-process` tests that compare output with fixed expected files:
    - the current catalog;
    - an empty catalog;
    - a product with no claims;
    - names with Mermaid special characters.
  These tests compare full output. Unlike the check tests (feature 002, research R6), they fail
  when the output differs.
