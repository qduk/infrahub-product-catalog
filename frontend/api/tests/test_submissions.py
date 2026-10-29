import json
import asyncio
import copy
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from catalog_web.submissions import Submission, SubmissionError, submit

VALID = {
    "product": {
        "name": "Example Tool",
        "description": "Collects interface counters from network devices.",
        "homepage_url": "https://example.org/tool",
        "license_model": "open_source",
        "status": "active",
    },
    "publisher": {"new": {"name": "Example Corp", "homepage_url": "https://example.org/"}},
    "sources": [
        {"key": "s1", "title": "Example docs", "url": "https://example.org/docs"},
        {"key": "s2", "title": "Example license", "url": "https://example.org/license"},
    ],
    "fact_sources": {"publisher": ["s1"], "description": ["s1"], "license_model": ["s2"], "status": []},
    "claims": [{"block": "Collector", "note": None, "sources": ["s1"]}],
}


def submission(**changes) -> dict:
    data = copy.deepcopy(VALID)
    for path, value in changes.items():
        target = data
        *parents, last = path.split("__")
        for part in parents:
            target = target[int(part)] if part.isdigit() else target[part]
        target[int(last) if last.isdigit() else last] = value
    return data


def errors(data: dict) -> str:
    with pytest.raises(ValidationError) as caught:
        Submission.model_validate(data)
    return str(caught.value)


# Validation rules (data-model.md)


def test_valid_submission_passes() -> None:
    Submission.model_validate(VALID)


def test_license_model_needs_a_source() -> None:
    assert "license model needs a license model source" in errors(submission(fact_sources__license_model=[]))


def test_license_model_can_be_left_out() -> None:
    Submission.model_validate(submission(product__license_model=None, fact_sources__license_model=[]))


def test_status_other_than_active_needs_a_source() -> None:
    assert "status of discontinued needs a status source" in errors(submission(product__status="discontinued"))


def test_status_with_source_passes() -> None:
    Submission.model_validate(submission(product__status="acquired", fact_sources__status=["s1"]))


def test_one_claim_per_building_block() -> None:
    claims = [VALID["claims"][0], {"block": "Collector", "sources": ["s1"]}]
    assert "only one claim per building block" in errors(submission(claims=claims))


def test_unknown_source_key_is_rejected() -> None:
    assert "unknown source keys: nope" in errors(submission(fact_sources__description=["nope"]))


def test_publisher_and_description_need_sources() -> None:
    message = errors(submission(fact_sources__publisher=[], fact_sources__description=[]))
    assert "fact_sources.publisher" in message
    assert "fact_sources.description" in message


@pytest.mark.parametrize("url", ["javascript:alert(1)", "ftp://example.org/x", "not a url"])
def test_only_http_links_are_accepted(url: str) -> None:
    assert "url" in errors(submission(sources__0__url=url)).lower()


def test_over_long_fields_are_rejected() -> None:
    message = errors(submission(product__name="x" * 101, product__description="x" * 1001))
    assert "product.name" in message
    assert "product.description" in message


def test_duplicate_source_links_are_rejected() -> None:
    assert "only once" in errors(submission(sources__1__url="https://example.org/docs"))


def test_publisher_needs_exactly_one_choice() -> None:
    assert "existing publisher or enter a new one" in errors(
        submission(publisher={"existing": "Example Corp", "new": VALID["publisher"]["new"]})
    )


def test_needs_at_least_one_claim() -> None:
    assert "claims" in errors(submission(claims=[]))


# Submission steps, with a fake Infrahub client


class FakeNode:
    def __init__(self, store: "FakeClient", kind: str, branch: str, **data) -> None:
        self.store, self.kind, self.branch, self.data = store, kind, branch, data
        self.id = None
        for key, value in data.items():
            setattr(self, key, SimpleNamespace(value=value))

    async def save(self) -> None:
        if self.kind in self.store.fail_on:
            raise RuntimeError(f"cannot save {self.kind}")
        self.id = f"{self.kind}-{len(self.store.saved)}"
        self.store.saved.append(self)


class FakeBranches:
    def __init__(self, store: "FakeClient") -> None:
        self.store = store

    async def create(self, branch_name: str, **_) -> None:
        self.store.branches.append(branch_name)

    async def delete(self, branch_name: str) -> None:
        self.store.branches.remove(branch_name)
        self.store.deleted.append(branch_name)


