"""Checks that guard the catalog against submissions that change existing records, near-duplicate
records, products that cover no building block and sources that support nothing.

All four checks use the catalog_records query. They live in one file because Infrahub loads each
check file from its own copy of the repository, so check files cannot import each other.
"""

import re
from collections import defaultdict
from collections.abc import Callable, Iterable
from itertools import combinations
from pathlib import Path

from infrahub_sdk.checks import InfrahubCheck

QUERY = "catalog_records"
QUERY_FILE = Path("queries") / "catalog_records.gql"
SUBMISSION_PREFIX = "submission-"


def nodes(data: dict, kind: str) -> list[dict]:
    return [edge["node"] for edge in data[kind]["edges"]]


def attribute(name: str) -> Callable[[dict], object]:
    return lambda node: node[name]["value"]


def peer(name: str) -> Callable[[dict], object]:
    return lambda node: (node[name]["node"] or {}).get("id")


def peers(name: str) -> Callable[[dict], object]:
    return lambda node: sorted(edge["node"]["id"] for edge in node[name]["edges"])


# The facts each record states about itself, as compared with main. Links that other records make
# to a record (a publisher's products, a building block's claims, a source's products and claims)
# are left out, so that a new product may link to existing records.
FACTS: dict[str, tuple[str, dict[str, Callable[[dict], object]]]] = {
    "CatalogPublisher": (
        "Publisher",
        {"name": attribute("name"), "home page": attribute("homepage_url")},
    ),
    "CatalogProduct": (
        "Product",
        {
            "name": attribute("name"),
            "description": attribute("description"),
            "home page": attribute("homepage_url"),
            "license model": attribute("license_model"),
            "status": attribute("status"),
            "status date": attribute("status_date"),
            "publisher": peer("publisher"),
            "publisher sources": peers("publisher_sources"),
            "description sources": peers("description_sources"),
            "license model sources": peers("license_model_sources"),
            "status sources": peers("status_sources"),
        },
    ),
    "CatalogSource": (
        "Source",
        {"title": attribute("title"), "link": attribute("url"), "last-checked date": attribute("last_checked")},
    ),
    "CatalogCoverageClaim": (
        "Coverage claim",
        {
            "product": peer("product"),
            "building block": peer("building_block"),
            "note": attribute("note"),
            "sources": peers("sources"),
        },
    ),
    "CatalogRequirement": (
        "Requirement",
        {
            "identifier": attribute("identifier"),
            "level": attribute("level"),
            "position": attribute("position"),
            "summary": attribute("summary"),
            "statement": attribute("statement"),
            "reference link": attribute("reference_url"),
            "building block": peer("building_block"),
        },
    ),
    "CatalogRequirementVerdict": (
        "Requirement verdict",
        {
            "claim": peer("claim"),
            "requirement": peer("requirement"),
            "verdict": attribute("verdict"),
            "note": attribute("note"),
            "sources": peers("sources"),
        },
    ),
    "CatalogBuildingBlock": (
        "Building block",
        {
            "name": attribute("name"),
            "description": attribute("description"),
            "definition link": attribute("definition_url"),
        },
    ),
}

# Records that come from the framework itself; a submission may not add them.
FRAMEWORK_KINDS = {"CatalogBuildingBlock", "CatalogRequirement"}

SOURCE_USES = (
    "publisher_of_products",
    "description_of_products",
    "license_model_of_products",
    "status_of_products",
    "coverage_claims",
    "verdicts",
)


def normalise_name(name: str) -> str:
    """Lower case, letters and digits only. A name with no letters or digits is kept as written."""
    return re.sub(r"[\W_]+", "", name.casefold()) or name


def normalise_link(url: str) -> str:
    """Lower case, without the http:// or https:// prefix and without trailing slashes."""
    return re.sub(r"^https?://", "", url.strip().lower()).rstrip("/")


def pairs(items: Iterable[dict], key: Callable[[dict], object], label: Callable[[dict], str]):
    """Yield each pair of items that share a key, in label order."""
    groups: dict[object, list[dict]] = defaultdict(list)
    for item in items:
        groups[key(item)].append(item)
    for group in groups.values():
        yield from combinations(sorted(group, key=label), 2)


