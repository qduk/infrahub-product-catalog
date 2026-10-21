# Feature Specification: Product Status

**Feature Branch**: `004-product-status`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Product status: catalog maintainers record whether each product is
active, discontinued or acquired (continues under another company), so the catalog can keep and
track products that are no longer sold, such as Skybox Security (closed 2025), System Initiative
(archived) and Pliant (acquired by IBM). The status is a fact, so it links to the sources that
state it. Products default to active. The source check flags a product that is discontinued or
acquired with no status source, and the coverage report shows the status of each product."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record that a product is no longer sold (Priority: P1)

A catalog maintainer adds a product that has been discontinued or absorbed into another company,
such as a product from the Network Automation Map whose vendor has closed. The maintainer records
its status, the date the status took effect when a source states it, and the source that states
the status. The product keeps its publisher, description and coverage claims, so the catalog
still shows what the product did.

**Why this priority**: the user asked to track these products rather than leave them out. Without
a status, a discontinued product would look like an option an engineer can still buy.

**Independent Test**: add a product with status "discontinued", a status date and a status
source, and view it. The product shows its status, date and source next to its other facts.

**Acceptance Scenarios**:

1. **Given** a new product, **When** the maintainer records it without a status, **Then** its
   status is "active".
2. **Given** a product, **When** the maintainer sets its status to "discontinued" with a status
   date and a status source, **Then** the product shows all three.
3. **Given** a product with status "acquired", **When** a reader views it, **Then** the reader
   can open the source that states the acquisition, separately from the sources of the product's
   other facts.

---

### User Story 2 - Flag a status that has no source (Priority: P1)

A maintainer opens a proposed change that marks a product as discontinued or acquired but gives
no source for the status. The source check fails and names the product, so the merge is blocked
until a source is added.

**Why this priority**: constitution Principle III requires every fact to link to its source. A
status is a fact, and the claim that a product is no longer sold matters to anyone choosing tools.

**Independent Test**: on a branch, set a product's status to "discontinued" without a status
source, run the source check, and confirm it fails and names the product.

**Acceptance Scenarios**:

1. **Given** a product with status "discontinued" or "acquired" and no status source, **When**
   the source check runs, **Then** it fails and names the product with a message that says to add
   a status source.
2. **Given** a product with status "active" and no status source, **When** the source check runs,
   **Then** it reports nothing about the status.

---

### User Story 3 - See status in the coverage report (Priority: P2)

An engineer opens the coverage report and can tell at a glance which products are no longer sold.

**Why this priority**: the report is where engineers compare products. Without the status there,
a discontinued product's coverage could be read as a current option.

**Independent Test**: with one discontinued product in the catalog, open the report and confirm
the product's row shows its status.

**Acceptance Scenarios**:

1. **Given** a discontinued product, **When** the engineer opens the report, **Then** its row in
   the table names its status after the product name.
2. **Given** only active products, **When** the engineer opens the report, **Then** no status is
   shown and the report text is unchanged from today.

### Edge Cases

- A product is acquired but its new owner still sells it under the same name, such as Device42
  under Freshworks. Its status stays "active", and its publisher is the new owner.
- An acquisition is announced but not completed, such as Infoblox's agreement to acquire Kentik.
  The status stays "active" until a source states that the product is no longer sold on its own.
- No source states the date a status took effect. The status date stays empty.
- A discontinued product is later revived. The maintainer sets the status back to "active" and
  can keep the status source as the record of the change.
- A product's status changes on a branch. The proposed change shows the report with the new
  status before the merge.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The catalog MUST record a status for each product, with exactly one of these values:
  - **active**: the publisher sells or develops the product under its current name;
  - **discontinued**: the product is no longer developed or sold;
  - **acquired**: the product was absorbed into another company and is no longer offered on its
    own under its own name.
- **FR-002**: A product recorded without a status MUST have the status "active". Existing products
  MUST become "active" with no change to their data files.
- **FR-003**: The catalog MUST record an optional status date: the date the status took effect,
  when a source states it.
- **FR-004**: The catalog MUST let each product link to the sources that state its status,
  separately from the sources of its other facts.
- **FR-005**: The source check MUST fail, and block the merge, for any product whose status is
  "discontinued" or "acquired" and that has no status source. The message MUST name the product
  and say to add a status source.
- **FR-006**: The coverage report MUST show the status after the product name for every product
  that is not "active", and MUST show nothing extra for active products.
- **FR-007**: A product's publisher, description and coverage claims MUST stay unchanged when its
  status changes.

### Key Entities

- **Product** (feature 001): gains a status, an optional status date, and links to the sources
  that state the status.
- **Source** (feature 001): can now also support a product's status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of products marked "discontinued" or "acquired" on `main` link to at least one
  status source.
- **SC-002**: The three known cases (Skybox Security, System Initiative, Pliant) can be recorded
  with their status, date where known, and source.
- **SC-003**: The coverage report on `main` is unchanged for a catalog with only active products.
- **SC-004**: A reader can tell from the report alone, in under 10 seconds, which products are no
  longer sold.

## Assumptions

- The three status values cover the cases found so far. Other states, such as "announced for
  end of life", are out of scope until a product needs them.
- The catalog does not record which product replaced a discontinued one (for example Tufin after
  Skybox). A maintainer can say so in the product description.
- The status date has a day precision. A source that gives only a month or year uses the first
  day of that month or year, and the status source states the real precision.
- This feature includes the schema change, the source check rule and the report change, because a
  status without the check would break Principle III. Loading the products from the Network
  Automation Map is separate work that follows this feature.
