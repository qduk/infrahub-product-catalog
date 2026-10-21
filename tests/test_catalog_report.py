"""Tests for each section of the catalog coverage report.

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


def test_bar_chart_for_current_catalog() -> None:
    assert section(build_report("catalog_report_current"), "Products per building block") == "\n".join(
        [
            "```mermaid",
            "xychart-beta",
            '    title "Products per building block"',
            '    x-axis ["Collector", "Executor", "Intent", "Observability", "Orchestrator", "Presentation"]',
            '    y-axis "Products" 0 --> 3',
            "    bar [2, 1, 1, 1, 0, 0]",
            "    bar [1, 1, 1, 1, 0, 0]",
            "```",
            "",
            "The first bar series counts all products that cover the block. The second, drawn over it, "
            "counts products with full coverage. The difference is partial coverage.",
        ]
    )


def test_bar_chart_for_empty_catalog() -> None:
    chart = section(build_report("catalog_report_empty"), "Products per building block")
    assert '    y-axis "Products" 0 --> 1' in chart.splitlines()
    assert "    bar [0, 0, 0, 0, 0, 0]" in chart.splitlines()


def test_quote_in_block_name_is_escaped_in_bar_chart() -> None:
    chart = section(build_report("catalog_report_special_names"), "Products per building block")
    assert '    x-axis ["Block #quot;B#quot;", "Block (A)"]' in chart.splitlines()


def test_product_map_for_current_catalog() -> None:
    assert section(build_report("catalog_report_current"), "Map of products to building blocks") == "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            '    p1["OpsMill Infrahub"]',
            '    p2["Red Hat Ansible"]',
            '    p3["Stardust Systems SuzieQ"]',
            '    b1["Collector"]',
            '    b2["Executor"]',
            '    b3["Intent"]',
            '    b4["Observability"]',
            '    b5["Orchestrator"]',
            '    b6["Presentation"]',
            "    p1 ==> b3",
            "    p2 -.-> b1",
            "    p2 ==> b2",
            "    p3 ==> b1",
            "    p3 ==> b4",
            "```",
            "",
            "Thick lines show full coverage. Dotted lines show partial coverage.",
        ]
    )


def test_product_map_without_claims_has_no_lines() -> None:
    diagram = section(build_report("catalog_report_no_claims"), "Map of products to building blocks")
    assert '    p1["Example Corp Example Tool"]' in diagram.splitlines()
    assert "==>" not in diagram
    assert "-.->" not in diagram


def test_special_characters_are_escaped_in_product_map() -> None:
    diagram = section(build_report("catalog_report_special_names"), "Map of products to building blocks")
    assert '    p1["Example Corp Tool #quot;X#quot; [beta] | (v2)"]' in diagram.splitlines()
    assert '    b1["Block #quot;B#quot;"]' in diagram.splitlines()
    assert "    p1 ==> b2" in diagram.splitlines()


def test_summary_line_uses_singular_for_one() -> None:
    report = build_report("catalog_report_special_names")
    assert "1 product, 2 building blocks, 1 coverage claim." in report.splitlines()
