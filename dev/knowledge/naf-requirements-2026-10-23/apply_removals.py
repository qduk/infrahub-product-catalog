"""Delete the products, claims, publishers and sources removed on 2026-10-27 from an Infrahub branch.

Object files only add and update records, so these deletions are applied with this script on the
same branch that loads the verdicts. Run:
  uv run python dev/knowledge/naf-requirements-2026-10-23/apply_removals.py <branch>
It reads INFRAHUB_ADDRESS (or infrahubctl.toml's address) and INFRAHUB_API_TOKEN, and skips records
that are already gone.
"""

import asyncio
import json
import sys
from pathlib import Path

from infrahub_sdk import InfrahubClient
from infrahub_sdk.exceptions import NodeNotFoundError

# Claims go before products and publishers; deleting a product deletes its claims as well.
REMOVALS = [
    ("CatalogCoverageClaim", ["Freshworks Device42", "Observability"]),
    ("CatalogCoverageClaim", ["EfficientIP SOLIDserver DDI", "Executor"]),
    ("CatalogCoverageClaim", ["System Initiative System Initiative", "Executor"]),
    ("CatalogCoverageClaim", ["Forward Networks Forward Enterprise", "Intent"]),
    ("CatalogCoverageClaim", ["NetBrain Technologies Agentic NetOps Platform", "Intent"]),
    ("CatalogProduct", ["Network Unit Testing System", "NUTS"]),
    ("CatalogProduct", ["Spacelift", "Spacelift"]),
    ("CatalogProduct", ["Infoblox", "NIOS"]),
    ("CatalogProduct", ["phpIPAM project", "phpIPAM"]),
    ("CatalogPublisher", ["Network Unit Testing System"]),
    ("CatalogPublisher", ["Spacelift"]),
    ("CatalogPublisher", ["Infoblox"]),
    ("CatalogPublisher", ["phpIPAM project"]),
]

# Sources that only the removed records used, as recorded by merge.py.
REMOVED_SOURCES = json.loads((Path(__file__).parent / "removed-sources.json").read_text())


async def main(branch: str) -> None:
    client = InfrahubClient()
    for kind, hfid in [*REMOVALS, *(("CatalogSource", [url]) for url in REMOVED_SOURCES)]:
        try:
            node = await client.get(kind=kind, hfid=hfid, branch=branch)
        except NodeNotFoundError:
            print(f"already gone: {kind} {hfid}")
            continue
        await node.delete()
        print(f"deleted: {kind} {hfid}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
