# Feature Specification: Source Check for Catalog Changes

**Feature Branch**: `002-source-check`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description (taken from the recommendation the user accepted): "Source check: when
a maintainer proposes a change to the catalog, flag any product that has a license model but no
source for it, and any source whose last-checked date is older than a set age."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find a license model with no source (Priority: P1)

A catalog maintainer opens a proposed change that adds or edits products. Infrahub runs the
source check on the proposed change. The check lists every product that has a license model but no
source for it, and the change cannot be merged until each one has a source or its license model is
removed.

**Why this priority**: constitution Principle III requires every fact to link to its source. The
catalog's data model enforces this for every product fact except the license model, because the
license model is optional. This check closes that gap.

**Independent Test**: on a branch, add a product with a license model and no license model
source, open a proposed change, and confirm the check lists the product and the merge is
blocked.

**Acceptance Scenarios**:

1. **Given** a product with a license model and no source for it, **When** the maintainer opens
   a proposed change, **Then** the check names the product and reports a failure that blocks the
   merge.
2. **Given** a product with a license model and at least one source for it, **When** the
   maintainer runs the check, **Then** the check reports nothing for that product.
3. **Given** a product with no license model and no license model source, **When** the
   maintainer runs the check, **Then** the check reports nothing for that product.
4. **Given** a product with a license model and no source for it, **When** the maintainer runs
   the check by hand on the branch before opening a proposed change, **Then** the check names the
   product and reports the same failure.

---

### User Story 2 - Find sources that are due for review (Priority: P2)

A catalog maintainer runs the check and views every source whose last-checked date is older than
the review age. For each one, the check names the source and the date it was last checked, so the
maintainer can open it again, confirm the facts it supports and update the date.

**Why this priority**: product facts change when vendors release new versions or change
licenses. A source that nobody has opened for a long time may no longer support the facts linked
to it. This story is second because the catalog is new and no source is old yet.

**Independent Test**: on a branch, set one source's last-checked date to a date older than the
review age, run the check, and confirm the source is listed with its date.

**Acceptance Scenarios**:

1. **Given** a source last checked before the review age, **When** the maintainer runs the
   check, **Then** the check names the source and its last-checked date, and the change can
   still be merged.
2. **Given** a source last checked within the review age, **When** the maintainer runs the
   check, **Then** the check reports nothing for that source.
3. **Given** a maintainer who updates an old source's last-checked date to today, **When** the
   maintainer runs the check again, **Then** the source is no longer listed.

### Edge Cases

- A source's last-checked date is exactly at the review age. The source counts as within the
  review age and is not listed.
- A source's last-checked date is in the future, for example from a typing error. The check
  names the source and reports the date as invalid, and this blocks the merge.
- A product has a license model, and its only license model source was removed in the same
  change. The check lists the product.
- The catalog has no products or no sources. The check finishes and reports nothing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The check MUST list every product that has a license model and no license model
  source, by the product's full name.
- **FR-002**: A product listed under FR-001 MUST cause the check to fail, so the change cannot be
  merged.
- **FR-003**: The check MUST list every source whose last-checked date is older than the review
  age, with the source's title, link and last-checked date.
- **FR-004**: The review age MUST be 6 months. A source last checked more than 6 months before
  the day the check runs is due for review.
- **FR-005**: A source listed under FR-003 MUST be reported without blocking the merge.
- **FR-006**: The check MUST report a source whose last-checked date is in the future as invalid,
  and this MUST cause the check to fail.
- **FR-007**: The check MUST cover all products and sources in the catalog, not only those changed
  in the current proposal.
- **FR-008**: Each message MUST name the product or source and say what the maintainer has to
  do, for example "Add a license model source or remove the license model."
- **FR-009**: The check MUST run automatically on every proposed change in the catalog, so a
  failure blocks the merge without the maintainer having to remember to run it. To do this, this
  repository MUST be connected to the Infrahub instance as a Git repository.
- **FR-010**: The maintainer MUST still be able to run the check by hand on any branch before
  opening a proposed change.

### Key Entities

- **Product**: from the catalog schema. The check reads its full name, its license model and its
  license model sources.
- **Source**: from the catalog schema. The check reads its title, link and last-checked date.
- **Review age**: the length of time after which a source is due to be opened and confirmed again.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of products with a license model and no license model source are listed when
  the check runs.
- **SC-002**: 0 products or sources are listed when every license model has a source and every
  source is within the review age.
- **SC-003**: A maintainer can view the check's result on a proposed change within 5 minutes of
  opening it.
- **SC-005**: 0 proposed changes that fail the license model rule are merged.
- **SC-004**: For each item listed, a maintainer can tell from the message alone which product or
  source to fix and what to change.

## Assumptions

- This repository is not connected to Infrahub as a Git repository today, and `AGENTS.md` and
  constitution Principle II both say so. Connecting it changes how the instance is set up, so this
  feature also updates `AGENTS.md` and needs an amendment to Principle II.
- Infrahub can only connect to a Git repository it can reach. The repository is hosted at
  <https://github.com/qduk/infrahub-product-catalog> (public), set up by the user on 2026-10-20.
  How Infrahub reaches it is decided during planning.
- When the repository is connected, Infrahub may also load the schema and object files from it.
  Planning must confirm this does not conflict with loading them by hand with `infrahubctl`.
- The 6-month review age is fixed in this feature. Changing it later is a change to the check.
- The rules in this check are the only source rules that the catalog's data model cannot enforce
  ([research R3](../001-catalog-schema/research.md)). The other rules, such as "a coverage claim
  needs a source", are already enforced and are not repeated here.
- The check does not open source links to test whether they still work. Checking links is out of
  scope.
- The review age is the same for every source.
- No source is older than 6 months today, because all were checked on 2026-10-20. User Story 2 is
  tested with a source whose date is set back on a test branch.
