# Implementation Plan: Graph View with Logos

**Branch**: `006-graph-view-logos` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/006-graph-view-logos/spec.md`

## Summary

The box layout in `frontend/web` is replaced by an interactive graph built with React Flow, the
library Infrahub's own graph views use:
- the six building blocks are large nodes in the framework arrangement;
- products are smaller nodes with their logos, linked to the blocks they cover by solid (full) or
  dashed (partial) lines.

A small deterministic layout places products near and between their blocks. Logos are files in
the web app, listed in a manifest with their source pages, and shown only as images. The filters,
page address and details panel from feature 005 carry over ([research.md](./research.md)).

## Technical Context

**Language/Version**: TypeScript with React 19 (existing `frontend/web`).

**Primary Dependencies**: adds `@xyflow/react` (MIT).

**Storage**: logo files in `frontend/web/public/logos/` and a manifest in `src/graph/logos.json`.

**Testing**: Vitest tests for the graph building, the layout (no overlaps, blocks in place), and the
logo manifest and SVG safety; the browser walkthrough in [quickstart.md](./quickstart.md).

**Target Platform**: current desktop and mobile browsers.

**Project Type**: front-end change only. The service and the catalog are unchanged.

**Performance Goals**: filter changes and clicks update the graph in under 1 second (SC-003), with
50 products and about 100 edges.

**Constraints**:
- No logos from other websites (FR-010).
- Logos only through `<img>` (FR-012).

**Scale/Scope**: one view, about 6 new source files, about 50 logo files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this feature meets it | Status |
|-----------|---------------------------|--------|
| I. Schema-first modeling | No schema change. | Pass |
| II. Validation on the local instance | The graph is built from the service running against the local instance; the walkthrough runs there. | Pass |
| III. Sourced product records | Logos are not catalog facts, but each has a source page in the manifest, in the same spirit. | Pass |
| IV. Framework terms recorded as data | Blocks come from the catalog; only their positions are keyed by name, and unknown blocks get an extra row. | Pass |
| V. Infrahub conventions | Same graph library as Infrahub's own interface. | Pass |

## Project Structure

```text
frontend/web/
├── public/logos/                 # logo files
└── src/
    ├── graph/
    │   ├── buildGraph.ts         # catalog + filters + focus → nodes and edges
    │   ├── layout.ts             # block positions and product placement
    │   ├── logos.json            # logo manifest
    │   ├── logos.ts              # slug and logo lookup
    │   ├── nodes.tsx             # BlockNode and ProductNode
    │   └── CatalogGraph.tsx      # React Flow canvas, controls, focus handling
    ├── App.tsx                   # uses CatalogGraph instead of Diagram
    └── components/               # Diagram.tsx and Block.tsx removed
```

## Complexity Tracking

No constitution violations to justify.
