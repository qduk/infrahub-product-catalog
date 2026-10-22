---

description: "Task list for the graph view with logos"
---

# Tasks: Graph View with Logos

**Input**: Design documents from `specs/006-graph-view-logos/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/ui.md](./contracts/ui.md), [quickstart.md](./quickstart.md)

**Tests**: included for graph building, layout and the logo manifest.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Add `@xyflow/react` to `frontend/web/package.json` and import its stylesheet in
  `frontend/web/src/main.tsx`

## Phase 2: Foundational

- [X] T002 Write tests in `frontend/web/src/graph/buildGraph.test.ts`:
  - one edge per claim that passes the filters, solid for full and dashed for partial;
  - products with no visible claim are left out;
  - a single block shows only that block and its products;
  - focus on a product or a block marks the right nodes and edges as faded.
- [X] T003 Write tests in `frontend/web/src/graph/layout.test.ts`: blocks in the framework
  arrangement, unknown blocks in an extra row, product nodes do not overlap, a product with two
  blocks lies between them, the same input gives the same positions
- [X] T004 Write `frontend/web/src/graph/layout.ts` and `frontend/web/src/graph/buildGraph.ts` until
  the tests pass

## Phase 3: User Story 1 - Explore the catalog as a graph (Priority: P1) 🎯 MVP

- [X] T005 [US1] Write `frontend/web/src/graph/nodes.tsx` (BlockNode with colour, name and tagline;
  ProductNode with logo tile or initials, full name and status label) and
  `frontend/web/src/graph/CatalogGraph.tsx` (React Flow canvas, background, zoom and fit controls)
- [X] T006 [US1] Replace the diagram in `frontend/web/src/App.tsx` with `CatalogGraph`, remove
  `components/Diagram.tsx`, `components/Block.tsx` and their styles, and add the graph styles to
  `frontend/web/src/styles.css`

## Phase 4: User Story 2 - Focus on one product or block (Priority: P1)

- [X] T007 [US2] In `CatalogGraph.tsx`, handle clicks on nodes (focus and details), clicks on the
  background and the Escape key (clear)

## Phase 5: User Story 3 - Filter the graph (Priority: P1)

- [X] T008 [US3] Connect the existing filters and page address to `buildGraph`; add a "show only"
  action on block nodes; confirm `src/filters.test.ts` still passes

## Phase 6: User Story 4 - Recognise products by their logos (Priority: P2)

- [X] T009 [US4] Review the two logo manifests from the research agents, copy the accepted files to
  `frontend/web/public/logos/`, and write `frontend/web/src/graph/logos.json`
- [X] T010 [P] [US4] Write tests in `frontend/web/src/graph/logos.test.ts`: every manifest entry with
  a file has a source page and a file on disk; every SVG has no script, event attribute,
  foreignObject or external reference; slugs match the catalog's product names
- [X] T011 [US4] Write `frontend/web/src/graph/logos.ts` (slug and lookup) and use it in ProductNode
  with an initials fallback when the file is missing or fails to load
- [X] T012 [US4] Add the trademark notice from research R5 to the footer in `App.tsx`

## Phase 7: Polish

- [X] T013 Run `npm test` and `npm run build` in `frontend/web` with no errors
- [X] T014 Record the walkthrough results that can be checked without a browser in
  `specs/006-graph-view-logos/quickstart.md`, and ask the user to view the graph
- [ ] T015 Commit on `006-graph-view-logos`, merge into `main`, and ask the user before pushing

## Notes from implementation

- The building block filter became a dropdown in the filter bar, because block nodes are now graph
  nodes; clicking a block highlights it.
- `applyFilters` from feature 005 was removed; `buildGraph` applies the filters and its tests cover
  the same rules.
- Logo collection: the two research agents were interrupted by a usage limit and resumed; one
  stalled after writing its manifest. Both manifests are complete.
- The agents chose dark logos for some products and white ones for others, so each manifest entry
  records the tile colour (`tile`) it needs.
