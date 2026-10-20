# Feature Specification: Network Automation Product Catalog Schema

**Feature Branch**: `001-catalog-schema`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Initial catalog schema: a network automation team records network
automation products in Infrahub and maps each product to the building blocks of the Network
Automation Framework that it covers. Each product record links to the sources of the facts it
states. The framework's building blocks are recorded as nodes loaded from object files, each linked
to the framework's own definition, not hard-coded in the schema."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record the framework's building blocks (Priority: P1)

A catalog maintainer records each building block of the Network Automation Framework in the
catalog, with the block's name exactly as the framework writes it, a short description and a link
to the framework's definition of the block. The maintainer adds or changes blocks by editing a
data file and loading it, without changing the data model.

**Why this priority**: every product mapping points to a building block, so the blocks must exist
before any product can be mapped.

**Independent Test**: load the building block data file into an empty catalog and view the list of
building blocks. Every block appears with its name, description and definition link.

**Acceptance Scenarios**:

1. **Given** an empty catalog, **When** the maintainer loads the building block data file,
   **Then** the catalog lists every building block in the file, each with a link to its
   definition.
2. **Given** a loaded catalog, **When** the maintainer adds one building block to the data file
   and loads it again, **Then** the new block appears and no existing block is duplicated.
3. **Given** a building block data file entry with no definition link, **When** the maintainer
   loads the file, **Then** the catalog rejects the entry.

---

### User Story 2 - Record a product and the building blocks it covers (Priority: P1)

A catalog maintainer records a network automation product: its name, the organization that
publishes it, a neutral description, its license model and its home page. The maintainer then
records which building blocks the product covers, and whether it covers each one fully or partly.
Each coverage claim links to at least one source that supports it. Each fact on the product, such
as the publisher or the license model, links to the source that states it.

**Why this priority**: this is the purpose of the catalog. Without products and coverage claims,
the catalog holds no information that a reader can use.

**Independent Test**: with the building blocks loaded, record one product with two coverage claims
and view the product. The product shows its publisher, its covered building blocks and the source
for each claim.

**Acceptance Scenarios**:

1. **Given** the building blocks are loaded, **When** the maintainer records a product with a
   coverage claim and a source for the claim, **Then** the product appears with the covered
   building block, the extent of coverage and the source link.
2. **Given** the building blocks are loaded, **When** the maintainer records a coverage claim
   with no source, **Then** the catalog rejects the claim.
3. **Given** a product whose license model no source states, **When** the maintainer records the
   product, **Then** the license model stays empty and the catalog accepts the product.
4. **Given** a product whose description comes from the vendor's documentation, **When** the
   maintainer records the description, **Then** the description links to that documentation as
   its source.

---

### User Story 3 - Compare products by building block (Priority: P2)

A network engineer who is choosing tools opens a building block and views every product that
covers it, with the source for each claim. The engineer also opens a product and views every
building block it covers.

**Why this priority**: this is how readers use the catalog, but it depends on the data recorded in
User Stories 1 and 2.

**Independent Test**: with three products loaded, open one building block and confirm that the
list of products matches the coverage claims in the data files.

**Acceptance Scenarios**:

1. **Given** two products that cover the same building block, one fully and one partly, **When**
   the engineer opens that building block, **Then** both products are listed, each with its extent
   of coverage and the source for its claim.
2. **Given** a building block that no product covers, **When** the engineer opens it, **Then** the
   list of products is empty.

---

### User Story 4 - Trace a fact to its source (Priority: P2)

A reader who doubts a fact in the catalog opens the source that supports it and views the date the
maintainer last checked that source.

**Why this priority**: the constitution requires every fact to link to its source (Principle III).
This story makes that link visible to readers.

**Independent Test**: open any coverage claim, follow its source link and confirm the source has a
title, a link and a date it was last checked.

**Acceptance Scenarios**:

1. **Given** a coverage claim, **When** the reader opens its source, **Then** the source shows a
   title, a link and the date it was last checked.
2. **Given** one source that supports claims for two products, **When** the reader opens the
   source, **Then** both claims are listed.
