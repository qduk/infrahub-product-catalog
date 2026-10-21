# Feature Specification: Catalog Coverage Report

**Feature Branch**: `003-catalog-report`

**Created**: 2026-10-21

**Status**: Draft. Scope reduced on 2026-10-21: the user kept only the coverage table (see
"Scope change" below).

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

### User Story 4 - Review how a change affects the report (Priority: P2)

A catalog maintainer opens a proposed change that adds a product or a coverage claim. The proposed
change shows the report as it will be after the change, so the reviewer can see how the table,
table changes before merging.

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
- A product has no coverage claims. It appears in the table with no coverage in every cell.
- A building block is added to the catalog. The report adds a column for it without any change to
  the report itself.
- Product or building block names contain characters that the table format treats specially, such
  as `|`. The report shows the names as written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The catalog MUST provide one report that covers the whole catalog, viewable in
  Infrahub's web interface.
- **FR-002**: The report MUST include a table with one row per product (named with its publisher)
  and one column per building block, showing full, partial or no coverage in each cell.
- **FR-003**: Removed on 2026-10-21 (bar chart, see "Scope change").
- **FR-004**: Removed on 2026-10-21 (product map, see "Scope change").
- **FR-005**: The report MUST list building blocks and products in a stable order: sorted by name.
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

- **SC-001**: 100% of coverage claims in the catalog appear in the table with the right extent.
- **SC-002**: An engineer can find which products cover a given building block in under 30
  seconds after opening the report.
- **SC-003**: Adding a product or claim and opening a proposed change shows the updated report on
  the proposed change within 5 minutes.
- **SC-004**: Adding a building block to the catalog changes the report with no change to the
  report's own files.

## Scope change

On 2026-10-21, after viewing the rendered report, the user decided to keep only the coverage table
for now and to build interactive charts in a separate front end later. User Stories 2 (bar chart)
and 3 (product map), FR-003 and FR-004 were removed. Both charts worked in Infrahub before they
were removed: they are in commit `a63ec0d`, and the user confirmed that the bar chart drew the two
series over each other.

## Assumptions

- A license model chart is out of scope.
- The report is read in Infrahub's web interface, which shows Markdown reports as formatted text.
- Infrahub attaches each report to one object. The catalog has no object that stands for the
  catalog as a whole, so this feature adds one. This is a small schema change. Planning decides
  whether it is done in this feature or in a separate schema feature first (constitution
  Principle I).
- The report does not list sources for each claim. Readers open the claim in the catalog to see
  them (FR-009).
- Anyone who can open the catalog in Infrahub can open the report. No separate access rules apply.
