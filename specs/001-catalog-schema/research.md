# Research: Network Automation Product Catalog Schema

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-20

Findings marked "tested" come from a test schema loaded on a throwaway Infrahub branch
(`spike-001`) on the local instance (Infrahub 1.11.8, infrahub-sdk 1.23.2). The branch was deleted
after the tests.

## R1. Building blocks of the Network Automation Framework

- **Decision**: record six building blocks, with names, descriptions and definition links taken
  from the framework's reference page,
  <https://reference.networkautomation.forum/Framework/Framework/>.

  | Name | Description quoted from the framework | Definition link |
  |------|---------------------------------------|-----------------|
  | Intent | "Defines the logic to handle and the persistence layer to store the desired state of the network, including both configuration and operational expectations." | `…/Framework/Framework/#intent` |
  | Observability | "It persists the actual network state, and defines the logic to process it." | `…/Framework/Framework/#observability` |
  | Orchestrator | "Defines how the automation tasks are coordinated and executed in response to events." | `…/Framework/Framework/#orchestrator` |
  | Executor | "Encompasses the actual tasks applied to the network to drive changes (e.g., updating configuration) as guided by the intended state." | `…/Framework/Framework/#executor` |
  | Collector | "In contrast to Executor, this component focuses on retrieving (i.e., reading) the actual state of the network." | `…/Framework/Framework/#collector` |
  | Presentation | "Provides the interfaces through which users interact with the system, including dashboards, graphical user interfaces (e.g., ITSM), and CLI tools." | `…/Framework/Framework/#presentation` |

