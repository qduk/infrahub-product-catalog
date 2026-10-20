---
status: accepted
date: 2026-10-20
---

# Connect the repository to Infrahub as a read-only repository that provides only checks

## Context and problem statement

The catalog's source check must run on every proposed change, so that a product with a license
model and no source cannot be merged ([spec FR-009](../../specs/002-source-check/spec.md)).
Infrahub runs only checks that come from a Git repository connected to the instance. Until now
this repository was not connected, and every check was run by hand with `infrahubctl`.

The repository is public on GitHub at <https://github.com/qduk/infrahub-product-catalog>. The
evidence for this decision is in [research.md](../../specs/002-source-check/research.md), sections
R1 and R2.

## Decision drivers

- Infrahub must run the check on every proposed change.
- Infrahub must not write to the GitHub repository, and no GitHub token should be stored in the
  instance.
- Catalog data and schema must reach `main` only through a proposed change, where the check runs.

## Considered options

1. A read-only repository (`CoreReadOnlyRepository`) on `main`, with `.infrahub.yml` listing only
   checks and queries.
2. A read-write repository (`CoreRepository`).
3. A read-only repository whose `.infrahub.yml` also lists the schema and object files.

## Decision outcome

Chosen option: 1.

- A read-only repository needs no credential for a public repository and never writes to it.
- Option 2 needs a GitHub token with write access. It also polls GitHub several times a minute,
  creates an Infrahub branch for every Git branch, and pushes merges back to GitHub.
- Option 3 would import the object files straight into `main` on every import, so data would skip
  the proposed change where the check runs.

### Consequences

- Infrahub does not fetch new commits from a read-only repository by itself. After a change to a
  check is pushed to `main`, a maintainer runs **Import latest commit** in the web interface.
- Schema and object files are still loaded with `infrahubctl` on an Infrahub branch and merged
  through a proposed change.
- A direct branch merge skips the proposed change and therefore the check. Maintainers merge
  through proposed changes only.
- Constitution Principle II was amended to version 1.1.0 to describe the connection.
