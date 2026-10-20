# Quickstart: Validate the Catalog Schema

**Feature**: [spec.md](./spec.md) | **Data model**: [data-model.md](./data-model.md) |
**Object files**: [contracts/object-files.md](./contracts/object-files.md)

## Prerequisites

- The local instance is running: `docker compose up -d`, then `uv run infrahubctl info` shows
  `http://localhost:8100` as connected.
- `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec`
- The schema and object files from this feature exist in `schemas/` and `objects/`, with at least
  three products whose claims include one building block covered fully by one product and partly
  by another.
- Work on an Infrahub branch: `uv run infrahubctl branch create catalog-schema`, and pass
  `--branch catalog-schema` to every command below.

## Demo arc

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | `uv run infrahubctl schema check schemas/` then `uv run infrahubctl schema load schemas/` | Both commands finish with no errors. Five `Catalog` node types appear in the web interface. | ~60s | SC-005 |
| 2 | `uv run infrahubctl object load objects/01_building_blocks.yml` | One load with no errors. The building block list shows six blocks, each with a definition link that opens the framework's page. | ~45s | SC-001 |
| 3 | `uv run infrahubctl object load objects/` | Sources, publishers, products and claims load with no errors. Running the command again creates nothing new. | ~45s | SC-001 |
| 4 | In the web interface, record a new product with three coverage claims and their sources, including a source for its publisher and description | The product is saved and shows its three claims, each with an extent and sources. Time taken is under 10 minutes. | ~4m | SC-002 |
| 5 | Try to save a claim with no source, and a product with no description source | Infrahub refuses both and names the missing field. | ~45s | SC-003 |
| 6 | Open the building block covered fully by one product and partly by another | Its claims list shows both products with their extents, in one step from the block. | ~30s | SC-004 |
| 7 | Open one of those claims and follow its source | The source opens in one step and shows its title, link and last-checked date. | ~30s | SC-004 |
| 8 | Add a seventh test block to a copy of `01_building_blocks.yml`, load it, then delete the test block | The block appears and is deleted without any schema change. | ~60s | SC-005 |
| 9 | Try to delete a building block that has a claim | Infrahub refuses and names the claim that links to it. | ~30s | SC-003 |

Total time: about 9 minutes 45 seconds, most of it in step 4.

## Clean up

- Delete the Infrahub branch: `uv run infrahubctl branch delete catalog-schema`, or merge it
  through a proposed change once the arc passes.

## Results

Run on 2026-10-20 against the Infrahub branch `catalog-schema` of the local instance
(Infrahub 1.11.8). The web interface steps were run through Infrahub's GraphQL API, which applies
the same rules, because the person running the arc had no access to a browser. Times were not
measured for each row. The command-line rows each finished in under 10 seconds.

| # | Outcome |
|---|---|
| 1 | Pass. `schema check` and `schema load` finished with no errors. The menu lists the five `Catalog` node types. |
| 2 | Pass. Six building blocks loaded from one file. The page at each definition link has a section with the matching anchor. |
| 3 | Pass. 8 sources, 3 publishers, 3 products and 5 claims loaded. A second load left all counts the same. |
| 4 | Not run. This row times a person entering a product in the web interface and still needs a person to run it. |
| 5 | Pass. Infrahub refused a claim with no source ("sources is mandatory") and a product with no description source ("description_sources is mandatory"). |
| 6 | Pass. Collector lists Red Hat Ansible (partial) and Stardust Systems SuzieQ (full), each with its source. |
| 7 | Pass. The Intent claim's source shows its title, link and last-checked date. |
| 8 | Pass. A seventh test block loaded from a copy of the data file and was then deleted, with no schema change. |
| 9 | Pass. Infrahub refused to delete Collector because a coverage claim links to it. |

Not checked: spec User Story 4, scenario 3 (one source supporting claims for two products). No
source in the current data supports claims for more than one product.