class FakeClient:
    def __init__(self, existing: dict[str, list[dict]] | None = None, fail_on: set[str] | None = None) -> None:
        self.saved: list[FakeNode] = []
        self.branches: list[str] = []
        self.deleted: list[str] = []
        self.fail_on = fail_on or set()
        self.branch = FakeBranches(self)
        self.existing = {
            kind: [FakeNode(self, kind, "main", **item) for item in items] for kind, items in (existing or {}).items()
        }
        for kind, nodes in self.existing.items():
            for index, node in enumerate(nodes):
                node.id = f"existing-{kind}-{index}"

    def _match(self, kind: str, **filters) -> list[FakeNode]:
        found = []
        for node in self.existing.get(kind, []) + [n for n in self.saved if n.kind == kind]:
            ok = True
            for key, wanted in filters.items():
                if key == "branch":
                    continue
                field = key.removesuffix("__value")
                if key == "publisher__ids":
                    ok &= getattr(node, "publisher", SimpleNamespace(value=None)).value in wanted
                else:
                    ok &= getattr(node, field, SimpleNamespace(value=None)).value == wanted
            if ok:
                found.append(node)
        return found

    async def all(self, kind: str, **_) -> list[FakeNode]:
        return self._match(kind)

    async def filters(self, kind: str, **filters) -> list[FakeNode]:
        return self._match(kind, **filters)

    async def get(self, kind: str, **filters) -> FakeNode:
        return self._match(kind, **filters)[0]

    async def create(self, kind: str, branch: str = "main", **data) -> FakeNode:
        return FakeNode(self, kind, branch, **data)


BLOCKS = {"CatalogBuildingBlock": [{"name": "Collector"}, {"name": "Executor"}]}


def run(client: FakeClient, data: dict) -> str:
    return asyncio.run(submit(client, Submission.model_validate(data), branch_name="submission-test"))


def test_submission_creates_branch_sources_publisher_product_claims_and_proposed_change() -> None:
    client = FakeClient(existing=BLOCKS)
    assert run(client, VALID) == "submission-test"
    kinds = [node.kind for node in client.saved]
    assert kinds == [
        "CatalogSource",
        "CatalogSource",
        "CatalogPublisher",
        "CatalogProduct",
        "CatalogCoverageClaim",
        "CoreProposedChange",
    ]
    assert all(node.branch == "submission-test" for node in client.saved if node.kind != "CoreProposedChange")
    proposed_change = client.saved[-1]
    assert proposed_change.data["name"] == "Submission: Example Corp Example Tool"
    assert proposed_change.data["source_branch"] == "submission-test"


def test_existing_sources_and_publisher_are_reused() -> None:
    existing = dict(BLOCKS)
    existing["CatalogSource"] = [{"url": "https://example.org/docs", "title": "Docs"}]
    existing["CatalogPublisher"] = [{"name": "Example Corp"}]
    client = FakeClient(existing=existing)
    run(client, submission(publisher={"existing": "Example Corp"}))
    kinds = [node.kind for node in client.saved]
    assert kinds.count("CatalogSource") == 1
    assert "CatalogPublisher" not in kinds


def test_existing_product_for_publisher_is_refused() -> None:
    existing = dict(BLOCKS)
    existing["CatalogPublisher"] = [{"name": "Example Corp"}]
    client = FakeClient(existing=existing)
    client.existing["CatalogProduct"] = [
        FakeNode(client, "CatalogProduct", "main", name="Example Tool", publisher="existing-CatalogPublisher-0")
    ]
    with pytest.raises(SubmissionError) as caught:
        run(client, submission(publisher={"existing": "Example Corp"}))
    assert caught.value.status_code == 409
    assert client.branches == []


def test_new_publisher_that_already_exists_is_refused() -> None:
    existing = dict(BLOCKS)
    existing["CatalogPublisher"] = [{"name": "Example Corp"}]
    with pytest.raises(SubmissionError) as caught:
        run(FakeClient(existing=existing), VALID)
    assert caught.value.status_code == 409


def test_unknown_building_block_is_refused() -> None:
    with pytest.raises(SubmissionError) as caught:
        run(FakeClient(existing=BLOCKS), submission(claims__0__block="Infrastructure"))
    assert caught.value.status_code == 422


def test_failure_after_branch_creation_deletes_the_branch() -> None:
    client = FakeClient(existing=BLOCKS, fail_on={"CoreProposedChange"})
    with pytest.raises(RuntimeError):
        run(client, VALID)
    assert client.deleted == ["submission-test"]
    assert client.branches == []


def test_extent_from_an_older_form_is_ignored() -> None:
    data = json.loads(json.dumps(VALID))
    data["claims"][0]["extent"] = "full"
    claim = Submission.model_validate(data).claims[0]
    assert not hasattr(claim, "extent")
