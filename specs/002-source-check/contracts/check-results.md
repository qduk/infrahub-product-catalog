# Contract: Source Check Results and Registration

## Check definition

| Item | Value |
|------|-------|
| Check name | `catalog_source_check` (global, no target group) |
| Python file | `checks/catalog_source_check.py`, class `CatalogSourceCheck` |
| Query name | `catalog_source_check` |
| Query file | `queries/catalog_source_check.gql` |
| Tests | `tests/test_checks.yml`, fixtures in `tests/fixtures/` |

## `.infrahub.yml` after this feature

```yaml
---
# Infrahub repository configuration.
# Schemas and object files are loaded with infrahubctl on an Infrahub branch, not imported from
# this repository, so that data reaches main only through a proposed change.
queries:
  - name: catalog_source_check
    file_path: queries/catalog_source_check.gql

check_definitions:
  - name: catalog_source_check
    class_name: CatalogSourceCheck
    file_path: checks/catalog_source_check.py
```

`check_definitions` takes no `query:` key. The class attribute `query` names the query.

## Messages

Every message names the product or source and says what to do (FR-008). `<...>` marks a value
filled in from the data.

| Level | Message |
|-------|---------|
| Error | `<full name>: the license model has no source. Add a license model source or remove the license model.` |
| Error | `<title> (<url>): the last-checked date <YYYY-MM-DD> is in the future. Correct the date.` |
| Information | `Due for review: <title> (<url>) was last checked on <YYYY-MM-DD>, more than 6 months ago. Open the source, confirm the facts it supports and update the last-checked date.` |

Each message carries the node's `id` and kind, so the proposed change links it to the node.

## Running the check

| Where | How | What the maintainer views |
|-------|-----|---------------------------|
| Proposed change | Runs by itself when the proposed change is opened or updated | The "User" check on the proposed change's **Checks** tab, with every message. |
| By hand | `uv run infrahubctl check catalog_source_check --branch <branch> --format-json` | One JSON line per message, with its level. The command exits with status 1 when there is an error. |

## Repository registration

`bootstrap/repository.yml`:

```yaml
---
apiVersion: infrahub.app/v1
kind: Object
spec:
  kind: CoreReadOnlyRepository
  data:
    - name: infrahub-product-catalog
      location: https://github.com/qduk/infrahub-product-catalog.git
      ref: main
```

After a change to the check is pushed to `main` on GitHub, run **Import latest commit** on the
repository in the Infrahub web interface.
