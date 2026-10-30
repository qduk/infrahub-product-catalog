# Record a product in the catalog

These steps add a network automation product, its publisher, its sources and the building blocks
it covers. The file format is in
[contracts/object-files.md](../../specs/001-catalog-schema/contracts/object-files.md).

## Before you start

- The local instance is running. `uv run infrahubctl info` shows `http://localhost:8100` as
  connected.
- Run `export INFRAHUB_API_TOKEN=06438eb2-8019-4776-878c-0941b1f1d1ec`.
- Create an Infrahub branch for the change, for example
  `uv run infrahubctl branch create add-<product>`.

## Steps

1. Collect a source for each fact before you write anything.
   - One source for the publisher.
   - One source for the description.
   - One source for the license model, if any source states it.
   - One or more sources for each building block the product covers, and whether it covers the
     block fully or partly.
   A fact that no source states stays out of the catalog.
2. Add each new source to `objects/02_sources.yml`, with a title, the URL and today's date as
   `last_checked`. Reuse an existing entry when the URL is already there.
3. Add the publisher to `objects/03_publishers.yml` if it is not there yet.
4. Add the product to `objects/04_products.yml`.
   - Refer to the publisher by name and to sources by URL.
   - Write a description that states what the product does, without marketing language.
   - Leave out `license_model` when no source states it.
   - Add one entry under `coverage_claims` for each building block, with an optional `note` and at
     least one source. There is no `extent`: the catalog computes full or partial coverage from the
     requirement verdicts.
   - Add the claim's requirement verdicts to `objects/06_requirement_verdicts.yml`: one for each
     MUST, SHOULD and MAY requirement of the block and for the two framework-wide requirements.
     Each verdict is `met`, `partly_met`, `not_met` or `not_shown`, with a note and, unless it is
     `not_shown`, the source that states it. Refer to the claim as `["<publisher> <product>", "<block>"]`.
     A claim is full only when every MUST and SHOULD of its block is `met`; framework-wide
     requirements are shown but do not count.
   - If the product is no longer sold, set `status` to `discontinued`. This includes a product
     that was absorbed into another company and is no longer sold on its own. Add the source that
     states it under `status_sources`, and `status_date` when the source gives a date. Leave all
     three out for a product that is still sold.
5. Check and load the files on your branch:

   ```bash
   uv run infrahubctl object validate --branch add-<product> objects/
   uv run infrahubctl object load --branch add-<product> objects/
   ```

6. Open the product in the web interface on your branch and check its publisher, sources and
   claims.
7. Run the source check on your branch:

   ```bash
   uv run infrahubctl check catalog_source_check --branch add-<product> --format-json
   ```

   Fix every `ERROR` line, for example a license model with no source. `INFO` lines that start
   with "Due for review" list sources to open again and confirm. They do not block the merge.
8. Open a proposed change from your branch to `main`. Infrahub runs the same check on it. Merge
   only through the proposed change: a direct branch merge skips the check.
9. On the proposed change, open the artifact `catalog-coverage-report`. It shows the coverage
   table as it will be after the merge. Check that the new product's claims appear in the right
   building block columns.

## Viewing the coverage report

The report is an artifact of the object **Catalog Report** > "Catalog coverage report". Open the
object and select **Artifacts** > `catalog-coverage-report`. Infrahub rebuilds it on every proposed
change. The report text depends only on the catalog data, so it shows as changed only when the
data changes.

## Renaming a building block, publisher or product

Object files find existing nodes by name. Changing a name in a file creates a new node and leaves
the old one in place. Rename the node in the web interface first, then change the name in the
file.
