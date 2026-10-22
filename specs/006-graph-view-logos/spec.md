# Feature Specification: Graph View with Logos

**Feature Branch**: `006-graph-view-logos`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Graph view with logos: replace the box layout in the public catalog web
app with an interactive graph like Infrahub's own graph views. The six building blocks are large
nodes in the framework colours, placed where the Network Automation Framework diagram puts them;
each product is a smaller node, linked to every building block it covers with a solid line for full
coverage and a dashed line for partial coverage. Visitors pan and zoom, click a node to highlight
its links and open its details, and the existing status, coverage and building block filters hide
nodes and links. Product nodes show the product's official logo, stored as files in the web app
with a manifest that records the source page of each logo; products without a logo show their
initials. The page states that logos are trademarks of their owners."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore the catalog as a graph (Priority: P1)

A network engineer opens the web app and sees the catalog as a graph. The six building blocks are
large nodes in the framework's colours, arranged as in the framework diagram:
- Presentation at the top;
- Observability, Orchestrator and Intent in the middle;
- Collector and Executor below.

Products are smaller nodes. Each has a line to every building block it covers: a solid line for
full coverage, a dashed line for partial coverage. A product that covers several blocks sits
between them. The engineer pans and zooms to look closer.

**Why this priority**: the user asked for a view like Infrahub's graph views instead of boxes. The
graph shows overlap between products, which boxes do not.

**Independent Test**: open the app and check that every coverage claim on `main` appears as one
line between the right product and block, with the right line style.

**Acceptance Scenarios**:

1. **Given** the catalog on `main`, **When** a visitor opens the app, **Then** the six building
   blocks appear as large nodes in the framework layout, and every product with a claim appears as a
   node linked to each block it covers.
2. **Given** a full claim and a partial claim, **When** the visitor looks at the lines, **Then** the
   full claim uses a solid line and the partial claim a dashed line.
3. **Given** the graph, **When** the visitor drags, scrolls or uses the zoom controls, **Then** the
   view pans and zooms, and a "fit" control returns to the whole graph.
4. **Given** a product that covers more than one block, **When** the graph is laid out, **Then** the
   product node sits between the blocks it covers.

---

### User Story 2 - Focus on one product or block (Priority: P1)

The visitor clicks a product node. Its lines and the blocks it covers are highlighted, the rest of
the graph fades, and the details panel opens with the product's facts and sources. Clicking a block
node highlights every product linked to it. Clicking empty space clears the highlight.

**Why this priority**: with 50 products and almost 100 lines, the graph is only readable if the
visitor can focus on one part of it.

**Independent Test**: click a product and confirm only its lines and blocks stay highlighted and its
details open; click a block and confirm its products stay highlighted.

**Acceptance Scenarios**:

1. **Given** the graph, **When** the visitor clicks a product, **Then** its lines and blocks are
   highlighted, other nodes and lines fade, and the details panel shows the product.
2. **Given** the graph, **When** the visitor clicks a block, **Then** the block and every product
   linked to it are highlighted, and the others fade.
3. **Given** a highlight, **When** the visitor clicks empty space or presses Escape, **Then** the
   highlight clears and the details panel closes.

---

### User Story 3 - Filter the graph (Priority: P1)

The status, coverage and building block filters from the previous version work on the graph: they
hide product nodes and lines that do not match, and showing a single building block shows only that
block and its products. Filters stay in the page address.

**Why this priority**: the filters were part of the previous version, and the user asked for them to
keep working.

**Independent Test**: apply each filter and confirm that the nodes and lines shown match the
catalog data.

**Acceptance Scenarios**:

1. **Given** the default filters, **When** the app opens, **Then** only active products and their
   lines are shown.
2. **Given** the coverage filter set to "full", **When** the graph updates, **Then** no dashed line
   is shown, and products left with no line are hidden.
3. **Given** a single building block selected, **When** the graph updates, **Then** only that block,
   its products and their lines to it are shown.
4. **Given** a filtered view, **When** the visitor opens the copied page address elsewhere, **Then**
   the same filters apply.

---

### User Story 4 - Recognise products by their logos (Priority: P2)

Each product node shows the product's official logo, so visitors recognise products as they do on
the Network Automation Map. A product with no logo on file shows its initials in the node. The page
says that logos are trademarks of their owners.

