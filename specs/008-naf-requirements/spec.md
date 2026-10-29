# Feature Specification: Framework Requirements and Coverage Assessments

**Feature Branch**: `015-naf-requirements`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: "Would be cool to showcase how the tools map to the MUST, SHOULD and MAY
requirements from the NAF framework itself. When I see full coverage I would imagine the tool
implements all of the MUST and SHOULD requirements. For example sticking Netbox to partial coverage
of the intent block would make sense to me. Or at least having it clearly shown which requirements
it falls short on."

Decisions the user made on 2026-10-23:
- Coverage is computed from the requirements: full when every MUST and SHOULD is met, partial
  otherwise.
- A requirement that no source shows as met counts against full coverage.
- All 97 existing coverage claims are assessed, and the user approves the verdicts before they are
  loaded.
- Visitors do not assess requirements in the submission form. Maintainers add verdicts during
  review.

Decisions the user made on 2026-10-27, after reviewing the research:
- The strict rule stays: partly met and not shown count against full.
- The two framework-wide SHOULD requirements are shown on every claim but do not count toward full
  coverage. Full depends only on the block's own MUST and SHOULD requirements.
- executor-must-1 and collector-must-1 use a looser reading: at least one of the listed write
  interfaces, and live reads plus at least one kind of metrics, logs, flows, packets or traces
  (`dev/knowledge/naf-requirements-2026-10-23/adjustments.json`).
- NUTS and Spacelift are removed from the catalog, and five claims are removed: Device42 on
  Observability, EfficientIP on Executor, System Initiative on Executor, Forward Enterprise on Intent,
  NetBrain on Intent.
- Seven verdicts are corrected by the user's knowledge of the products, each with a source.

## Background: what the framework defines

