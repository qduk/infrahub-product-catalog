"""Tests for the four catalog record checks, with data in the shape of the catalog_records query."""

import asyncio
import copy

import pytest

from checks.catalog_record_checks import (
    CatalogCoverageCheck,
    CatalogDuplicateCheck,
    CatalogSubmissionCheck,
    CatalogUnusedSourceCheck,
    normalise_link,
    normalise_name,
)

# The SDK logs this message itself when a check passes.
SDK_PASS_MESSAGE = "Check succesfully completed"


def edges(*items: dict) -> dict:
    return {"edges": [{"node": item} for item in items]}


def ids(*values: str) -> dict:
    return edges(*({"id": value} for value in values))


def value(item: object) -> dict:
    return {"value": item}


def publisher(id_: str, name: str) -> dict:
    return {
        "id": id_,
        "__typename": "CatalogPublisher",
        "display_label": name,
        "name": value(name),
        "homepage_url": value(f"https://example.org/{id_}"),
    }


def product(id_: str, name: str, publisher_id: str, publisher_name: str, sources=("s1",), claims: int = 1) -> dict:
    return {
        "id": id_,
        "__typename": "CatalogProduct",
        "display_label": f"{publisher_name} {name}",
        "name": value(name),
        "full_name": value(f"{publisher_name} {name}"),
        "description": value("Collects device state."),
        "homepage_url": value(f"https://example.org/{id_}"),
        "license_model": value(None),
        "status": value("active"),
        "status_date": value(None),
        "publisher": {"node": {"id": publisher_id}},
        "publisher_sources": ids(*sources),
        "description_sources": ids(*sources),
        "license_model_sources": ids(),
        "status_sources": ids(),
        "coverage_claims": {"count": claims},
    }


def source(id_: str, title: str, url: str, uses: int = 1) -> dict:
    return {
        "id": id_,
        "__typename": "CatalogSource",
        "display_label": title,
        "title": value(title),
        "url": value(url),
        "last_checked": value("2026-10-01T00:00:00Z"),
        "publisher_of_products": {"count": uses},
        "description_of_products": {"count": 0},
        "license_model_of_products": {"count": 0},
        "status_of_products": {"count": 0},
        "coverage_claims": {"count": 0},
    }


def claim(id_: str, product_id: str, block_id: str, label: str, sources=("s1",)) -> dict:
    return {
        "id": id_,
        "__typename": "CatalogCoverageClaim",
        "display_label": label,
        "extent": value("full"),
        "note": value(None),
        "product": {"node": {"id": product_id}},
        "building_block": {"node": {"id": block_id}},
        "sources": ids(*sources),
    }


def block(id_: str, name: str) -> dict:
    return {
        "id": id_,
        "__typename": "CatalogBuildingBlock",
        "display_label": name,
        "name": value(name),
        "description": value(f"{name} block"),
        "definition_url": value(f"https://example.org/{name.lower()}"),
    }


def catalog(publishers=(), products=(), sources=(), claims=(), blocks=()) -> dict:
    return {
        "CatalogPublisher": edges(*publishers),
        "CatalogProduct": edges(*products),
        "CatalogSource": edges(*sources),
        "CatalogCoverageClaim": edges(*claims),
        "CatalogBuildingBlock": edges(*blocks),
    }


def main_catalog() -> dict:
    return catalog(
        publishers=[publisher("pub1", "OpsMill")],
        products=[product("prod1", "Infrahub", "pub1", "OpsMill")],
        sources=[source("s1", "Infrahub documentation", "https://docs.infrahub.app/")],
        claims=[claim("c1", "prod1", "b1", "OpsMill Infrahub - Intent")],
        blocks=[block("b1", "Intent"), block("b2", "Collector")],
    )


def run(check_class, data: dict, branch: str = "test-branch"):
    check = check_class(branch=branch)
    asyncio.run(check.run(data=data))
    return check


def messages(check, level: str) -> list[str]:
    return [log["message"] for log in check.logs if log["level"] == level and log["message"] != SDK_PASS_MESSAGE]


def nodes_of(data: dict, kind: str) -> list[dict]:
    return [edge["node"] for edge in data[kind]["edges"]]


def add(data: dict, kind: str, node: dict) -> None:
    data[kind]["edges"].append({"node": node})


# Normalisation


@pytest.mark.parametrize(
    ("first", "second"),
    [("NetBox Labs", "Netbox labs"), ("Slurp'it", "Slurpit"), ("Ansible-Lint", "ansible lint")],
)
def test_names_that_differ_by_case_spaces_or_punctuation_match(first: str, second: str) -> None:
    assert normalise_name(first) == normalise_name(second)


def test_names_with_other_characters_differ() -> None:
    assert normalise_name("Batfish") != normalise_name("Batfish 2")


