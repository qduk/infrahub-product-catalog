# Check Results Contract

Each message names the record with its label from Infrahub and says what to change (FR-013). Every
`log_error` and `log_info` message about a record also passes the record's `object_id` and
`object_type`.

## `catalog_submission_check`

| Situation | Level | Message |
|-----------|-------|---------|
| Branch name does not start with `submission-` | INFO | `This check applies only to submission branches (names that start with submission-).` |
| Record on `main` missing on the branch | ERROR | `<Kind label> <label> is on main but was deleted on this branch. A submission may only add records; restore it.` |
| Fact changed | ERROR | `<Kind label> <label>: <fact> differs from main. A submission may only add records; change it back, and make the edit on a separate branch.` |
| Building block added | ERROR | `Building block <label> was added. Building blocks come from the framework and are not added by submissions; delete it.` |

`<Kind label>` is one of: Publisher, Product, Source, Coverage claim, Building block.

## `catalog_duplicate_check`

| Situation | Level | Message |
|-----------|-------|---------|
| Two publishers | ERROR | `Publishers <a> and <b> have near-identical names. Keep one and move its products to it, or rename one.` |
| Two products of one publisher | ERROR | `Products <a> and <b> of <publisher> have near-identical names. Keep one, or rename one.` |
| Two sources | ERROR | `Sources <a> (<url a>) and <b> (<url b>) point to the same page. Keep one and link its facts to it.` |

## `catalog_coverage_check`

| Situation | Level | Message |
|-----------|-------|---------|
| Product with no claim | INFO | `Warning: <full name> covers no building block, so the web app does not show it. Add a coverage claim, or confirm that the product covers none.` |

## `catalog_unused_source_check`

| Situation | Level | Message |
|-----------|-------|---------|
| Source supports nothing | ERROR | `Source <title> (<url>) supports no product fact or coverage claim. Link it to the fact it supports, or delete it.` |