class CatalogSubmissionCheck(InfrahubCheck):
    """On a submission branch, fail when a record on main was deleted or changed, or a building
    block was added."""

    query = QUERY

    def is_submission(self) -> bool:
        return self.branch_name.startswith(SUBMISSION_PREFIX)

    async def main_data(self) -> dict:
        """Run catalog_records on main.

        The query is read from this copy of the repository, because both Infrahub and infrahubctl
        pass the branch's data to validate() and load the check from a copy of the repository.
        """
        query = (Path(self.root_directory) / QUERY_FILE).read_text()
        return await self.client.execute_graphql(query=query, branch_name="main")

    async def validate(self, data: dict) -> None:
        if not self.is_submission():
            self.log_info(
                message=f"This check applies only to submission branches (names that start with {SUBMISSION_PREFIX})."
            )
            return

        main = await self.main_data()
        for kind, (kind_label, facts) in FACTS.items():
            on_branch = {node["id"]: node for node in nodes(data, kind)}
            on_main = {node["id"]: node for node in nodes(main, kind)}
            for record_id, before in on_main.items():
                after = on_branch.get(record_id)
                if after is None:
                    self.log_error(
                        message=(
                            f"{kind_label} {before['display_label']} is on main but was deleted on this branch. "
                            "A submission may only add records; restore it."
                        ),
                        object_id=record_id,
                        object_type=kind,
                    )
                    continue
                for fact, value in facts.items():
                    if value(before) != value(after):
                        self.log_error(
                            message=(
                                f"{kind_label} {after['display_label']}: {fact} differs from main. "
                                "A submission may only add records; change it back, and make the edit on a "
                                "separate branch."
                            ),
                            object_id=record_id,
                            object_type=kind,
                        )
            if kind in FRAMEWORK_KINDS:
                for record_id in on_branch.keys() - on_main.keys():
                    self.log_error(
                        message=(
                            f"{kind_label} {on_branch[record_id]['display_label']} was added. Building blocks "
                            "and requirements come from the framework and are not added by submissions; "
                            "delete it."
                        ),
                        object_id=record_id,
                        object_type=kind,
                    )


class CatalogDuplicateCheck(InfrahubCheck):
    """Fail on publishers, products of one publisher and source links that differ only by case,
    spaces, punctuation, http/https or a trailing slash."""

    query = QUERY

    def validate(self, data: dict) -> None:
        publishers = nodes(data, "CatalogPublisher")
        publisher_names = {publisher["id"]: publisher["name"]["value"] for publisher in publishers}

        for first, second in pairs(publishers, lambda node: normalise_name(node["name"]["value"]), self.name_of):
            self.log_error(
                message=(
                    f"Publishers {self.name_of(first)} and {self.name_of(second)} have near-identical names. "
                    "Keep one and move its products to it, or rename one."
                ),
                object_id=second["id"],
                object_type=second["__typename"],
            )

        def product_key(node: dict) -> tuple:
            return (peer("publisher")(node), normalise_name(node["name"]["value"]))

        for first, second in pairs(nodes(data, "CatalogProduct"), product_key, self.name_of):
            publisher = publisher_names.get(peer("publisher")(first), "an unknown publisher")
            self.log_error(
                message=(
                    f"Products {self.name_of(first)} and {self.name_of(second)} of {publisher} have near-identical "
                    "names. Keep one, or rename one."
                ),
                object_id=second["id"],
                object_type=second["__typename"],
            )

        sources = nodes(data, "CatalogSource")
        for first, second in pairs(sources, lambda node: normalise_link(node["url"]["value"]), self.link_of):
            self.log_error(
                message=(
                    f"Sources {first['title']['value']} ({first['url']['value']}) and {second['title']['value']} "
                    f"({second['url']['value']}) point to the same page. Keep one and link its facts to it."
                ),
                object_id=second["id"],
                object_type=second["__typename"],
            )

    @staticmethod
    def name_of(node: dict) -> str:
        return node["name"]["value"]

    @staticmethod
    def link_of(node: dict) -> str:
        return node["url"]["value"]


class CatalogCoverageCheck(InfrahubCheck):
    """Warn about products that cover no building block. A warning does not block the merge."""

    query = QUERY

    def validate(self, data: dict) -> None:
        for product in nodes(data, "CatalogProduct"):
            if product["coverage_claims"]["count"] > 0:
                continue
            self.log_info(
                message=(
                    f"Warning: {product['full_name']['value']} covers no building block, so the web app does not "
                    "show it. Add a coverage claim, or confirm that the product covers none."
                ),
                object_id=product["id"],
                object_type=product["__typename"],
            )


class CatalogUnusedSourceCheck(InfrahubCheck):
    """Fail on sources that support no product fact, coverage claim or requirement verdict."""

    query = QUERY

    def validate(self, data: dict) -> None:
        for source in nodes(data, "CatalogSource"):
            if any(source[use]["count"] > 0 for use in SOURCE_USES):
                continue
            self.log_error(
                message=(
                    f"Source {source['title']['value']} ({source['url']['value']}) supports no product fact, "
                    "coverage claim or requirement verdict. Link it to the fact it supports, or delete it."
                ),
                object_id=source["id"],
                object_type=source["__typename"],
            )
