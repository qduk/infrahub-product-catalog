"""Submits one product to the local Infrahub instance through the running service.

Run on demand: uv run pytest -m integration -p no:pytest-infrahub
Needs the service on port 8200 (with the catalog-web token) and an admin token in
INFRAHUB_ADMIN_TOKEN to inspect and clean up the result.
"""

import asyncio
import os

import httpx
import pytest
from infrahub_sdk import Config, InfrahubClient

from tests.test_submissions import submission


@pytest.mark.integration
def test_submission_reaches_infrahub_as_a_proposed_change_and_not_main() -> None:
    body = submission(
        product__name="Integration Test Tool",
        publisher={"existing": "OpsMill"},
        sources__0__url="https://example.org/integration-docs",
        sources__1__url="https://docs.infrahub.app/overview",
    )
    response = httpx.post("http://localhost:8200/api/submissions", json=body, timeout=120)
    assert response.status_code == 201, response.text
    branch = response.json()["reference"]

    async def inspect_and_clean_up() -> None:
        admin = InfrahubClient(
            config=Config(address="http://localhost:8100", api_token=os.environ["INFRAHUB_ADMIN_TOKEN"])
        )
        try:
            products = await admin.filters("CatalogProduct", name__value="Integration Test Tool", branch=branch,
                                           prefetch_relationships=True)
            assert len(products) == 1
            claims = await admin.filters("CatalogCoverageClaim", product__ids=[products[0].id], branch=branch)
            assert len(claims) == 1
            reused = await admin.filters("CatalogSource", url__value="https://docs.infrahub.app/overview", branch=branch)
            assert len(reused) == 1
            assert not await admin.filters("CatalogProduct", name__value="Integration Test Tool", branch="main")
            changes = await admin.filters("CoreProposedChange", source_branch__value=branch)
            assert len(changes) == 1
            assert changes[0].name.value == "Submission: OpsMill Integration Test Tool"
        finally:
            for change in await admin.filters("CoreProposedChange", source_branch__value=branch):
                change.state.value = "closed"
                await change.save()
            await admin.branch.delete(branch)

    asyncio.run(inspect_and_clean_up())