def test_name_without_letters_or_digits_is_kept_as_written() -> None:
    assert normalise_name("---") == "---"
    assert normalise_name("---") != normalise_name("...")


@pytest.mark.parametrize(
    "other", ["http://docs.infrahub.app", "HTTPS://Docs.Infrahub.app/", "https://docs.infrahub.app//"]
)
def test_links_that_differ_by_case_scheme_or_trailing_slash_match(other: str) -> None:
    assert normalise_link("https://docs.infrahub.app/") == normalise_link(other)


@pytest.mark.parametrize("other", ["https://www.docs.infrahub.app/", "https://docs.infrahub.app/?a=1"])
def test_links_with_other_differences_do_not_match(other: str) -> None:
    assert normalise_link("https://docs.infrahub.app/") != normalise_link(other)


# User Story 1: submission branches only add records


def submission_branch() -> dict:
    """main plus a new product with a new publisher, a new source and claims on existing blocks."""
    branch = main_catalog()
    add(branch, "CatalogPublisher", publisher("pub2", "Example Corp"))
    add(branch, "CatalogSource", source("s2", "Example docs", "https://example.org/docs"))
    add(branch, "CatalogProduct", product("prod2", "Collector", "pub2", "Example Corp", sources=("s2", "s1")))
    add(branch, "CatalogCoverageClaim", claim("c2", "prod2", "b2", "Example Corp Collector - Collector", ("s2",)))
    add(branch, "CatalogCoverageClaim", claim("c3", "prod2", "b1", "Example Corp Collector - Intent", ("s1",)))
    return branch


class SubmissionCheckWithMain(CatalogSubmissionCheck):
    """The submission check with main's data from main_catalog() instead of from Infrahub."""

    async def main_data(self) -> dict:
        return main_catalog()


def run_submission(branch: dict, branch_name: str = "submission-20261022-abc123"):
    return run(SubmissionCheckWithMain, branch, branch_name)


def test_submission_that_only_adds_records_passes() -> None:
    check = run_submission(submission_branch())
    assert check.passed is True
    assert messages(check, "ERROR") == []


def test_new_records_may_link_to_existing_records() -> None:
    branch = submission_branch()
    existing_source = nodes_of(branch, "CatalogSource")[0]
    existing_source["publisher_of_products"]["count"] = 2
    product_on_branch = nodes_of(branch, "CatalogProduct")[1]
    product_on_branch["publisher"] = {"node": {"id": "pub1"}}
    check = run_submission(branch)
    assert messages(check, "ERROR") == []


def test_changed_fact_of_existing_product_fails() -> None:
    branch = submission_branch()
    nodes_of(branch, "CatalogProduct")[0]["description"] = value("Changed.")
    check = run_submission(branch)
    assert check.passed is False
    assert messages(check, "ERROR") == [
        "Product OpsMill Infrahub: description differs from main. A submission may only add records; change "
        "it back, and make the edit on a separate branch."
    ]


@pytest.mark.parametrize(
    ("kind", "index", "field", "new", "expected"),
    [
        ("CatalogProduct", 0, "description_sources", ids("s1", "s2"), "Product OpsMill Infrahub: description sources"),
        ("CatalogProduct", 0, "publisher", {"node": {"id": "pub2"}}, "Product OpsMill Infrahub: publisher"),
        ("CatalogSource", 0, "last_checked", value("2026-10-22T00:00:00Z"), "Source Infrahub documentation: last-checked date"),
        ("CatalogSource", 0, "url", value("https://evil.example/"), "Source Infrahub documentation: link"),
        ("CatalogCoverageClaim", 0, "extent", value("partial"), "Coverage claim OpsMill Infrahub - Intent: extent"),
        ("CatalogPublisher", 0, "homepage_url", value("https://x.example/"), "Publisher OpsMill: home page"),
        ("CatalogBuildingBlock", 0, "name", value("Intent!"), "Building block Intent: name"),
    ],
)
def test_changed_facts_fail(kind: str, index: int, field: str, new: dict, expected: str) -> None:
    branch = submission_branch()
    nodes_of(branch, kind)[index][field] = new
    errors = messages(run_submission(branch), "ERROR")
    assert len(errors) == 1
    assert errors[0].startswith(f"{expected} differs from main.")


def test_deleted_record_fails() -> None:
    branch = submission_branch()
    branch["CatalogCoverageClaim"]["edges"].pop(0)
    assert messages(run_submission(branch), "ERROR") == [
        "Coverage claim OpsMill Infrahub - Intent is on main but was deleted on this branch. A submission may "
        "only add records; restore it."
    ]


