"""Infrahub client for the service, configured from the environment."""

import os
from functools import lru_cache

from infrahub_sdk import Config, InfrahubClient


@lru_cache
def get_client() -> InfrahubClient:
    return InfrahubClient(
        config=Config(
            address=os.environ.get("INFRAHUB_ADDRESS", "http://localhost:8100"),
            api_token=os.environ["INFRAHUB_API_TOKEN"],
            timeout=30,
        )
    )
