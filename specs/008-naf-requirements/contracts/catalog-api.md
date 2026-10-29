# Contract changes: catalog service and checks

## `GET /api/catalog`

New top-level list `requirements`, in reference order:

```json
{
  "identifier": "intent-should-2",
  "level": "should",
  "statement": "It SHOULD provide a consistent and unified view of the desired state, ...",
  "reference_url": "https://reference.networkautomation.forum/Framework/Framework/#intent",
  "block": "Intent"
}
```

`block` is `null` for framework-wide requirements.

Each claim:
- keeps `block`, `note`, `sources`;
- `extent` is now computed (`full` or `partial`);
- new `assessed` (boolean): false when the claim has no verdicts;
- new `verdicts`: `[{"requirement": "intent-should-2", "verdict": "partly_met", "note": "...", "sources": [{"title", "url"}]}]`.

## `POST /api/submissions`

`claims[].extent` is removed. A request that still sends it is accepted and the field is ignored, so
an open browser tab with the old form keeps working.

## `catalog_verdict_check` results

| Situation | Level | Message |
|-----------|-------|---------|
| Verdict other than not shown with no source | ERROR | `<claim name>, <requirement>: the verdict "<verdict>" has no source. Add the source that states it, or set the verdict to "not shown".` |
| Requirement of another block | ERROR | `<claim name>, <requirement>: this requirement belongs to <block>, not to the claim's block <claim block>. Delete the verdict.` |
