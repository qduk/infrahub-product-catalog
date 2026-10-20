<!--
Sync Impact Report
- Version change: template (unversioned) → 1.0.0
- Principles defined (all new, replacing template placeholders):
  - I. Schema-First Modeling
  - II. Validation on the Local Infrahub Instance
  - III. Sourced Product Records
  - IV. Framework Terms Recorded as Data
  - V. Infrahub Conventions Through the Managing Skills
- Added sections: Technical Constraints, Development Workflow, Governance
- Removed sections: none
- Templates: none modified. Dependent templates and commands read this file at runtime.
- Deferred TODOs: none
-->

# Infrahub Product Catalog Constitution

This repository runs an Infrahub instance that records network automation products and maps each
product to the building blocks of the Network Automation Framework that it covers.

## Core Principles

### I. Schema-First Modeling

- Every feature MUST start as a change to the schema files listed in `.infrahub.yml`.
- The schema change MUST pass `uv run infrahubctl schema check` before anyone writes object
  files, transforms, generators, checks or menus that depend on it.
- A node, attribute or relationship that the schema does not define MUST NOT appear in object
  files or GraphQL queries.

Rationale: the schema defines what the catalog can record. Data and automation written before the
schema exists have to be rewritten when the schema changes.

### II. Validation on the Local Infrahub Instance

- A change counts as done only after it is loaded into the local Infrahub instance
  (`http://localhost:8100`) and runs there without errors.
- Schemas are loaded with `uv run infrahubctl schema load`, object files with
  `uv run infrahubctl object load`, and menus with `uv run infrahubctl menu load`.
- Transforms, generators and checks are run with `uv run infrahubctl transform`,
  `uv run infrahubctl render`, `uv run infrahubctl generator` and `uv run infrahubctl check`,
  because this repository is not connected to the instance as a Git repository.
- A failed load or run MUST be reported with its output. It MUST NOT be reported as done.

Rationale: unit tests and schema checks do not catch every error that a running Infrahub server
returns. Loading into the local instance is the only check that matches how the catalog is used.

### III. Sourced Product Records

- Every product record MUST link to the source of each fact it states, such as the vendor's
  documentation or release notes.
- When no source states a fact, the record MUST leave the attribute empty. It MUST NOT fill the
  attribute with an assumed value.
- Product descriptions MUST state what the product does without marketing language. When a record
  quotes a vendor's claim, it MUST name the vendor as the source of the claim.

Rationale: people use the catalog to compare products. A value without a source cannot be checked,
and a wrong value leads to a wrong comparison.

### IV. Framework Terms Recorded as Data

- The building blocks of the Network Automation Framework MUST be recorded as nodes in Infrahub,
  loaded from object files, with a link to the framework's own definition of each block.
- Schemas, transforms, generators and checks MUST NOT hard-code the list of building blocks.
- Product records MUST use the framework's names for its building blocks exactly as the framework
  defines them.

Rationale: when the framework changes, the catalog is updated by editing object files, not code.
Using the framework's own names lets readers match the catalog to the framework.

### V. Infrahub Conventions Through the Managing Skills

- Before writing or editing a schema, object file, transform, generator, check, menu or GraphQL
  query, contributors MUST read the matching `infrahub-managing-*` skill.
- Nodes and generics MUST use PascalCase names. Attributes and relationships MUST use snake_case
  names.
- Every node MUST define a `human_friendly_id`. Every relationship that has a peer relationship in
  the other direction MUST set an `identifier`.
- A generic MUST be added only when two or more nodes share its attributes or relationships.

Rationale: the skills hold integration rules that the source code does not show. Changes that skip
them have passed unit tests and still failed against a running Infrahub server.

## Technical Constraints

- Infrahub version: 1.11.8, set in `docker-compose.yml`. That file is the unchanged file from
  <https://infrahub.opsmill.io>. Local changes MUST go in `docker-compose.override.yml`.
- The instance runs under the Docker Compose project name `infrahub-product-catalog`, and its web
  server is published on port 8100 unless `INFRAHUB_PORT` sets another port. Commands MUST NOT
  pass `-p infrahub`, because other stacks on this machine use that project name.
- `infrahubctl` MUST be run through uv (`uv run infrahubctl`). It is not installed on the PATH.
- Commands that change data use the default admin API token from `docker-compose.yml`, set in
  `INFRAHUB_API_TOKEN`. This token MUST NOT be used outside the local instance.
- Python 3.13 or later, with dependencies managed by uv in `pyproject.toml`.

## Development Workflow

- Features follow the Spec Kit sequence: `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`,
  `/speckit-implement`. The Infrahub routing hooks in `.specify/extensions.yml` run before the
  specify, plan and implement steps and MUST NOT be skipped.
- Each plan MUST include a constitution check that lists how the feature meets Principles I to V,
  and MUST justify any exception.
- Work is committed on a feature branch, not on `main`.
- Specs that the team keeps after a feature is done go in `dev/specs/`. Decisions that change the
  schema design or this constitution are recorded as decision records in `dev/adr/`.

## Governance

- This constitution takes precedence over other practices in this repository. `AGENTS.md` holds
  the operating instructions for the local instance and MUST stay consistent with this document.
- An amendment is made by running `/speckit-constitution`, and is reviewed in a pull request. An
  amendment that removes or redefines a principle MUST be recorded in `dev/adr/`.
- Versions follow semantic versioning:
  - MAJOR: a principle or section is removed or redefined in a way that makes earlier compliant
    work non-compliant.
  - MINOR: a principle or section is added, or its rules are materially expanded.
  - PATCH: wording, clarifications and typo fixes that do not change a rule.
- Every pull request review MUST confirm that the change complies with Principles I to V.

**Version**: 1.0.0 | **Ratified**: 2026-10-20 | **Last Amended**: 2026-10-20