**Why this priority**: logos make the graph faster to read, but the graph works without them.

**Independent Test**: open the graph and confirm that products with a logo on file show it and that
a product without one shows its initials.

**Acceptance Scenarios**:

1. **Given** a product with a logo on file, **When** the graph shows it, **Then** its node shows the
   logo and its name.
2. **Given** a product with no logo on file, **When** the graph shows it, **Then** its node shows
   its initials and its name.
3. **Given** a logo file that fails to load, **When** the graph shows the product, **Then** the node
   falls back to the initials.
4. **Given** the page, **When** the visitor reads its footer, **Then** it states that product names
   and logos are trademarks of their owners and are used only to identify the products.
5. **Given** any logo file, **When** a maintainer checks the manifest, **Then** the manifest names
   the page it came from.

### Edge Cases

- A product covers no building block. It is not shown in the graph, because it has no line. The
  footer counts it among the products in the catalog.
- A new building block is added to the catalog. It appears as a block node in an extra row, and its
  products link to it.
- A newly merged product has no logo yet. It shows its initials until a maintainer adds a logo.
- A logo is dark on a transparent background and would disappear on the dark page. The node draws
  logos on a light tile, so every logo stays visible.
- A narrow screen. The graph still pans and zooms with touch, and the "fit" control shows the whole
  graph.

## Requirements *(mandatory)*

### Functional Requirements

**Graph**

- **FR-001**: The app MUST show the catalog as a graph and MUST no longer show the box layout.
- **FR-002**: Building blocks MUST be large nodes in the framework colours, placed as in the
  framework diagram, with any block not in that diagram in an extra row. Blocks MUST come from the
  catalog (constitution Principle IV).
- **FR-003**: Each product with at least one claim MUST be a node, linked to each block it covers by
  one line: solid for full coverage, dashed for partial coverage.
- **FR-004**: Product nodes MUST be placed near the blocks they cover, between them when a product
  covers more than one, and MUST NOT overlap each other at the default zoom.
- **FR-005**: Visitors MUST be able to pan, zoom and fit the whole graph with the mouse, a trackpad,
  touch and on-screen controls.
- **FR-006**: Clicking a product MUST highlight it, its lines and its blocks, fade the rest, and open
  its details. Clicking a block MUST highlight it and its products. Clicking empty space or pressing
  Escape MUST clear the highlight.
- **FR-007**: Discontinued and acquired products MUST look different from active ones, and their
  status MUST be written on the node.
- **FR-008**: The status, coverage and building block filters, the page-address encoding and the
  details panel from feature 005 MUST keep working on the graph.

**Logos**

- **FR-009**: Product nodes MUST show the product's logo when a logo file is on record for it, and
  its initials otherwise or when the file fails to load.
- **FR-010**: Logo files MUST be stored with the web app. The app MUST NOT load logos from other
  websites.
- **FR-011**: A manifest MUST list every logo file with the product it belongs to, the page it came
  from, and the file address it was downloaded from.
- **FR-012**: Logos MUST be shown only as images. Logo files MUST NOT contain scripts or links to
  other websites.
- **FR-013**: The page MUST state that product names and logos are trademarks of their owners, used
  only to identify the products.
- **FR-014**: Visitors MUST NOT be able to upload logos. Maintainers add logos to the web app.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the coverage claims on `main` appear as lines when all filters are off, with
  the right line style.
- **SC-002**: A visitor finds every product linked to a given block in under 30 seconds after
  opening the app.
- **SC-003**: A filter change or a click on a node updates the graph in under 1 second.
- **SC-004**: At least 90% of products show their official logo.
- **SC-005**: 100% of logo files have a source page in the manifest, and 0 logos are loaded from
  other websites.

## Assumptions

- The graph replaces the box layout entirely, by the user's decision. A text list for screen readers
  is out of scope for this feature.
- Logos come from the publishers' own pages: press kits, official repositories or their websites.
  Showing a logo to identify a product is common practice, but the user should confirm the
  trademark notice with whoever handles legal questions before the app is public.
- Logos are drawn on a light tile inside the dark node, so that dark logos stay visible.
- The look follows Infrahub's own graph views: rounded nodes, smooth lines, and pan and zoom
  controls in a corner.
- No change to the catalog schema, the service or the submission form.
