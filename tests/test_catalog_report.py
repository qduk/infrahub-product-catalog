"""Tests for the catalog coverage report.

tests/test_transforms.yml compares the complete report with the expected output files.
"""

import asyncio
import json
from pathlib import Path

from infrahub_sdk import Config, InfrahubClient
from infrahub_sdk.node import InfrahubNode

from transforms.catalog_report import CatalogReportTransform

FIXTURES = Path(__file__).parent / "fixtures"


def build_report(fixture: str) -> str:
    data = json.loads((FIXTURES / fixture / "input.json").read_text())
    # The client is required by the constructor but is not used: the data comes from the fixture.
    client = InfrahubClient(config=Config(address="http://localhost:8100"))
    transform = CatalogReportTransform(client=client, infrahub_node=InfrahubNode)
    return asyncio.run(transform.run(data=data))


def section(report: str, heading: str) -> str:
    """Return the text under a level-2 heading, up to the next level-2 heading."""
    start = report.index(f"## {heading}\n") + len(heading) + 4
    end = report.find("\n## ", start)
    return report[start:end if end != -1 else None].strip("\n")


def test_coverage_table_for_current_catalog() -> None:
    assert section(build_report("catalog_report_current"), "Coverage by product") == "\n".join(
        [
            "| Product | Collector | Executor | Intent | Observability | Orchestrator | Presentation |",
            "|---|---|---|---|---|---|---|",
            "| OpsMill Infrahub | — | — | Full | — | — | — |",
            "| Red Hat Ansible | Partial | Full | — | — | — | — |",
            "| Stardust Systems SuzieQ | Full | — | — | Full | — | — |",
            "",
            "Each claim's sources are listed on the claim in the catalog.",
        ]
    )


def test_coverage_table_for_empty_catalog() -> None:
    table = section(build_report("catalog_report_empty"), "Coverage by product")
    assert table.splitlines()[0] == (
        "| Product | Collector | Executor | Intent | Observability | Orchestrator | Presentation |"
    )
    assert "No products are recorded." in table


def test_product_without_claims_has_empty_cells() -> None:
    table = section(build_report("catalog_report_no_claims"), "Coverage by product")
    assert "| Example Corp Example Tool | — | — |" in table.splitlines()


def test_pipe_in_product_name_is_escaped() -> None:
    table = section(build_report("catalog_report_special_names"), "Coverage by product")
    assert '| Example Corp Tool "X" [beta] \\| (v2) | — | Full |' in table.splitlines()


def test_summary_line_uses_singular_for_one() -> None:
    report = build_report("catalog_report_special_names")
    assert "1 product, 2 building blocks, 1 coverage claim." in report.splitlines()
