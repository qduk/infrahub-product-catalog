# Quickstart: Validate the Graph View

**Prerequisites**: the service on port 8200 and the web app on port 5173 (`frontend/README.md`).

## Demo arc

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | Open the app | Six block nodes in the framework layout; product nodes with logos linked by solid and dashed lines. | ~30s | SC-001, SC-004 |
| 2 | Click Collector | Collector and its products stay bright; the rest fades. | ~20s | SC-002, SC-003 |
| 3 | Click Stardust Systems SuzieQ | Its two lines and blocks stay bright; details open with sources. | ~20s | SC-003 |
| 4 | Set coverage to "full" | All dashed lines disappear. | ~15s | SC-001, SC-003 |
| 5 | Add "discontinued" to status | Skybox and System Initiative appear with their status. | ~15s | SC-003 |
| 6 | Zoom out with the fit control, then into one block | The whole graph fits; zooming in shows logos clearly. | ~30s | SC-002 |
| 7 | Run `npm test` | Layout, filter and logo-manifest tests pass, including the SVG safety check. | ~20s | SC-005 |

Total time: about 2 minutes 30 seconds.

## Results

Run on 2026-10-21 with headless Chrome screenshots of the running app, because I cannot use a
browser interactively. Clicks (rows 2 and 3) need a person.

| # | Outcome |
|---|---|
| 1 | Pass. Six block nodes in the framework layout, product nodes with logos, solid and dashed lines in the block colours, and a working mini-map. On the live catalog, the layout test found no overlapping product nodes. |
| 2–3 | Covered by tests (focus fades the right nodes and edges). Needs a person to click. |
| 4–5 | Covered by tests; the `?block=Collector` and status page addresses render correctly in screenshots. |
| 6 | Zoom and fit controls are shown. Zooming needs a person. |
| 7 | Pass. 30 tests pass, including the logo manifest and SVG safety checks for all 50 logos. |

Logos: all 50 products have an official logo from the publisher's own pages. 26 are white or light
logos shown on a dark tile; 24 are shown on a light tile. The tile colours were chosen from a contact
sheet that showed every logo on both backgrounds.
