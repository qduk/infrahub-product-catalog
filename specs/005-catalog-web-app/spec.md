# Feature Specification: Public Catalog Web App

**Feature Branch**: `005-catalog-web-app`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Public catalog web app: an internet-facing web application in the
frontend/ folder that shows the catalog laid out like the Network Automation Framework diagram
(Presentation across the top; Observability, Orchestrator and Intent in the middle; Collector and
Executor below), with each building block listing the products that cover it. Visitors filter by
product status (active, discontinued, acquired), show a single building block, and filter by full
or partial coverage. Anyone, without logging in, can submit a new product with all its information
(publisher, description, home page, license model, status, coverage claims, and the sources for
each fact) through a form. Each submission creates an Infrahub branch with the product and opens a
proposed change for a maintainer to review; visitors see only reviewed data from main, never
pending submissions. Infrahub itself is not exposed to the internet: a small backend service holds
a limited-permission Infrahub account and offers only reading the catalog and submitting a
product. Spam protection (rate limits, human verification) is to be decided later and blocks going
live."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse the catalog as a framework diagram (Priority: P1)

A network engineer opens the web app and sees the six building blocks of the Network Automation
Framework laid out like the framework's own diagram:
- Presentation across the top;
- Observability, Orchestrator and Intent in the middle row;
- Collector and Executor below them.

Each block lists the products that cover it, with each product marked as full or partial coverage.

**Why this priority**: this is what the app is for. Engineers see at a glance which products cover
which part of the framework, which the coverage report table shows less directly.

**Independent Test**: open the app and compare each block's product list with the coverage claims
on `main`.

**Acceptance Scenarios**:

1. **Given** the catalog on `main`, **When** a visitor opens the app, **Then** each of the six
   building blocks appears in its place in the layout and lists every product with a claim on it,
   marked full or partial.
2. **Given** a building block with no claims, **When** the visitor opens the app, **Then** the
   block appears and says that no products cover it.
3. **Given** a product in a block, **When** the visitor selects it, **Then** the app shows the
   product's publisher, description, home page, license model, status and coverage claims, with a
   link to the source of each fact.

---

### User Story 2 - Filter the diagram (Priority: P1)

The visitor narrows what the diagram shows:
- by product status (active, discontinued, acquired, any combination);
- by coverage extent (full, partial, or both);
- by building block, showing one block on its own.

The filters combine, and the diagram updates as soon as a filter changes.

**Why this priority**: with 50 products and almost 100 claims, the diagram is only usable if
visitors can reduce it to what they need.

**Independent Test**: apply each filter alone and in combination, and compare the products shown
with the catalog data.

**Acceptance Scenarios**:

1. **Given** the default view, **When** the visitor opens the app, **Then** only active products
   are shown, with both full and partial coverage, across all six blocks.
2. **Given** the status filter, **When** the visitor also selects "discontinued", **Then**
   discontinued products appear and are marked as discontinued.
3. **Given** the extent filter set to "full" only, **When** the diagram updates, **Then** no
   partial claim is shown.
4. **Given** the visitor selects one building block, **When** the diagram updates, **Then** only
   that block is shown, with the other filters still applied, and the visitor can return to all
   six blocks in one action.
5. **Given** filters that match no product in a block, **When** the diagram updates, **Then** the
   block says that no products match the filters.
6. **Given** a set of filters, **When** the visitor copies the page address and opens it
   elsewhere, **Then** the same filters are applied.

---

### User Story 3 - Submit a new product (Priority: P2)

A visitor who knows of a product that is missing fills in a form, without logging in:
- the product name, description and home page;
- its publisher, chosen from existing publishers or entered as a new one with a home page;
- an optional license model;
- its status, with an optional status date;
- one or more coverage claims, each with a building block, an extent and an optional note;
- a source for each fact: the publisher, the description, the license model (if given), the status
  (if not active), and each claim. A source is a link and a title, and can be reused across facts.