def test_added_building_block_fails() -> None:
    branch = submission_branch()
    add(branch, "CatalogBuildingBlock", block("b3", "Spam"))
    assert messages(run_submission(branch), "ERROR") == [
        "Building block Spam was added. Building blocks come from the framework and are not added by "
        "submissions; delete it."
    ]


def test_new_record_may_be_corrected_on_the_submission_branch() -> None:
    branch = submission_branch()
    nodes_of(branch, "CatalogProduct")[1]["description"] = value("Corrected typing error.")
    assert messages(run_submission(branch), "ERROR") == []


def test_other_branches_are_not_compared() -> None:
    branch = submission_branch()
    nodes_of(branch, "CatalogProduct")[0]["description"] = value("Maintainer correction.")
    check = run(CatalogSubmissionCheck, branch, "fix-infrahub-description")
    assert check.passed is True
    assert messages(check, "INFO") == [
        "This check applies only to submission branches (names that start with submission-)."
    ]


# User Story 2: near-duplicate names and links


def test_near_duplicate_publishers_fail_once_per_pair() -> None:
    data = main_catalog()
    add(data, "CatalogPublisher", publisher("pub2", "Ops-Mill"))
    add(data, "CatalogPublisher", publisher("pub3", "opsmill"))
    errors = messages(run(CatalogDuplicateCheck, data), "ERROR")
    assert errors == [
        "Publishers Ops-Mill and OpsMill have near-identical names. Keep one and move its products to it, or "
        "rename one.",
        "Publishers Ops-Mill and opsmill have near-identical names. Keep one and move its products to it, or "
        "rename one.",
        "Publishers OpsMill and opsmill have near-identical names. Keep one and move its products to it, or "
        "rename one.",
    ]


def test_near_duplicate_products_of_one_publisher_fail() -> None:
    data = main_catalog()
    add(data, "CatalogProduct", product("prod2", "infra hub", "pub1", "OpsMill"))
    assert messages(run(CatalogDuplicateCheck, data), "ERROR") == [
        "Products Infrahub and infra hub of OpsMill have near-identical names. Keep one, or rename one."
    ]


def test_same_product_name_from_different_publishers_passes() -> None:
    data = main_catalog()
    add(data, "CatalogPublisher", publisher("pub2", "Example Corp"))
    add(data, "CatalogProduct", product("prod2", "Infrahub", "pub2", "Example Corp"))
    assert messages(run(CatalogDuplicateCheck, data), "ERROR") == []


def test_near_duplicate_source_links_fail() -> None:
    data = main_catalog()
    add(data, "CatalogSource", source("s2", "Docs again", "http://Docs.Infrahub.app"))
    assert messages(run(CatalogDuplicateCheck, data), "ERROR") == [
        "Sources Docs again (http://Docs.Infrahub.app) and Infrahub documentation (https://docs.infrahub.app/) "
        "point to the same page. Keep one and link its facts to it."
    ]


def test_other_differences_pass() -> None:
    data = main_catalog()
    add(data, "CatalogPublisher", publisher("pub2", "OpsMill Labs"))
    add(data, "CatalogSource", source("s2", "Docs www", "https://www.docs.infrahub.app/"))
    assert messages(run(CatalogDuplicateCheck, data), "ERROR") == []


# User Story 3: products that cover no building block


def test_product_without_claim_is_a_warning() -> None:
    data = main_catalog()
    add(data, "CatalogProduct", product("prod2", "Lonely", "pub1", "OpsMill", claims=0))
    check = run(CatalogCoverageCheck, data)
    assert check.passed is True
    assert messages(check, "INFO") == [
        "Warning: OpsMill Lonely covers no building block, so the web app does not show it. Add a coverage "
        "claim, or confirm that the product covers none."
    ]


def test_product_with_claim_is_not_reported() -> None:
    assert messages(run(CatalogCoverageCheck, main_catalog()), "INFO") == []


# User Story 4: sources that support nothing


def test_source_that_supports_nothing_fails() -> None:
    data = main_catalog()
    add(data, "CatalogSource", source("s2", "Spam page", "https://spam.example/", uses=0))
    check = run(CatalogUnusedSourceCheck, data)
    assert check.passed is False
    assert messages(check, "ERROR") == [
        "Source Spam page (https://spam.example/) supports no product fact or coverage claim. Link it to the "
        "fact it supports, or delete it."
    ]


@pytest.mark.parametrize(
    "use",
    ["publisher_of_products", "description_of_products", "license_model_of_products", "status_of_products", "coverage_claims"],
)
def test_source_with_any_use_passes(use: str) -> None:
    data = main_catalog()
    unused = source("s2", "Used page", "https://used.example/", uses=0)
    unused[use] = {"count": 1}
    add(data, "CatalogSource", unused)
    assert messages(run(CatalogUnusedSourceCheck, copy.deepcopy(data)), "ERROR") == []
