# Feature Specification: Proposed Change Checks for Catalog Submissions

**Feature Branch**: `007-proposed-change-checks`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description (taken from the recommendation the user accepted): "Proposed change
checks for catalog submissions: add Infrahub checks that run on every proposed change. (1) On
submission branches (named submission-*), the branch only adds catalog data: it does not change or
delete existing products, publishers, sources, coverage claims or building blocks compared with
main. (2) Near-duplicate names: publisher names, product names within a publisher, and source links
that differ only by case, spaces, punctuation, http/https or a trailing slash fail the check. (3)
Every product covers at least one building block; a product with no coverage claim is reported as a
warning, not a failure. (4) Every source supports at least one fact or coverage claim; a source that
supports nothing fails the check."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Block a submission that changes existing records (Priority: P1)

A maintainer reviews a proposed change opened by the public web app. Before reading the facts, the
maintainer needs to know that the submission only adds a new product and the records that come
with it. Infrahub runs a check on the proposed change. When the submission branch changes or
deletes any record that is already on `main`, or adds a building block, the check names each record
and the merge is blocked.

**Why this priority**: anyone on the internet can create a submission. The web service only adds
records, but the service account is allowed to edit any catalog record. This check makes sure that a
submission branch changed by any other means cannot overwrite the catalog through a merge.

**Independent Test**: on a branch named `submission-test`, change the description of a product that
is on `main`, run the check, and confirm the check names the product and fails. On a second
submission branch, only add a new product and confirm the check passes.

**Acceptance Scenarios**:

1. **Given** a submission branch that only adds a product, a new publisher, new sources and
   coverage claims for the new product, **When** the check runs, **Then** it passes.
2. **Given** a submission branch that links the new product to a publisher, building blocks and
   sources that are already on `main`, **When** the check runs, **Then** it passes.
3. **Given** a submission branch that changes a fact of a record on `main` (for example a product's
   description, a source's link or last-checked date, or a claim's extent), **When** the check runs,
   **Then** it names the record and the changed fact, and fails.
4. **Given** a submission branch that adds or removes a source of a fact of a product on `main`, or
   moves a product on `main` to another publisher, **When** the check runs, **Then** it names the
   record and fails.
5. **Given** a submission branch that deletes a record that is on `main`, **When** the check runs,
   **Then** it names the record and fails.
6. **Given** a submission branch that adds a building block, **When** the check runs, **Then** it
   names the building block and fails.
7. **Given** a branch whose name does not start with `submission-`, **When** the check runs,
   **Then** it passes without comparing the branch with `main`, so maintainers can still correct
   existing records.

---

### User Story 2 - Catch near-duplicate names and links (Priority: P1)

A maintainer reviews a proposed change. Infrahub lists every pair of publishers, products of the
same publisher, or sources whose names or links are the same once case, spaces, punctuation, the
`http`/`https` prefix and a trailing `/` are ignored. The merge is blocked until one record of each
pair is removed or renamed.

**Why this priority**: the catalog rejects names that are spelled exactly the same, but not names
such as "Netbox Labs" and "NetBox Labs". A visitor who does not find a product, or does not look,
can submit it again under a slightly different name.

**Independent Test**: on a branch, add a publisher named like an existing one with different case
and spacing, run the check, and confirm the check names both publishers and fails.

**Acceptance Scenarios**:

1. **Given** two publishers whose names differ only by case, spaces or punctuation, **When** the
   check runs, **Then** it names both and fails.
2. **Given** two products of the same publisher whose names differ only by case, spaces or
   punctuation, **When** the check runs, **Then** it names both and fails.
3. **Given** two products with the same name from different publishers, **When** the check runs,
   **Then** it reports nothing for them.
4. **Given** two sources whose links differ only by case, the `http`/`https` prefix or a trailing
   `/`, **When** the check runs, **Then** it names both and fails.
5. **Given** names and links that differ by any other character, **When** the check runs, **Then**
   it reports nothing for them.

---

### User Story 3 - Warn about a product that covers no building block (Priority: P2)

A maintainer reviews a proposed change. Infrahub lists every product that has no coverage claim, as
a warning. The merge is not blocked.

**Why this priority**: the graph view shows only products with at least one coverage claim, so a
reviewer can merge a product that never appears in the web app without noticing. The catalog
allows such products (feature 006 edge cases), so this is a warning and not a failure.

**Independent Test**: on a branch, add a product with no coverage claim, run the check, and confirm
the product is listed as a warning and the check passes.

**Acceptance Scenarios**:

1. **Given** a product with no coverage claim, **When** the check runs, **Then** it names the
   product in a message that starts with "Warning:", and the check passes.
2. **Given** a product with at least one coverage claim, **When** the check runs, **Then** it reports
   nothing for that product.

---

### User Story 4 - Block a source that supports nothing (Priority: P2)

A maintainer reviews a proposed change. Infrahub lists every source that supports no product fact
and no coverage claim. The merge is blocked until the source supports a fact or is removed.

**Why this priority**: a source that supports nothing adds no value to the catalog, and adding links
that support nothing is a common way to place spam links.

**Independent Test**: on a branch, add a source that no product or claim uses, run the check, and
confirm the check names the source and fails.

**Acceptance Scenarios**:

1. **Given** a source that supports no publisher, description, license model, status or coverage
   claim, **When** the check runs, **Then** it names the source and its link, and fails.
2. **Given** a source that supports at least one of them, **When** the check runs, **Then** it
   reports nothing for that source.
3. **Given** a change that removes the last fact or claim a source supports, **When** the check
   runs, **Then** it names the source and fails.

### Edge Cases

- A submission reuses a source that is already on `main` for its new product. The existing source
  gains a new product that it supports, but its own title, link and last-checked date do not
  change, so User Story 1 passes.
- A maintainer edits a submission branch to correct a typing error in the new product. The product
  is not on `main`, so User Story 1 still passes.
- A maintainer edits a record on `main` from inside a submission branch. User Story 1 fails. The
  maintainer makes that edit on a separate branch.
- Records on `main` already break the rules of User Story 2 or 4. Every proposed change fails until
  `main` is corrected. Before the checks are turned on, they are run against `main` and any finding
  is corrected through a proposed change.
- A name made only of punctuation or spaces. It is compared as written, so it is not a duplicate of
  every other such name.
- A pair of near-duplicate records appears once in the results, not once for each record.
- The catalog has no products or no sources. The checks finish and report nothing.

## Requirements *(mandatory)*

### Functional Requirements

**Submission branches only add records**

- **FR-001**: On a branch whose name starts with `submission-`, the check MUST compare every
  publisher, product, source, coverage claim and building block that is on `main` with the same
  record on the branch.
- **FR-002**: The check MUST fail and name the record when a record on `main` is missing on the
  branch.
- **FR-003**: The check MUST fail and name the record and the fact when any of the record's own
  facts differs from `main`:
  - publisher: name, home page;
  - product: name, description, home page, license model, status, status date, publisher, and the
    sources of the publisher, description, license model and status;
  - source: title, link, last-checked date;
  - coverage claim: product, building block, extent, note, sources;
  - building block: name, description, definition link.
- **FR-004**: The check MUST NOT fail when a record on `main` gains a link from a new record: a
  publisher with a new product, a building block with a new claim, or a source that supports a new
  product or claim.
- **FR-005**: The check MUST fail and name the building block when the branch adds a building block.
- **FR-006**: On any other branch, the check MUST pass and MUST say that it applies only to
  submission branches.

**Near-duplicate names and links**

- **FR-007**: The check MUST compare publisher names, product names of the same publisher, and
  source links after removing case, spaces and punctuation from names, and case, the `http://` or
  `https://` prefix and a trailing `/` from links.
- **FR-008**: The check MUST fail once for each pair of records that match after that comparison,
  naming both records.

**Products with no coverage**

- **FR-009**: The check MUST report each product with no coverage claim in a message that starts
  with "Warning:", and MUST NOT fail because of it.

**Sources that support nothing**

- **FR-010**: The check MUST fail and name each source, with its link, that supports no publisher,
  description, license model, status or coverage claim.

**All checks**

- **FR-011**: Each rule MUST be reported under its own name in the proposed change, so a reviewer
  can view which rule failed.
- **FR-012**: The checks MUST run on every proposed change and MUST be runnable by hand on a branch
  before a proposed change is opened, with the same result.
- **FR-013**: Every failure and warning MUST name the record so a reviewer can find it, and MUST say
  what to change.
- **FR-014**: The checks MUST only read data. They MUST NOT change any record.

### Key Entities

- **Submission branch**: a branch created by the web service for one submission. Its name starts
  with `submission-`.
- **Record on `main`**: a publisher, product, source, coverage claim or building block that exists
  on `main`, found on the branch by its identifier.
- **Near-duplicate pair**: two publishers, two products of the same publisher, or two sources that
  match after the comparison in FR-007.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the test submission branches that change, delete or add a record forbidden by
  FR-002, FR-003 or FR-005 fail the check, and 100% of those that only add a product with its records
  pass.
- **SC-002**: 100% of the near-duplicate pairs in the test data are reported, and no pair that
  differs by another character is reported.
- **SC-003**: 100% of the products with no coverage claim and the sources that support nothing in the
  test data are reported.
- **SC-004**: The checks report nothing that blocks a merge when run against `main` after any
  findings there are corrected.
- **SC-005**: A reviewer finds the record named by each finding in under 1 minute.
- **SC-006**: The checks finish in under 1 minute on the current catalog of about 50 products.

## Assumptions

- The web service names every submission branch `submission-<date>-<code>`. Other branches are
  maintainer branches and may change existing records.
- Infrahub has no "warning" result for checks. A warning is an information message that does not
  block the merge, and its text starts with "Warning:".
- The comparison in User Story 1 covers only the catalog records listed in FR-001. Changes to
  Infrahub's own records, such as accounts and groups, are out of scope.
- Product names are compared only within a publisher, because different publishers may use the same
  product name.
- Links are compared with the rules the user listed. A `www.` prefix or a query string is not
  removed.
- A failed check blocks the merge. The merge-permission gap recorded in feature 005 (FR-020) is not
  closed by this feature. Whether that gap also lets an account merge when a check has failed is
  not known.
- The checks run in Infrahub after the repository is pushed to GitHub and **Import latest commit**
  is run, as for the source check.
