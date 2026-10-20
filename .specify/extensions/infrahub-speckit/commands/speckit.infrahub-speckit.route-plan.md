---
description: "Hook command — runs before /speckit.plan in Infrahub projects. Invokes the matching infrahub-managing-* skill so Phase 0 research and data-model design are grounded in authoritative Infrahub reference material."
---

# Infrahub Routing — pre-plan hook

This command is fired as a `before_plan` hook by the `infrahub-speckit` extension. It runs every time the `speckit-plan` skill is invoked. If `.infrahub.yml` is not present, this command is a no-op.

**MANDATORY — do NOT skip, defer, or rationalize around this.**

Before the core `speckit-plan` skill generates any design artifacts (`research.md`, `data-model.md`, `contracts/`), the matching Infrahub skill must be loaded. The skill loads authoritative reference material that design decisions MUST be consistent with. Skill content is NOT persisted across commands; each command starts fresh, so the skill MUST be re-loaded here even if it was loaded during `/speckit.specify`.

## Hook return semantics

Throughout this file, **"return"** means: stop emitting hook-command output and let control flow back to the calling core skill. Do NOT terminate the session, abort the parent slash command, or skip the core skill body. The spec-kit hook contract requires this hook to either:

- emit a no-routing line and return (no-op case), OR
- emit the Step 5 directive block and return (routing case), OR
- emit a user-facing error message and halt the entire command sequence (preflight failure case — the calling skill should NOT proceed in this case).

The third case is the only one where the calling skill should not resume.

## Step 1 — Detect Infrahub project

If the repository has no `.infrahub.yml`, emit:

```text
[infrahub-speckit] No .infrahub.yml detected. No routing applied.
```

Then return. The core plan skill runs unchanged.

## Step 2 — Verify required Infrahub skills are installed

Confirm these skills appear in your available-skills inventory:

- `infrahub-managing-schemas`
- `infrahub-managing-transforms`
- `infrahub-managing-checks`
- `infrahub-managing-generators`
- `infrahub-managing-menus`
- `infrahub-managing-objects`

**If ANY are missing**, halt and tell the user:

```text
The infrahub-speckit extension requires the opsmill/infrahub Claude Code skills.

Install (recommended):
  npx skills add opsmill/infrahub-skills

Or via the Claude Code plugin marketplace:
  /plugin marketplace add opsmill/claude-marketplace
  /plugin install infrahub@opsmill

Docs: https://docs.infrahub.app/skills/installation-setup

After installing, restart this session and re-run /speckit.plan.
```

Do NOT proceed further until the skills are installed. Do NOT continue to later steps or emit any routing directive — exit the hook with the user-facing error message only.

## Step 3 — Classify the artifact type from `spec.md`

1. Read `spec.md` from the current feature directory (resolve via `.specify/feature.json` or by inspecting the current working branch, however the core skill resolves it).
2. Classify the Infrahub artifact type from the spec content:

   | Artifact Type | Signals in Spec | Skill to Invoke |
   |---------------|-----------------|-----------------|
   | **Schema**    | schema, data model, nodes, attributes, relationships, generics, namespace, kind, CoreFileObject, inherit_from | `infrahub-managing-schemas` |
   | **Transform** | transform, render, config, artifact, jinja, device config | `infrahub-managing-transforms` |
   | **Check**     | check, validate, validation, enforce, rule, constraint | `infrahub-managing-checks` |
   | **Generator** | generator, auto-create, design-driven, topology, provision | `infrahub-managing-generators` |
   | **Menu**      | menu, navigation, sidebar, UI | `infrahub-managing-menus` |

3. If the spec involves multiple artifact types, invoke the skill for the PRIMARY type (the one being designed in this cycle).

## Step 4 — Invoke the matched skill

Invoke the matched skill using the Skill tool BEFORE returning. Use the skill's reference material when:

- Writing `data-model.md` (entity definitions, attribute kinds, relationship types)
- Making research decisions (SDK patterns, API conventions, naming rules)
- Validating the design against Infrahub capabilities

**Anti-rationalization check** — if you think "I already researched this via WebFetch" or "I know Infrahub well enough" or "the spec already has everything I need", invoke the skill anyway. The skill has curated reference material that general knowledge and web fetches do not provide.