On submission, the catalog receives the product as a change waiting for review. The visitor sees a
confirmation with a reference they can quote, and nothing changes in the public view until a
maintainer accepts it.

**Why this priority**: it lets the community grow the catalog. It comes after browsing because
the catalog must be readable before contributions are useful.

**Independent Test**: submit a complete product through the form, and confirm that a change
waiting for review exists with the product, its publisher, sources and claims, and that the public
view does not show it.

**Acceptance Scenarios**:

1. **Given** a complete form, **When** the visitor submits it, **Then** a change waiting for review
   is created with the product and all its facts, and the visitor sees a confirmation with a
   reference.
2. **Given** a form with a missing required field or a fact without a source, **When** the visitor
   tries to submit it, **Then** the form names each problem next to the field and nothing is
   created.
3. **Given** a status of "discontinued" or "acquired" with no status source, **When** the visitor
   tries to submit, **Then** the form asks for a status source.
4. **Given** a product name that already exists for the chosen publisher, **When** the visitor
   tries to submit, **Then** the form says the product is already in the catalog.
5. **Given** a submitted product, **When** any visitor opens the public view before a maintainer has
   accepted it, **Then** the product does not appear.
6. **Given** a submission that fails while being saved, **When** the visitor submits, **Then** the
   visitor sees that the submission was not saved and can try again, and no partial change is left
   waiting for review.

---

### User Story 4 - Review a submission (Priority: P2)

A catalog maintainer sees each submission as its own change waiting for review in Infrahub, with
the source check and the coverage report already run on it. The maintainer accepts it by merging,
or rejects it by closing it.

**Why this priority**: review is what makes anonymous submissions safe. Without it, anyone could
change the public catalog.

**Independent Test**: submit a product, open the resulting proposed change in Infrahub, confirm the
checks ran, merge it, and confirm the product then appears in the public view.

**Acceptance Scenarios**:

1. **Given** a submission, **When** a maintainer opens Infrahub, **Then** the submission is a
   proposed change named after the product, and its description says it came from the public form.
2. **Given** an accepted submission, **When** a visitor reloads the public view, **Then** the
   product appears within 5 minutes.
3. **Given** a rejected submission, **When** the maintainer closes it, **Then** nothing changes in
   the public view.

### Edge Cases

- A visitor enters a source link that is already in the catalog. The submission reuses the
  existing source rather than creating a copy.
- A visitor enters a publisher name that already exists. The form offers the existing publisher.
- Two visitors submit the same product before either is reviewed. Both changes wait for review,
  and the maintainer merges one and closes the other.
- Submitted text contains HTML or script. The app shows it as plain text, and it is stored as typed.
- The catalog service is unreachable. The public view says the catalog is unavailable, and the form
  does not accept submissions.
- A very long field or an unusually large number of claims or sources. The form and the service
  reject input above set limits.

## Requirements *(mandatory)*

### Functional Requirements

**Browsing**

- **FR-001**: The app MUST show the six building blocks in the layout of the Network Automation
  Framework diagram: Presentation across the top; Observability, Orchestrator and Intent in the
  middle row; Collector and Executor in the bottom row.
- **FR-002**: Each block MUST list the products with a coverage claim on it, each marked full or
  partial, and MUST mark products that are discontinued or acquired.
- **FR-003**: The app MUST show a product's full details, with a link to the source of each fact,
  when the visitor selects the product.
- **FR-004**: The app MUST read building blocks, products and claims from the catalog, with no
  fixed list in the app (constitution Principle IV).
- **FR-005**: The app MUST show only data from `main`. It MUST NOT show submissions waiting for
  review.

**Filtering**

- **FR-006**: The visitor MUST be able to filter by status (any combination of active, discontinued
  and acquired), by extent (full, partial or both), and to show a single building block. Filters
  MUST combine.
- **FR-007**: The default view MUST show active products, both extents and all six blocks.
- **FR-008**: The current filters MUST be part of the page address, so a filtered view can be
  shared.