The [Network Automation Framework reference](https://reference.networkautomation.forum/Framework/Framework/)
describes each building block in sentences that use MUST, SHOULD and MAY. The reference is published
under CC0 (public domain) in <https://github.com/Network-Automation-Forum/reference>. On 2026-10-23
it contained:

| Block | MUST | SHOULD | MAY |
|-------|------|--------|-----|
| Intent | 3 | 4 | 1 |
| Executor | 1 | 5 | 1 |
| Collector | 1 | 1 | 0 |
| Observability | 1 | 2 | 2 |
| Orchestrator | 1 | 5 | 1 |
| Presentation | 1 | 0 | 2 |

Its introduction also says that all components SHOULD follow modern software engineering practices
(version control, CI/CD) and expose machine-friendly APIs documented by a schema.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The framework's requirements are part of the catalog (Priority: P1)

A maintainer views every requirement of a building block in the catalog: its level (MUST, SHOULD or
MAY), its text quoted from the framework reference, and a link to the reference.

**Why this priority**: every later story depends on the requirements being recorded. Recording them
as data keeps the catalog aligned with the framework's own words (constitution Principle IV).

**Independent Test**: compare the requirements recorded for each block with the reference page and
confirm that each MUST, SHOULD and MAY statement appears once, with the same level and text.

**Acceptance Scenarios**:

1. **Given** the reference page, **When** a maintainer views the Intent block's requirements,
   **Then** 3 MUST, 4 SHOULD and 1 MAY requirements are listed in the order of the page, each quoted
   and linked.
2. **Given** a sentence in the reference that contains two keywords, **When** the requirements are
   recorded, **Then** each keyword becomes its own requirement, and both quote the same sentence.
3. **Given** the framework-wide SHOULD statements, **When** the requirements are recorded, **Then**
   they are recorded once and are shown on every building block's claims, without counting toward
   full coverage.

---

### User Story 2 - Each coverage claim is assessed against its block's requirements (Priority: P1)

For each product and building block it covers, a maintainer records a verdict for every requirement
that applies: met, partly met, not met, or not shown by any source. Each verdict other than "not
shown" links to the source that supports it and has a short note. The coverage extent follows from
the verdicts: full when every MUST and SHOULD is met, partial otherwise.

**Why this priority**: this is what the user asked for. A visitor can then see why a product is
marked full or partial, instead of trusting a label.

**Independent Test**: assess one claim with every MUST and SHOULD met, and another with one SHOULD
partly met; confirm the first is full and the second partial.

**Acceptance Scenarios**:

1. **Given** a claim whose verdicts are "met" for every MUST and SHOULD that applies, **When** its
   extent is read, **Then** it is full, whatever the MAY verdicts are.
2. **Given** a claim with any MUST or SHOULD that is partly met, not met or not shown, **When** its
   extent is read, **Then** it is partial.
3. **Given** a claim with no verdicts yet, **When** its extent is read, **Then** it is partial and
   marked "not assessed".
4. **Given** a verdict of met, partly met or not met with no source, **When** a proposed change
   contains it, **Then** a check fails and names the claim and the requirement.
5. **Given** a verdict for a requirement that does not apply to the claim's block, **When** a
   proposed change contains it, **Then** a check fails.
6. **Given** a maintainer who tries to set full or partial by hand, **When** they look for the
   field, **Then** there is none to set: the extent is always computed.

---

### User Story 3 - Visitors view where a product meets the framework and where it falls short (Priority: P1)

A visitor clicks a product in the graph. For each building block it covers, the details card lists
the block's requirements grouped by MUST, SHOULD and MAY, each with its verdict, note and sources.
Requirements that keep the product from full coverage are shown first. The graph's solid and dashed
lines and the coverage filter follow the computed extent.

**Why this priority**: the user's example: NetBox on the Intent block should be partial, or at least
show which requirements it falls short on.

**Independent Test**: open a product with a partial claim and confirm the card names each MUST or
SHOULD that is not met, with its verdict and source.

**Acceptance Scenarios**:

1. **Given** a product with a partial claim, **When** the visitor opens its details, **Then** the
   card lists each MUST and SHOULD that is not met, before the met ones, with its verdict, note and
   sources.
2. **Given** a claim with a MUST requirement not met, **When** the visitor views it, **Then** the
   card says that the product does not meet a MUST requirement of the block.
3. **Given** a claim with no verdicts, **When** the visitor views it, **Then** the card says the
   claim is not assessed yet, and the line in the graph is dashed.
4. **Given** the coverage filter set to "full", **When** the graph updates, **Then** only claims
   computed as full are shown.
5. **Given** a requirement in the card, **When** the visitor follows its link, **Then** the framework
   reference opens.

---

### User Story 4 - The existing catalog is assessed and approved (Priority: P2)

The 97 existing claims are researched against their blocks' requirements. The proposed verdicts,
with sources and notes, are presented to the user for approval before they are loaded through a
proposed change.

**Why this priority**: without verdicts, every claim shows as partial and "not assessed", so the
feature would show nothing useful. The research is large, so it follows the model work.

**Independent Test**: confirm that every claim on `main` has one verdict for each requirement that
applies to its block, and that the user approved the set.

**Acceptance Scenarios**:

1. **Given** the proposed verdicts, **When** the user reviews them, **Then** they are grouped by block
   and product, with the computed extent before and after for each claim.
2. **Given** the approved verdicts, **When** they are loaded, **Then** they reach `main` only through a
   proposed change, and all checks pass.
3. **Given** a verdict whose sources do not state the fact, **When** the research is done, **Then** the
   verdict is "not shown by any source", not a guess.

---

### User Story 5 - New submissions are assessed during review (Priority: P2)

A visitor submits a product as before, but no longer chooses full or partial for each building
block. The new claims show as "not assessed". The maintainer reviewing the proposed change adds the
verdicts before merging.

**Why this priority**: keeps the form short for visitors and keeps the verdicts consistent, because
maintainers apply the same rule to every product.

**Independent Test**: submit a product, confirm the form has no full or partial choice and the new
claims show as not assessed, then add verdicts on the branch and confirm the extent changes.

**Acceptance Scenarios**:

1. **Given** the submission form, **When** a visitor adds a building block, **Then** they choose the
   block, a note and sources, and no extent.
2. **Given** a merged submission without verdicts, **When** the graph shows it, **Then** its lines are
   dashed and the card says "not assessed".
3. **Given** a maintainer adding verdicts on a submission branch, **When** the checks run, **Then**
   the submission check still passes, because the verdicts belong to new claims.

### Edge Cases

- A requirement statement changes in the framework reference. The maintainer updates the recorded
  text and link; verdicts stay attached to the requirement and are reviewed again.
- The framework adds a requirement. Every claim of that block becomes partial ("not shown") until it
  is assessed, which is correct under the rule.
- The Presentation block has no SHOULD requirement. Full coverage needs only its MUST.
- The framework's statement that "all the blocks MAY be implemented by one or more components"
  describes how a solution is built, not what a product does. It is not recorded as a requirement.
- A product meets a requirement only with a paid edition or plugin. The verdict is "partly met" or
  "met" with the note naming the edition or plugin, depending on what the source states.
- A product's own documentation is the only source. The verdict may use it, and the note says that
  the vendor states it (constitution Principle III).
- Infrahub, made by OpsMill, is assessed with the same rule and the same kind of sources as every
  other product.

## Requirements *(mandatory)*

### Functional Requirements

**Requirements recorded as data**

- **FR-001**: The catalog MUST record each requirement with its building block (or none, for a
  framework-wide requirement), its level (MUST, SHOULD or MAY), its order on the reference page, its
  text quoted from the reference, and a link to the reference.
- **FR-002**: A reference sentence with two keywords MUST be recorded as two requirements.
- **FR-003**: Framework-wide requirements MUST be assessed for every claim and shown with it, and
  MUST NOT count toward full coverage (user decision, 2026-10-27).
- **FR-004**: Requirements MUST be loaded from object files, like the building blocks.

**Verdicts and computed extent**

- **FR-005**: For each claim, the catalog MUST allow one verdict for each requirement that applies:
  met, partly met, not met, or not shown by any source, with an optional note.
- **FR-006**: A verdict of met, partly met or not met MUST link to at least one source. A verdict of
  "not shown" MUST NOT need one.
- **FR-007**: The extent of a claim MUST be computed: full when every MUST and SHOULD requirement of
  the claim's building block has the verdict "met", partial otherwise. A missing verdict counts as not
  met. MAY verdicts and framework-wide verdicts MUST NOT change the extent.
- **FR-008**: The extent MUST NOT be settable by hand anywhere: in Infrahub, in object files or in the
  submission form.
- **FR-009**: Checks on every proposed change MUST fail when a verdict lacks a required source, when a
  verdict is for a requirement that does not apply to its claim's block, or when a claim has two
  verdicts for one requirement.
- **FR-010**: The submission check MUST treat verdicts like other records: on a submission branch,
  verdicts of claims already on `main` MUST NOT change.

**Web app and report**

- **FR-011**: The details card MUST list, for each covered block, its requirements grouped by level,
  with verdict, note and sources, and list the MUST and SHOULD requirements that are not met first.
- **FR-012**: The card MUST state when a MUST requirement is not met, and when a claim is not assessed.
- **FR-013**: Graph lines, the coverage filter and the coverage report MUST use the computed extent.
- **FR-014**: The submission form MUST NOT ask for an extent. New claims MUST start with no verdicts.

**Initial assessment**

- **FR-015**: Every claim on `main` MUST have a verdict for each requirement that applies before this
  feature is finished.
- **FR-016**: The verdicts MUST be presented to the user for approval before they are loaded, and
  MUST reach `main` only through a proposed change.

### Key Entities

- **Requirement**: one MUST, SHOULD or MAY statement of the framework. Belongs to one building block,
  or to none when framework-wide. Has a level, an order, the quoted text and a link.
- **Verdict**: the assessment of one claim against one requirement. Has a value (met, partly met, not
  met, not shown), a note and sources. Belongs to the claim.
- **Coverage claim**: as before, but its extent is computed from its verdicts instead of being
  recorded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the MUST, SHOULD and MAY statements on the reference page are recorded, with
  the same level and text, and none is recorded twice.
- **SC-002**: 100% of claims on `main` have one verdict for each requirement that applies.
- **SC-003**: 100% of verdicts other than "not shown" link to at least one source.
- **SC-004**: For 100% of claims, the extent shown in the graph, the filter and the report matches the
  rule in FR-007.
- **SC-005**: A visitor finds which requirements keep a product from full coverage on a block in under
  30 seconds after opening the app.
- **SC-006**: The user approves 100% of the verdicts before they reach `main`.

## Assumptions

- The requirements are taken from the reference page as it was on 2026-10-23. Later changes to the
  framework are applied by hand (edge cases).
- "Partly met" counts as not met for full coverage, by the user's rule.
- The framework-wide SHOULD statement is split into two requirements: software engineering practices
  (version control, CI/CD), and machine-friendly APIs documented by a schema.
- Verdicts are researched from public sources: product documentation, repositories and vendor pages.
  When those do not state a fact, the verdict is "not shown", even if the product may support it.
- The existing extent values are replaced by the computed ones. Some claims now marked full will
  become partial, including NetBox, Nautobot and Infrahub on Intent, unless their sources show every
  MUST and SHOULD as met.
- The live beta deployment is updated after the feature is merged and pushed, with the user's
  approval.