## Step 5 — Emit the routing record and return

Emit a single status line:

```text
[infrahub-speckit routing — applies to this /speckit.plan run only]

Skill loaded: <SKILL-NAME>
```

Then continue to Step 6 before returning — do not return yet.

## Step 6 — Detect Spec Kit-native spec and decide whether to inject shape directives

This step determines whether the current feature directory has a post-migration, Spec Kit-native `spec.md`. Only post-migration specs receive shape injection; old-shape specs continue to work unchanged.

**Detection heuristic:**

Read `spec.md` from the current feature directory (the same path used in Step 3). Search for the heading `## User Scenarios & Testing` (exact string, case-sensitive). This heading is the canonical Spec Kit-native marker — present in all specs produced by the post-migration `presales-creating-pov-sdds` workflow, absent in old-shape specs from pre-migration destinations.

- **If `## User Scenarios & Testing` is found**: proceed to Step 7 and emit the shape directives.
- **If it is NOT found** (old-shape spec, missing file, or unreadable): skip Step 7 entirely. Emit nothing further. Return — the core `speckit-plan` skill runs next unchanged.

**Failure handling:** If `spec.md` is missing, the feature directory cannot be resolved, or the file is unreadable for any reason, treat the outcome the same as "heading not found" — skip injection silently. Log a single internal note:

```text
[infrahub-speckit] spec.md unreadable or missing — shape injection skipped. pov-audit Pass 1e will surface a MEDIUM finding if Cascade was needed.
```

Do NOT emit this note to the user. Then return.

## Step 7 — Emit Phase 1 shape directives (post-migration specs only)

This step fires only when Step 6 confirmed the spec is Spec Kit-native. Append the following two directives to the routing record already emitted in Step 5. The core `speckit-plan` skill reads the full hook output as part of its context before generating Phase 1 artifacts, and MUST honor both directives.

**Directive 1 — `quickstart.md` Phase 1 output shape:**

```text
[infrahub-speckit shape directive — applies to this /speckit.plan run only]

The /speckit.plan Phase 1 output for `quickstart.md` MUST follow Demo Arc table shape:

| # | Action | Observable | Time | SC ref |
|---|---|---|---|---|
| 1 | <action> | <observable> | ~Ns | SC-001 |

Each row binds to one Success Criterion (SC-NNN) from `spec.md > ## Success Criteria > ### Measurable Outcomes`. Total walkthrough time MUST be ≤10 min for the happy-path arc. Do not produce a prose narrative in place of this table — the table shape is mandatory.
```

**Directive 2 — `data-model.md` Phase 1 conditional "Cascade architecture" subsection:**

Read `spec.md > ## Context > ### Design reasoning` (the same spec.md already read in Step 6).

- **If that section contains the sentinel text `Cascade architecture subsection required`** (exact string; emitted by `analysis-cascade-vs-single-inference` when all four forcing tests return YES for cascade topology):

  ```text
  [infrahub-speckit shape directive — applies to this /speckit.plan run only]

  When generating the Phase 1 output for `data-model.md`, the document MUST include a "Cascade architecture" subsection covering all four of the following points:
  - GeneratorTarget inheritance points (which nodes each cascading generator targets and how they inherit from a shared base)
  - `branch_scope: "other_branches"` trigger config (the branch-scope setting that causes downstream generators to re-run when the upstream generator commits to a different branch)
  - Checksum-guard scope per cascading generator (which fields each generator checksums to avoid redundant writes across cascade layers)
  - Layer-by-layer execution order (explicit ordering of generators in the cascade chain, from the first generator that creates objects to the last that consumes them)
  ```

- **If the sentinel is absent** (single-generator topology — the default), or if `## Context > ### Design reasoning` cannot be read for any reason: omit Directive 2 entirely. Log a single internal note if the section was unreadable:

  ```text
  [infrahub-speckit] Design reasoning section unreadable — Cascade subsection injection skipped. pov-audit Pass 1e will surface a MEDIUM finding if Cascade was needed.
  ```

  Do NOT emit this note to the user.

Then return. The core `speckit-plan` skill runs next.
