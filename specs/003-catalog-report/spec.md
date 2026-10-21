# Feature Specification: Catalog Coverage Report

**Feature Branch**: `003-catalog-report`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description (taken from the recommendation the user accepted): "Catalog report
artifact: one Markdown report in Infrahub with Mermaid charts built from the catalog data. It holds
a coverage matrix of products against building blocks (full or partial), a bar chart of how many
products cover each building block, and a flowchart from products to the building blocks they
cover."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View which products cover which building blocks (Priority: P1)

A network engineer who is choosing tools opens the catalog report in Infrahub. The report shows a
table with one row per product and one column per building block of the Network Automation
Framework. Each cell shows whether the product covers that block fully, partly or not at all.

**Why this priority**: today an engineer can only open one building block or one product at a
time (feature 001, User Story 3). The table answers "which tools cover what" in one view, which is
the main reason to read the catalog.

**Independent Test**: open the report and compare each cell of the table with the coverage claims
in the catalog.

**Acceptance Scenarios**:

1. **Given** the catalog's 3 products and 5 coverage claims, **When** the engineer opens the
   report, **Then** the table has 3 product rows and 6 building block columns, and each of the 5
   claims appears in the right cell as full or partial.
2. **Given** a building block that no product covers, **When** the engineer opens the report,
   **Then** its column is present and every cell in it shows no coverage.
3. **Given** the table, **When** the engineer reads a product row, **Then** the row names the
   product with its publisher.

---

### User Story 2 - View how many products cover each building block (Priority: P2)

The engineer views a bar chart with one bar per building block. Each bar shows how many products
cover the block, split into full and partial coverage, so the engineer can see which blocks have
many options and which have none.

**Why this priority**: the gaps (blocks with no products) show where the catalog or the market is
thin. This builds on the same data as User Story 1.

**Independent Test**: open the report and compare each bar with a count of the coverage claims
for that block.

**Acceptance Scenarios**:

1. **Given** Collector, covered fully by one product and partly by another, **When** the engineer
   views the chart, **Then** Collector shows 1 full and 1 partial.
2. **Given** Orchestrator and Presentation, which no product covers, **When** the engineer views
   the chart, **Then** both appear with a count of 0.

---

### User Story 3 - View the map from products to building blocks (Priority: P3)

The engineer views a diagram that connects each product to the building blocks it covers. A full
claim and a partial claim use different line styles, so the engineer can follow how a set of
products would combine to cover the framework.

**Why this priority**: the diagram shows the same claims as the table in another form. It is
easier to read for a few products and harder for many, so it comes after the table and the chart.

**Independent Test**: open the report and confirm that each coverage claim appears as one line
with the right style.

**Acceptance Scenarios**:

1. **Given** the catalog's 5 coverage claims, **When** the engineer views the diagram, **Then**
   it shows 5 lines, with full claims drawn one way and partial claims another.
2. **Given** a building block with no claims, **When** the engineer views the diagram, **Then**
   the block appears with no lines to it.

---

### User Story 4 - Review how a change affects the report (Priority: P2)

A catalog maintainer opens a proposed change that adds a product or a coverage claim. The proposed
change shows the report as it will be after the change, so the reviewer can see how the table,
chart and diagram change before merging.

**Why this priority**: changes reach `main` only through proposed changes (constitution 1.1.0,
Principle II). Seeing the report change during review catches mistakes, such as a claim on the
wrong building block, before they are merged.

**Independent Test**: on a branch, add a coverage claim, open a proposed change and confirm the
report on the proposed change includes the new claim while the report on `main` does not.

**Acceptance Scenarios**:

1. **Given** a proposed change that adds a claim, **When** the reviewer opens it, **Then** the
   report built for the proposed change shows the new claim.
2. **Given** the same proposed change before it is merged, **When** anyone opens the report on
   `main`, **Then** it does not show the new claim.

### Edge Cases

- The catalog has no products. The report still shows every building block, with empty rows and
  zero counts, and says that no products are recorded.
- A product has no coverage claims. It appears in the table with no coverage in every cell, and in
  the diagram with no lines.
- A building block is added to the catalog. The report adds a column, a bar and a diagram node for
  it without any change to the report itself.
- Product or building block names contain characters that the chart format treats specially,
  such as brackets, quotes or parentheses. The report shows the names as written.
- The catalog grows to many products. The table stays readable. The diagram may become crowded,
  and that is accepted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The catalog MUST provide one report that covers the whole catalog, viewable in
  Infrahub's web interface.
- **FR-002**: The report MUST include a table with one row per product (named with its publisher)
  and one column per building block, showing full, partial or no coverage in each cell.
- **FR-003**: The report MUST include a chart with one bar per building block, showing the number
  of products that cover it fully and the number that cover it partly.
- **FR-004**: The report MUST include a diagram that links each product to each building block it
  covers, with a different line style for full and partial coverage.
- **FR-005**: The report MUST list building blocks in the same order in every section, and
  products in the same order in every section.
- **FR-006**: The report MUST read building blocks, products and claims from the catalog data. It
  MUST NOT contain a fixed list of building blocks or products (constitution Principle IV).
- **FR-007**: The report MUST be rebuilt for each proposed change, so that the reviewer sees the
  report as it will be after the merge.
- **FR-008**: The report text MUST depend only on the catalog data. It MUST NOT include the time
  it was built or the branch it was built from, so that the report shows as changed on a proposed
  change only when the catalog data changes. Infrahub records when each report was updated, and
  its branch selector shows the branch (decided by the user on 2026-10-21, research R6).
- **FR-009**: The report MUST state, under the table, that each claim's sources are in the catalog,
  so readers know where to check a claim.

### Key Entities

- **Catalog report**: the single report described above. It is attached to one object in the
  catalog that represents the catalog as a whole, because Infrahub attaches each report to an
  object.
- **Product**, **Building block**, **Coverage claim**: read from the catalog (feature 001). The
  report uses the product's full name, the building block's name, and each claim's extent.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of coverage claims in the catalog appear in the table, the chart and the
  diagram, each with the right extent.
- **SC-002**: An engineer can find which products cover a given building block in under 30
  seconds after opening the report.
- **SC-003**: Adding a product or claim and opening a proposed change shows the updated report on
  the proposed change within 5 minutes.
- **SC-004**: Adding a building block to the catalog changes the report with no change to the
  report's own files.

## Assumptions

- The three sections chosen are the ones the user accepted: table, bar chart and diagram. A license
  model chart is out of scope.
- The report is read in Infrahub's web interface, which shows charts written in the Mermaid format
  inside Markdown reports (Infrahub 1.11 and later, [artifacts
  overview](https://github.com/opsmill/infrahub/blob/stable/docs/docs/artifacts/overview.mdx)).
  Which Mermaid chart types the installed version shows is confirmed during planning.
- Infrahub attaches each report to one object. The catalog has no object that stands for the
  catalog as a whole, so this feature adds one. This is a small schema change. Planning decides
  whether it is done in this feature or in a separate schema feature first (constitution
  Principle I).
- The report does not list sources for each claim. Readers open the claim in the catalog to see
  them (FR-009).
- Anyone who can open the catalog in Infrahub can open the report. No separate access rules apply.
