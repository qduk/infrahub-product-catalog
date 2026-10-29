import asyncio
import json

from catalog_web.catalog import CatalogCache, claim_extent, reshape


def source(title: str, url: str) -> dict:
    return {"node": {"title": {"value": title}, "url": {"value": url}}}


def requirement(identifier: str, level: str, position: int, block: str | None) -> dict:
    return {"node": {
        "identifier": {"value": identifier}, "level": {"value": level}, "position": {"value": position},
        "summary": {"value": f"Summary of {identifier}"}, "statement": {"value": f"It {level.upper()} ..."},
        "reference_url": {"value": "https://reference.networkautomation.forum/Framework/Framework/"},
        "building_block": {"node": {"name": {"value": block}} if block else None},
    }}


RAW = {
    "CatalogRequirement": {"edges": [
        requirement("intent-must-1", "must", 3, "Intent"),
        requirement("framework-should-1", "should", 1, None),
        requirement("intent-may-1", "may", 4, "Intent"),
    ]},
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
            "note": {"value": None},
            "building_block": {"node": {"name": {"value": "Intent"}}},
            "sources": {"edges": [source("Docs", "https://a.example/docs")]},
            "verdicts": {"edges": [
                {"node": {"verdict": {"value": "met"}, "note": {"value": "CRUD API."},
                          "requirement": {"node": {"identifier": {"value": "intent-must-1"}}},
                          "sources": {"edges": [source("Docs", "https://a.example/docs")]}}},
                {"node": {"verdict": {"value": "not_shown"}, "note": {"value": None},
                          "requirement": {"node": {"identifier": {"value": "framework-should-1"}}},
                          "sources": {"edges": []}}},
            ]},
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
    claim = product["claims"][0]
    assert claim["block"] == "Intent"
    assert claim["assessed"] is True
    # framework-should-1 is not shown, but framework-wide requirements do not count toward full.
    assert claim["extent"] == "full"
    assert claim["sources"] == [{"title": "Docs", "url": "https://a.example/docs"}]
    assert claim["verdicts"][0] == {"requirement": "intent-must-1", "verdict": "met", "note": "CRUD API.",
                                    "sources": [{"title": "Docs", "url": "https://a.example/docs"}]}
    assert [r["identifier"] for r in data["requirements"]] == ["framework-should-1", "intent-must-1", "intent-may-1"]
    assert data["requirements"][0]["block"] is None


def test_extent_is_full_only_when_every_must_and_should_is_met() -> None:
    requirements = [
        {"identifier": "intent-must-1", "level": "must", "block": "Intent"},
        {"identifier": "intent-should-1", "level": "should", "block": "Intent"},
        {"identifier": "intent-may-1", "level": "may", "block": "Intent"},
        {"identifier": "framework-should-1", "level": "should", "block": None},
        {"identifier": "executor-must-1", "level": "must", "block": "Executor"},
    ]
    all_met = {"intent-must-1": "met", "intent-should-1": "met", "framework-should-1": "met"}
    assert claim_extent("Intent", all_met, requirements) == "full"
    assert claim_extent("Intent", {**all_met, "intent-may-1": "not_met"}, requirements) == "full"
    assert claim_extent("Intent", {**all_met, "intent-should-1": "partly_met"}, requirements) == "partial"
    assert claim_extent("Intent", {**all_met, "framework-should-1": "not_met"}, requirements) == "full"
    assert claim_extent("Intent", {"intent-must-1": "met"}, requirements) == "partial"
    assert claim_extent("Intent", {}, requirements) == "partial"


def test_claim_without_verdicts_is_not_assessed() -> None:
    raw = json.loads(json.dumps(RAW))
    raw["CatalogProduct"]["edges"][0]["node"]["coverage_claims"]["edges"][0]["node"]["verdicts"]["edges"] = []
    claim = reshape(raw)["products"][0]["claims"][0]
    assert claim["assessed"] is False
    assert claim["extent"] == "partial"


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
