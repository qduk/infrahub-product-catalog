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
  CatalogRequirement {{
    edges {{
      node {{
        identifier {{ value }}
        level {{ value }}
        position {{ value }}
        summary {{ value }}
        statement {{ value }}
        reference_url {{ value }}
        building_block {{ node {{ name {{ value }} }} }}
      }}
    }}
  }}
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
              note {{ value }}
              building_block {{ node {{ name {{ value }} }} }}
              sources {{ {SOURCE} }}
              verdicts {{
                edges {{
                  node {{
                    verdict {{ value }}
                    note {{ value }}
                    requirement {{ node {{ identifier {{ value }} }} }}
                    sources {{ {SOURCE} }}
                  }}
                }}
              }}
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


# A claim is full only when every requirement of these levels that applies to its block is met.
REQUIRED_LEVELS = {"must", "should"}


def claim_extent(block: str, verdicts: dict[str, str], requirements: list[dict[str, Any]]) -> str:
    """Return "full" when every MUST and SHOULD requirement of the block itself is met.

    The same rule as in transforms/catalog_report.py. Framework-wide requirements are shown but do
    not count. A claim with no verdicts is not assessed yet and counts as partial; a missing or
    other verdict counts as not met.
    """
    if not verdicts:
        return "partial"
    applying = [r for r in requirements if r["block"] == block and r["level"] in REQUIRED_LEVELS]
    return "full" if all(verdicts.get(r["identifier"]) == "met" for r in applying) else "partial"


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
    requirements = sorted(
        (
            {
                "identifier": edge["node"]["identifier"]["value"],
                "level": edge["node"]["level"]["value"],
                "position": edge["node"]["position"]["value"],
                "summary": edge["node"]["summary"]["value"],
                "statement": edge["node"]["statement"]["value"],
                "reference_url": edge["node"]["reference_url"]["value"],
                "block": (edge["node"]["building_block"]["node"] or {}).get("name", {}).get("value"),
            }
            for edge in data["CatalogRequirement"]["edges"]
        ),
        key=lambda requirement: requirement["position"],
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
                "claims": [_claim(claim["node"], requirements) for claim in node["coverage_claims"]["edges"]],
            }
        )
    products.sort(key=lambda product: product["full_name"].casefold())
    return {"blocks": blocks, "publishers": publishers, "requirements": requirements, "products": products}


def _claim(node: dict, requirements: list[dict[str, Any]]) -> dict[str, Any]:
    block = node["building_block"]["node"]["name"]["value"]
    verdicts = [
        {
            "requirement": verdict["node"]["requirement"]["node"]["identifier"]["value"],
            "verdict": verdict["node"]["verdict"]["value"],
            "note": verdict["node"]["note"]["value"],
            "sources": _sources(verdict["node"]["sources"]),
        }
        for verdict in node["verdicts"]["edges"]
    ]
    return {
        "block": block,
        "extent": claim_extent(block, {v["requirement"]: v["verdict"] for v in verdicts}, requirements),
        "assessed": bool(verdicts),
        "note": node["note"]["value"],
        "sources": _sources(node["sources"]),
        "verdicts": verdicts,
    }


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