- **Rationale**: constitution Principle IV requires the framework's own names and a link to its
  own definition. The OpsMill article
  [The Network Automation Framework We've All Been Waiting For](https://opsmill.com/blog/naf-network-automation-framework/)
  links to the same reference page.
- **Confirmed on 2026-10-20 (task T008)**: the page HTML has a section heading with each of the six
  anchors, and its "Architecture" list gives the descriptions above word for word. The planning
  draft of this table had shortened four of the descriptions. The page shows no framework version
  or date.
- **Alternatives considered**: the presentation
  [The Network Automation Map](https://www.swinog.ch/wp-content/uploads/2026/05/Damien_Garros-OpsMill-Network_Automation_Map_and_NAF_Framework.pdf)
  lists the same six blocks. It was not chosen as the source because it is a talk, not the
  framework's definition.

## R2. Reuse of an Infrahub Marketplace schema for publishers

- **Decision**: define a `CatalogPublisher` node in this repository. Do not pull
  `infrahub/organization`.
- **Rationale**: `infrahub/organization` v1.0.1 holds `OrganizationGeneric` and two nodes. The
  `OrganizationManufacturer` node has relationships to `DcimDeviceType` and `DcimPlatform`, so the
  file does not load without the DCIM schema, which this catalog does not need. The skill rules
  forbid copying marketplace YAML into the repository. Searches for "product", "catalog" and
  "vendor" returned no schema for software products.
- **Alternatives considered**: pull `infrahub/organization` together with the DCIM schemas. This was
  rejected because it adds device models that the catalog never uses.

## R3. A source for each product fact (FR-009)

- **Decision**: give `CatalogProduct` one relationship to `CatalogSource` for each fact:
  - `publisher_sources`, required, at least one source.
  - `description_sources`, required, at least one source.
  - `license_model_sources`, optional, because the license model is optional.
- **Rationale**: each relationship can be queried and filled from object files, and Infrahub
  enforces the "at least one" rule (tested: creating a product without `description_sources`
  failed with "description_sources is mandatory for SpikeProduct").
- **Alternatives considered**:
  - The attribute `source` property. Rejected because it holds one value, it is meant for data
    lineage (accounts and repositories), and it is not known whether object files can set it.
  - A separate "fact" node for each product fact. Rejected because it turns each product
    attribute into a node and makes products harder to record and read.
- **Known gap**: the schema cannot require `license_model_sources` only when `license_model` is
  set. This rule needs a check, which is a separate feature.

## R4. Required sources on a coverage claim (FR-005, FR-006)

- **Decision**: `CatalogCoverageClaim.sources` is a required relationship with `min_count: 1`.
- **Rationale**: tested. Creating a claim without sources failed with "sources is mandatory for
  SpikeCoverageClaim at sources".

## R5. One claim per product and building block (FR-007)

- **Decision**: uniqueness constraint `["product", "building_block"]` on `CatalogCoverageClaim`.
- **Rationale**: tested. A second claim for the same pair failed with "Violates uniqueness
  constraint 'product-building_block'".

## R6. Blocking the deletion of linked building blocks and sources (FR-011)

- **Decision**: make `CatalogCoverageClaim.building_block` and `CatalogCoverageClaim.sources`
  required relationships. No extra logic is needed.
- **Rationale**: tested. Infrahub refused both deletions with "Cannot delete … It is linked to
  mandatory relationship … on node SpikeCoverageClaim". It also refused to delete a source when
  the claim had a second source, so any source linked to a claim is protected, not only the last
  one. Sources linked to a product's required fact relationships are protected in the same way.

## R7. Identifying products and claims (FR-012)

- **Decision**:
  - Products are unique by `["publisher", "name__value"]`, with human-friendly ID
    `[publisher__name__value, name__value]`.
  - Products have a computed, read-only, unique attribute `full_name` set to
    "{{ publisher__name__value }} {{ name__value }}".
  - Claims have human-friendly ID `[product__full_name__value, building_block__name__value]`.
- **Rationale**: tested.
  - A human-friendly ID that reaches through two relationships was rejected: "publisher is not a
    valid attribute of SpikeProduct".
  - A human-friendly ID that uses the product's `name` was rejected because the name is not
    unique: "HFID of SpikeCoverageClaim refers to peer SpikeProduct with a non-unique combination
    of attributes ['name__value']".
  - With `full_name`, two publishers each recorded a product named "Tool", and the claim loaded
    with the ID `['Acme Tool', 'Executor']`.

## R8. Loading data from object files

- **Decision**: coverage claims are written inside the product entry in object files, under
  `coverage_claims`. Sources, building blocks and publishers are referenced by their
  human-friendly IDs.
- **Rationale**: tested. A product with a claim and two sources loaded with
  `infrahubctl object load`. Loading the same file again changed nothing and created no copies.
- **Limit**: object files match existing nodes by human-friendly ID. Changing a name in a file
  therefore creates a new node and leaves the old one in place. A rename of a building block,
  publisher or product is made in the Infrahub web interface first, then copied into the file.

## R9. Other schema settings

- **Namespace**: `Catalog`.
- **Date the source was last checked**: attribute kind `DateTime`. The skill's attribute reference
  lists no date-only kind.
- **Profiles**: `generate_profile: false` on every node, because no workflow uses profiles (skill
  rule against unused generated profiles).
- **Menu**: the default menu that Infrahub builds from the schema. A custom menu is a separate
  feature.
- **Delete behavior**: deleting a product deletes its claims (`on_delete: cascade` on the
  component relationship). All other relationships keep the default `no-action`.

## R10. First products

Proposed on 2026-10-20 and approved by the user the same day (task T012). Every source was opened
on 2026-10-20. docs.ansible.com refuses scripted requests, so the Ansible documentation pages were
read from their source files in the `ansible/ansible-documentation` repository on GitHub.

- **Infrahub**, published by OpsMill.
  - Publisher and description: [What is Infrahub](https://docs.infrahub.app/overview): "Infrahub
    is built by OpsMill." and "Infrahub is a graph-based data management platform with built-in
    version control, CI workflows, peer review, and API access."
  - License model, open core: [opsmill/infrahub README](https://github.com/opsmill/infrahub): "The
    Infrahub Community edition is open source and free" and "Infrahub Enterprise … is available".
  - Intent, full: the same README: "one source of truth across devices, services, IPs, VLANs,
    circuits, and the business context tied to them."
- **Ansible**, published by Red Hat.
  - Publisher and license model, open source:
    [ansible/ansible README](https://github.com/ansible/ansible): "Ansible is sponsored by Red Hat,
    Inc." and "GNU General Public License v3.0 or later".
  - Description:
    [Network Getting Started](https://docs.ansible.com/ansible/latest/network/getting_started/index.html):
    "manage your entire network with a single automation tool".
  - Executor, full:
    [Network Resource Modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html):
    the merged, replaced, overridden and deleted states change the configuration on the device.
  - Collector, partial:
    [Run Your First Command and Playbook](https://docs.ansible.com/ansible/latest/network/getting_started/first_playbook.html),
    section "Gathering facts from network devices". Ansible gathers facts when a playbook runs and
    does not poll devices on its own.
- **SuzieQ**, published by Stardust Systems.
  - Publisher and license model, open core:
    [netenglabs/suzieq README](https://github.com/netenglabs/suzieq): "the company behind SuzieQ,
    Stardust Systems", "An enterprise version of SuzieQ is also available", Apache 2.0 license.
  - Description, Collector full and Observability full:
    [SuzieQ documentation](https://suzieq.readthedocs.io/en/latest/): "the first open source,
    multi-vendor network observability platform application", "Gathers data using an agentless
    model using either SSH or REST API as the transport", "Stores all data in files using the
    popular big data format, Parquet", with analysis through a CLI, GUI, REST API or Python.

The extents (full or partial) are the proposer's reading of these sources. None of the sources
uses the framework's building block names.
