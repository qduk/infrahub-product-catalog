# Research: Public Catalog Web App

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-21

## R1. Permissions for the service account (FR-017, FR-018, FR-020)

Tested on 2026-10-21 against the local instance (Infrahub 1.11.8) with a throwaway account whose
only role held the permissions below. The account, role, group and test data were removed
afterwards.

- **Decision**: one account, `catalog-web`, in the group `Catalog web service` with the role
  `Catalog submitter`, holding:
  - `object:Catalog:*:view:allow_all`: read the catalog on every branch;
  - `object:Catalog:*:create:allow_other`: create catalog nodes on branches other than `main`;
  - `object:Core:ProposedChange:create:allow_all` and `object:Core:ProposedChange:view:allow_all`;
  - `global:edit_default_branch:allow_all`: needed to open a proposed change, because proposed
    changes are stored on `main`.
- **Tested results**:
  - Without `edit_default_branch` the account could create branches, create catalog nodes on them,
    and delete branches, but could not open a proposed change ("You are not allowed to change data
    in the default branch").
  - With `edit_default_branch`, the account still could not create or update catalog nodes or
    tags on `main`, could not update or delete proposed changes, and could not merge a branch
    directly.
  - With `edit_default_branch`, the account **could merge its own proposed change** through
    `CoreProposedChangeMerge`, also when the role held `global:merge_proposed_change:deny`. The
    test node reached `main` and was removed afterwards.
- **User decision**: accept this for development on the local instance. Spec FR-020 blocks going
  live until Infrahub enforces the merge permission, or until proposed changes are opened by a
  separate internal process. The finding was written up for the Infrahub team privately and is not
  stored in this public repository.
- **Alternatives considered**:
  - An internal worker, not reachable from the internet, that opens the proposed changes.
    Recommended for going live; deferred by the user.
  - Maintainers open the proposed change themselves. Rejected by the user for now.

## R2. Architecture

- **Decision**: two parts in `frontend/`:
  - `frontend/web/`: a React and TypeScript single-page app built with Vite.
  - `frontend/api/`: a Python service built with FastAPI and the Infrahub SDK, its own uv
    project, which holds the service account token and offers two operations.
- **Rationale**:
  - The browser never sees an Infrahub credential (FR-018) and never talks to Infrahub (FR-017).
  - Python and the Infrahub SDK match the rest of the repository and give typed access to the
    catalog.
  - React suits the diagram layout, the filters and a form with nested claims.
- **Development wiring**: Vite proxies `/api` to the service on port 8200, so the browser sees one
  origin and no cross-origin rules are needed. Deployment uses the same pattern with a reverse
  proxy, which is a separate step.

## R3. Reading the catalog (FR-002 to FR-005)

- **Decision**: `GET /api/catalog` runs one GraphQL query on `main` and returns building blocks,
  publishers and products with their sources and claims as plain JSON. The service caches the
  result for 60 seconds. All filtering happens in the browser.
- **Rationale**: 50 products and about 100 claims make a small response (tens of kilobytes), so
  filters can update without a request (SC-003). A 60-second cache keeps load on Infrahub low and
  shows merged submissions within the 5 minutes of User Story 4.

## R4. Submitting a product (FR-009 to FR-016)

- **Decision**: `POST /api/submissions`:
  1. validates the body against the same rules as the form (FR-010, FR-016), with Pydantic;
  2. refuses a product whose name already exists for the chosen publisher on `main` (FR-014);
  3. creates the branch `submission-<YYYYMMDD>-<6 random hex characters>`;
  4. on that branch, reuses existing sources (matched by URL) and the existing publisher (matched
     by name), and creates the new sources, the publisher if new, the product and its claims;
  5. opens a proposed change named "Submission: <publisher> <product>", whose description says it
     came from the public form;
  6. returns the branch name as the visitor's reference (FR-013). Infrahub is not public, so the
     reference gives no access.
  If any step after 3 fails, the service deletes the branch and returns an error (FR-012).
- **Limits** (FR-016), enforced by both the form and the service:
  - product and publisher names: 100 characters;
  - descriptions and notes: 1,000 characters;
  - source titles: 200 characters;
  - URLs: 500 characters, `http` or `https` only;
  - at most one claim per building block, so 6 claims;
  - at most 20 distinct sources per submission.
- **Plain text** (FR-015): the React app renders every value as text. Nothing uses raw HTML.

## R5. Visual layout (FR-001)

- **Decision**: a CSS grid that follows the diagram the user supplied:
  - Presentation spans the top row;
  - Observability, Orchestrator and Intent fill the middle row;
  - Collector and Executor sit in the bottom row, under the outer columns.
  Colours follow the diagram: yellow Presentation, green Observability, cyan Orchestrator, orange
  Intent, red Collector, indigo Executor, on a dark background. On narrow screens the blocks stack
  in the same order. Infrastructure is shown as a grey footer bar without products, because it is
  not one of the six building blocks.
- **Rationale**: the user asked for the app to look like the framework diagram.

## R6. Filters in the page address (FR-008)

- **Decision**: query parameters `status` (comma-separated), `extent` (comma-separated) and `block`
  (one building block name). Missing parameters mean the defaults in FR-007.

## R7. Tests

- **Decision**:
  - `frontend/api`: pytest, with unit tests for validation and the submission steps, using a fake
    Infrahub client, plus one integration test against the local instance (marked, run on demand).
  - `frontend/web`: Vitest and Testing Library for the filter logic and the form validation.
  - A manual walkthrough in a browser for the layout (quickstart).