3. **Given** a product's license model, **When** the reader views it, **Then** the reader can open
   the source that states that license model, separately from the sources of the other facts.

### Edge Cases

- A product is renamed by its publisher. The maintainer changes the product name, and existing
  coverage claims stay linked to the product.
- A product moves from one publisher to another, for example after an acquisition. The maintainer
  changes the publisher, and the catalog keeps the product's coverage claims.
- The framework renames or removes a building block. The maintainer updates the data file. A
  building block that still has coverage claims cannot be deleted until the claims are moved or
  removed.
- Two products have the same name but different publishers. The catalog accepts both, and each is
  identified by publisher and name.
- A source link stops working. The source stays in the catalog, and its last-checked date shows
  when it was last confirmed.
- The same product and building block pair is recorded twice. The catalog rejects the second
  claim.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The catalog MUST record each building block of the Network Automation Framework with
  its name as the framework writes it, a description and a link to the framework's definition.
- **FR-002**: Building blocks MUST be added, changed and removed by loading data files, without a
  change to the data model.
- **FR-003**: The catalog MUST record each product with a name, a publisher, a description and a
  home page link. The license model MUST be optional.
- **FR-004**: The catalog MUST record each publisher (a company, a foundation or an open-source
  project) once, and link it to all of its products.
- **FR-005**: The catalog MUST record a coverage claim as one product, one building block, an
  extent of coverage (full or partial), an optional note and at least one source. The sources of a
  claim MUST support its extent as well as the coverage itself.
- **FR-006**: The catalog MUST reject a coverage claim that has no source.
- **FR-007**: The catalog MUST reject a second coverage claim for the same product and building
  block.
- **FR-008**: The catalog MUST record each source once, with a title, a link and the date it was
  last checked, and MUST allow one source to support many claims.
- **FR-009**: Each fact stated on the product record itself MUST link to its own source, so a
  reader can tell which source supports which fact. This applies to the publisher, the
  description and the license model. The home page link needs no separate source.
- **FR-010**: Readers MUST be able to view, from a building block, every product that covers it,
  and from a product, every building block it covers.
- **FR-011**: The catalog MUST prevent the deletion of a building block or a source that is still
  linked to a coverage claim.
- **FR-012**: Products MUST be identified by publisher and name together, so two publishers can
  each have a product with the same name.

### Key Entities

- **Building block**: one component of the Network Automation Framework. It has a name as the
  framework writes it, a description and a link to the framework's definition. It is linked to the
  coverage claims that name it.
- **Publisher**: the company, foundation or open-source project that publishes a product. It has a
  name and a home page link.
- **Product**: a network automation product. It has a name, a description, a home page link and an
  optional license model. It belongs to one publisher and has zero or more coverage claims. Its
  publisher, description and license model each link to the source that states them.
- **Coverage claim**: a statement that one product covers one building block, fully or partly,
  with an optional note, supported by one or more sources.
- **Source**: a document that supports facts in the catalog, such as vendor documentation or
  release notes. It has a title, a link and the date it was last checked.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer can load every building block of the framework from one data file in a
  single load, with no errors.
- **SC-002**: A maintainer can record a new product with three coverage claims and their sources
  in under 10 minutes.
- **SC-003**: 100% of coverage claims, and 100% of publisher, description and license model
  facts on products, link to at least one source.
- **SC-004**: A reader can go from a building block to the list of products that cover it in one
  step, and from any coverage claim to its source in one step.
- **SC-005**: Adding a building block to the framework requires no change to the data model, only
  a data file change.

## Assumptions

- The catalog covers both commercial and open-source products.
- The users are the network automation team that maintains the catalog and the engineers who read
  it. Access control beyond Infrahub's default accounts is out of scope.
- The framework is the Network Automation Framework published by the Network Automation Forum. The
  link to its definition of each building block is not known yet and must come from the
  framework's published documentation. The list of building blocks is not part of this spec.
- Only the top-level building blocks are recorded. Sub-capabilities within a block are out of
  scope for this feature.
- Product versions and release history are out of scope. A coverage claim applies to the product
  as a whole.
- Reports, menus, checks and transforms are separate features that follow this schema.
