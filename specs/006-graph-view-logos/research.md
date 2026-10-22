# Research: Graph View with Logos

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-21

## R1. Graph library

- **Decision**: React Flow (`@xyflow/react`, MIT license).
- **Rationale**: Infrahub 1.11.8's own web interface uses `@xyflow/react` for its graph and schema
  views. Its `package.json` lists `@xyflow/react` and `dagre`, and the local instance's web bundle
  contains the React Flow code. Using the same library gives the same look: rounded custom nodes,
  smooth edges, and pan, zoom and fit controls. It renders nodes as React components, so logos,
  initials and status labels are plain JSX, rendered as text.
- **Alternatives considered**:
  - Cytoscape or Sigma, which draw on a canvas. Rejected: harder to style like Infrahub and to
    render logos with fallbacks.
  - dagre layout. Rejected because it arranges nodes in layers and cannot keep the blocks in the
    framework's arrangement (R2).

## R2. Layout

- **Decision**: a small deterministic layout in `src/graph/layout.ts`.
  - **Blocks**: at fixed positions that follow the framework diagram: Presentation at the top
    centre; Observability, Orchestrator and Intent in a middle row; Collector and Executor in a
    bottom row between them. Unknown blocks go in a row below.
  - **Products with one block**: placed on rings around that block, in name order.
  - **Products with several blocks**: placed at the average position of their blocks, pulled
    slightly toward the outside so they do not sit on a block.
  - **Overlaps**: a fixed number of passes push overlapping product nodes apart.
  The same catalog always gives the same picture.
- **Rationale**: FR-002 needs the framework arrangement and FR-004 needs products between their
  blocks. A predictable result can be tested.

## R3. Highlight and fade

- **Decision**: one "focus" state, either a product or a block. Nodes and edges outside the focus
  get a faded style. Clicking the background or pressing Escape clears the focus.

## R4. Logos

- **Decision**:
  - Files go in `frontend/web/public/logos/<slug>.<svg|png|webp>`. The slug is the product's full
    name in lower case, with runs of other characters replaced by `-`.
  - `frontend/web/src/graph/logos.json` lists every file as
    `{slug, file, logo_of, source_page, file_url, brand_guidelines_url, notes}`.
  - Logos are drawn with `<img>` on a light rounded tile, so dark logos stay visible on the dark
    page (spec edge case). `<img>` never runs scripts inside an SVG.
  - A test checks every SVG for `<script>`, `on…=` attributes, `<foreignObject>` and external
    references, and checks that every manifest entry has a file and a source page (FR-011,
    FR-012).
- **Rationale**: the user chose files in the web app (FR-010). Serving them from the app means no
  visitor's address is sent to vendor websites.
- **Collection**: two research agents downloaded the logos from publishers' own pages on
  2026-10-21. Their manifests record each source page.

## R5. Trademark notice

- **Decision**: the footer reads "Product names and logos are trademarks of their respective
  owners. They are used only to identify the products. Their use does not imply endorsement."
