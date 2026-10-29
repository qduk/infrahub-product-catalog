"""Build the catalog coverage report: a Markdown table of products against building blocks."""

from dataclasses import dataclass

from infrahub_sdk.transforms import InfrahubTransform

NO_COVERAGE = "—"
EXTENT_LABELS = {"full": "Full", "partial": "Partial"}
# A claim is full only when every requirement of these levels that applies to its block is met.
REQUIRED_LEVELS = {"must", "should"}


@dataclass
class Requirement:
    identifier: str
    level: str
    block: str | None  # None for a requirement that applies to every building block


def claim_extent(block: str, verdicts: dict[str, str], requirements: list[Requirement]) -> str:
    """Return "full" when every MUST and SHOULD requirement of the block itself is met.

    verdicts maps requirement identifiers to verdicts. Framework-wide requirements are shown with
    their verdicts but do not count (user decision, 2026-10-27). A claim with no verdicts is not
    assessed yet and counts as partial; a missing or other verdict counts as not met.
    """
    if not verdicts:
        return "partial"
    applying = [r for r in requirements if r.block == block and r.level in REQUIRED_LEVELS]
    return "full" if all(verdicts.get(r.identifier) == "met" for r in applying) else "partial"


@dataclass
class Product:
    name: str
    status: str
    claims: dict[str, str]  # building block name -> extent ("full" or "partial")

    @property
    def label(self) -> str:
        return self.name if self.status == "active" else f"{self.name} ({self.status})"


def sort_key(name: str) -> str:
    return name.casefold()


def count(number: int, singular: str, plural: str) -> str:
    return f"{number} {singular if number == 1 else plural}"


def table_cell(text: str) -> str:
    return text.replace("|", "\\|")


def coverage_table(blocks: list[str], products: list[Product]) -> list[str]:
    lines = [
        "## Coverage by product",
        "",
        "| Product | " + " | ".join(table_cell(block) for block in blocks) + " |",
        "|---|" + "---|" * len(blocks),
    ]
    for product in products:
        cells = [EXTENT_LABELS.get(product.claims.get(block, ""), NO_COVERAGE) for block in blocks]
        lines.append(f"| {table_cell(product.label)} | " + " | ".join(cells) + " |")
    if not products:
        lines.extend(["", "No products are recorded."])
    lines.extend(
        [
            "",
            "Full means that every MUST and SHOULD requirement of the building block is met. Each claim's "
            "verdicts and sources are listed on the claim in the catalog.",
        ]
    )
    return lines


class CatalogReportTransform(InfrahubTransform):
    query = "catalog_report"

    async def transform(self, data: dict) -> str:
        report_name = data["CatalogReport"]["edges"][0]["node"]["name"]["value"]
        requirements = [
            Requirement(
                identifier=edge["node"]["identifier"]["value"],
                level=edge["node"]["level"]["value"],
                block=(edge["node"]["building_block"]["node"] or {}).get("name", {}).get("value"),
            )
            for edge in data["CatalogRequirement"]["edges"]
        ]
        blocks = sorted(
            (edge["node"]["name"]["value"] for edge in data["CatalogBuildingBlock"]["edges"]),
            key=sort_key,
        )
        products = sorted(
            (
                Product(
                    name=edge["node"]["full_name"]["value"],
                    status=edge["node"]["status"]["value"],
                    claims={
                        claim["node"]["building_block"]["node"]["name"]["value"]: claim_extent(
                            claim["node"]["building_block"]["node"]["name"]["value"],
                            {
                                verdict["node"]["requirement"]["node"]["identifier"]["value"]: verdict["node"]["verdict"]["value"]
                                for verdict in claim["node"]["verdicts"]["edges"]
                            },
                            requirements,
                        )
                        for claim in edge["node"]["coverage_claims"]["edges"]
                    },
                )
                for edge in data["CatalogProduct"]["edges"]
            ),
            key=lambda product: sort_key(product.name),
        )
        claim_count = sum(len(product.claims) for product in products)

        lines = [
            f"# {report_name}",
            "",
            f"{count(len(products), 'product', 'products')}, "
            f"{count(len(blocks), 'building block', 'building blocks')}, "
            f"{count(claim_count, 'coverage claim', 'coverage claims')}.",
            "",
            *coverage_table(blocks, products),
        ]
        return "\n".join(lines) + "\n"
