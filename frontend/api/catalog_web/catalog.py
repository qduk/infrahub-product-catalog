"""Read the catalog from main and reshape it for the web app."""

import os
import time
from typing import Any

from infrahub_sdk import InfrahubClient

SOURCE = "edges { node { title { value } url { value } } }"

CATALOG_QUERY = f"""
query {{
  CatalogBuildingBlock {{ edges {{ node {{ name {{ value }} description {{ value }} definition_url {{ value }} }} }} }}
  CatalogPublisher {{ edges {{ node {{ name {{ value }} homepage_url {{ value }} }} }} }}
  CatalogProduct {{
    edges {{
      node {{
        id
        name {{ value }}
        full_name {{ value }}
        description {{ value }}
        homepage_url {{ value }}
        license_model {{ value }}
        status {{ value }}
        status_date {{ value }}
        publisher {{ node {{ name {{ value }} }} }}
        publisher_sources {{ {SOURCE} }}
        description_sources {{ {SOURCE} }}
        license_model_sources {{ {SOURCE} }}
        status_sources {{ {SOURCE} }}
        coverage_claims {{
          edges {{
            node {{
              extent {{ value }}
              note {{ value }}
              building_block {{ node {{ name {{ value }} }} }}
              sources {{ {SOURCE} }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""


def _sources(relationship: dict) -> list[dict[str, str]]:
    return [
        {"title": edge["node"]["title"]["value"], "url": edge["node"]["url"]["value"]}
        for edge in relationship["edges"]
    ]


def reshape(data: dict) -> dict[str, Any]:
    blocks = [
        {
            "name": edge["node"]["name"]["value"],
            "description": edge["node"]["description"]["value"],
            "definition_url": edge["node"]["definition_url"]["value"],
        }
        for edge in data["CatalogBuildingBlock"]["edges"]
    ]
    publishers = sorted(
        (
            {"name": edge["node"]["name"]["value"], "homepage_url": edge["node"]["homepage_url"]["value"]}
            for edge in data["CatalogPublisher"]["edges"]
        ),
        key=lambda publisher: publisher["name"].casefold(),
    )
    products = []
    for edge in data["CatalogProduct"]["edges"]:
        node = edge["node"]
        products.append(
            {
                "id": node["id"],
                "name": node["name"]["value"],
                "full_name": node["full_name"]["value"],
                "publisher": node["publisher"]["node"]["name"]["value"],
                "description": node["description"]["value"],
                "homepage_url": node["homepage_url"]["value"],
                "license_model": node["license_model"]["value"],
                "status": node["status"]["value"],
                "status_date": node["status_date"]["value"],
                "sources": {
                    "publisher": _sources(node["publisher_sources"]),
                    "description": _sources(node["description_sources"]),
                    "license_model": _sources(node["license_model_sources"]),
                    "status": _sources(node["status_sources"]),
                },
                "claims": [
                    {
                        "block": claim["node"]["building_block"]["node"]["name"]["value"],
                        "extent": claim["node"]["extent"]["value"],
                        "note": claim["node"]["note"]["value"],
                        "sources": _sources(claim["node"]["sources"]),
                    }
                    for claim in node["coverage_claims"]["edges"]
                ],
            }
        )
    products.sort(key=lambda product: product["full_name"].casefold())
    return {"blocks": blocks, "publishers": publishers, "products": products}


class CatalogCache:
    """Keeps the catalog for a short time, so page loads do not each query Infrahub."""

    def __init__(self, seconds: float | None = None) -> None:
        self.seconds = seconds if seconds is not None else float(os.environ.get("CATALOG_CACHE_SECONDS", "60"))
        self._value: dict[str, Any] | None = None
        self._loaded_at = 0.0

    async def get(self, client: InfrahubClient) -> dict[str, Any]:
        if self._value is None or time.monotonic() - self._loaded_at > self.seconds:
            data = await client.execute_graphql(CATALOG_QUERY, branch_name="main")
            self._value = reshape(data)
            self._loaded_at = time.monotonic()
        return self._value

    def clear(self) -> None:
        self._value = None
