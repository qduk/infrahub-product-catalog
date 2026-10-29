"""Tests for the catalog coverage report.

tests/test_transforms.yml compares the complete report with the expected output files.
"""

import asyncio
import json
from pathlib import Path

from infrahub_sdk import Config, InfrahubClient
from infrahub_sdk.node import InfrahubNode

from transforms.catalog_report import CatalogReportTransform, Requirement, claim_extent

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
            "Full means that every MUST and SHOULD requirement of the building block is met. Each claim's "
            "verdicts and sources are listed on the claim in the catalog.",
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


def test_status_is_shown_after_name_of_products_that_are_not_active() -> None:
    table = section(build_report("catalog_report_status"), "Coverage by product").splitlines()
    assert "| Closed Corp Old Tool (discontinued) | — | Full |" in table
    assert "| Example Corp Example Tool | — | — |" in table


def test_claim_is_full_only_when_every_must_and_should_is_met() -> None:
    requirements = [
        Requirement("intent-must-1", "must", "Intent"),
        Requirement("intent-should-1", "should", "Intent"),
        Requirement("intent-may-1", "may", "Intent"),
        Requirement("framework-should-1", "should", None),
        Requirement("executor-must-1", "must", "Executor"),
    ]
    all_met = {"intent-must-1": "met", "intent-should-1": "met", "framework-should-1": "met"}
    assert claim_extent("Intent", all_met, requirements) == "full"
    assert claim_extent("Intent", {**all_met, "intent-may-1": "not_met"}, requirements) == "full"
    assert claim_extent("Intent", {**all_met, "intent-should-1": "partly_met"}, requirements) == "partial"
    # Framework-wide requirements are shown but do not count toward full.
    assert claim_extent("Intent", {**all_met, "framework-should-1": "not_shown"}, requirements) == "full"
    assert claim_extent("Intent", {"intent-must-1": "met"}, requirements) == "partial"
    assert claim_extent("Intent", {}, requirements) == "partial"
