import asyncio

from catalog_web.catalog import CatalogCache, reshape


def source(title: str, url: str) -> dict:
    return {"node": {"title": {"value": title}, "url": {"value": url}}}


RAW = {
    "CatalogBuildingBlock": {"edges": [
        {"node": {"name": {"value": "Intent"}, "description": {"value": "Desired state."},
                  "definition_url": {"value": "https://example.org/#intent"}}},
    ]},
    "CatalogPublisher": {"edges": [
        {"node": {"name": {"value": "zeta"}, "homepage_url": {"value": "https://z.example"}}},
        {"node": {"name": {"value": "Alpha"}, "homepage_url": {"value": "https://a.example"}}},
    ]},
    "CatalogProduct": {"edges": [{"node": {
        "id": "p1", "name": {"value": "Tool"}, "full_name": {"value": "Alpha Tool"},
        "description": {"value": "Does things."}, "homepage_url": {"value": "https://a.example/tool"},
        "license_model": {"value": None}, "status": {"value": "discontinued"},
        "status_date": {"value": "2025-02-24T00:00:00Z"},
        "publisher": {"node": {"name": {"value": "Alpha"}}},
        "publisher_sources": {"edges": [source("About", "https://a.example/about")]},
        "description_sources": {"edges": [source("Docs", "https://a.example/docs")]},
        "license_model_sources": {"edges": []},
        "status_sources": {"edges": [source("News", "https://a.example/news")]},
        "coverage_claims": {"edges": [{"node": {
            "extent": {"value": "partial"}, "note": {"value": None},
            "building_block": {"node": {"name": {"value": "Intent"}}},
            "sources": {"edges": [source("Docs", "https://a.example/docs")]},
        }}]},
    }}]},
}


def test_reshape_gives_the_documented_response() -> None:
    data = reshape(RAW)
    assert [publisher["name"] for publisher in data["publishers"]] == ["Alpha", "zeta"]
    product = data["products"][0]
    assert product["publisher"] == "Alpha"
    assert product["status"] == "discontinued"
    assert product["sources"]["status"] == [{"title": "News", "url": "https://a.example/news"}]
    assert product["claims"] == [{"block": "Intent", "extent": "partial", "note": None,
                                  "sources": [{"title": "Docs", "url": "https://a.example/docs"}]}]


class CountingClient:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_graphql(self, query: str, branch_name: str) -> dict:
        assert branch_name == "main"
        self.calls += 1
        return RAW


def test_cache_reuses_the_result_until_it_expires() -> None:
    client = CountingClient()
    cache = CatalogCache(seconds=60)
    asyncio.run(cache.get(client))
    asyncio.run(cache.get(client))
    assert client.calls == 1
    cache.clear()
    asyncio.run(cache.get(client))
    assert client.calls == 2