**Submitting**

- **FR-009**: Anyone MUST be able to submit a product without logging in.
- **FR-010**: The form MUST collect every fact the catalog records for a product, and MUST apply the
  catalog's rules before submission:
  - the product name, description, home page, publisher, publisher source and description source
    are required;
  - a license model needs a license model source;
  - a status other than active needs a status source;
  - each claim needs a building block, an extent and at least one source;
  - one claim per building block.
- **FR-011**: Each submission MUST create its own Infrahub branch with the product and its facts,
  and open a proposed change from that branch to `main`.
- **FR-012**: If any step of a submission fails, the service MUST NOT leave a partial branch or
  proposed change, and MUST tell the visitor the submission was not saved.
- **FR-013**: The visitor MUST receive a confirmation with a reference to the submission. The
  reference MUST NOT give public access to the pending change.
- **FR-014**: The service MUST reject a submission whose product already exists for the chosen
  publisher on `main`.
- **FR-015**: Submitted text MUST be shown as plain text everywhere in the app, never as markup.
- **FR-016**: Every text field and every list in the form MUST have a maximum size, enforced both
  in the form and by the service.

**Security and boundaries**

- **FR-017**: Infrahub MUST NOT be reachable from the internet through the app. The only public
  operations MUST be reading the catalog and submitting a product.
- **FR-018**: The service MUST use an Infrahub account limited to what these two operations need.
  The account's credentials MUST NOT reach the browser.
- **FR-019**: Protection against automated and repeated submissions (rate limits, human
  verification) MUST be in place before the app is made reachable from the internet. The design of
  this protection is not decided yet.
- **FR-020**: Before the app is made reachable from the internet, the service account MUST be unable
  to merge proposed changes. On Infrahub 1.11.8 this is not yet true: opening a proposed change
  needs the `edit_default_branch` permission, and an account with it could merge its own proposed
  change even with an explicit deny on `merge_proposed_change` (tested 2026-10-21, see the plan's
  research). The user accepted this for development on the local instance. It blocks going live
  until Infrahub enforces the merge permission, or until proposed changes are opened by a separate
  internal process.

### Key Entities

- **Catalog view**: the building blocks, products, publishers, claims and sources on `main`, as the
  public sees them.
- **Submission**: one product with all its facts as entered in the form, with the visitor's
  confirmation reference. It becomes an Infrahub branch and a proposed change.
- **Service account**: the Infrahub account the service uses, with only the permissions the two
  public operations need.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor finds every product that fully covers a given building block in under 30
  seconds after opening the app.
- **SC-002**: 100% of the coverage claims on `main` appear in the diagram when all filters are off,
  in the right block with the right extent.
- **SC-003**: A filter change updates the diagram in under 1 second.
- **SC-004**: A visitor can submit a product with three coverage claims in under 10 minutes.
- **SC-005**: 100% of submissions that pass the form create exactly one proposed change, and 0
  submissions appear in the public view before they are merged.
- **SC-006**: 100% of submissions that a maintainer merges pass the source check without edits,
  because the form applies the same rules.

## Assumptions

- The app lives in the `frontend/` folder of this repository, as the user asked.
- Maintainers review submissions in Infrahub's web interface. The app has no reviewer screens.
- Anonymous visitors cannot edit or delete existing products. Corrections are made by maintainers,
  or later through a separate feature.
- The visual style follows the Network Automation Framework diagram the user supplied: one coloured
  box per building block. The exact colours and fonts are decided during planning.
- Deploying the app and Infrahub for internet access, including replacing Infrahub's default admin
  password and token, is a separate step. This feature builds and tests the app against the local
  instance.
- Spam protection is out of scope for this feature by the user's decision, and blocks going live
  (FR-019).
- The merge-permission gap (FR-020) was reported to the Infrahub team privately. The report is not
  stored in this public repository.
- The browser targets are current versions of the major desktop and mobile browsers.
