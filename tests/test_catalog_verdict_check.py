"""Tests for the requirement verdict check."""

import asyncio

from checks.catalog_verdict_check import CatalogVerdictCheck

# The SDK logs this message itself when a check passes.
SDK_PASS_MESSAGE = "Check succesfully completed"


def verdict(value: str, sources: int, requirement: str, requirement_block: str | None, claim_block: str) -> dict:
    return {
        "node": {
            "id": f"{requirement}-{claim_block}",
            "__typename": "CatalogRequirementVerdict",
            "verdict": {"value": value},
            "sources": {"count": sources},
            "requirement": {
                "node": {
                    "identifier": {"value": requirement},
                    "building_block": {"node": {"name": {"value": requirement_block}} if requirement_block else None},
                }
            },
            "claim": {
                "node": {
                    "name": {"value": f"Example Corp Tool - {claim_block}"},
                    "building_block": {"node": {"name": {"value": claim_block}}},
                }
            },
        }
    }


def run(*verdicts: dict) -> CatalogVerdictCheck:
    check = CatalogVerdictCheck(branch="test-branch")
    asyncio.run(check.run(data={"CatalogRequirementVerdict": {"edges": list(verdicts)}}))
    return check


def errors(check: CatalogVerdictCheck) -> list[str]:
    return [log["message"] for log in check.logs if log["level"] == "ERROR"]


def test_sourced_verdicts_for_the_claims_block_pass() -> None:
    check = run(
        verdict("met", 1, "intent-must-1", "Intent", "Intent"),
        verdict("partly_met", 2, "framework-should-1", None, "Intent"),
        verdict("not_shown", 0, "intent-should-1", "Intent", "Intent"),
    )
    assert check.passed is True
    assert errors(check) == []


def test_verdict_without_source_fails() -> None:
    assert errors(run(verdict("not_met", 0, "intent-should-2", "Intent", "Intent"))) == [
        'Example Corp Tool - Intent, intent-should-2: the verdict "not met" has no source. Add the source '
        'that states it, or set the verdict to "not shown".'
    ]


def test_verdict_for_another_blocks_requirement_fails() -> None:
    assert errors(run(verdict("met", 1, "executor-must-1", "Executor", "Intent"))) == [
        "Example Corp Tool - Intent, executor-must-1: this requirement belongs to Executor, not to the "
        "claim's block Intent. Delete the verdict."
    ]
