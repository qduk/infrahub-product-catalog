"""Tests that confirm which messages the catalog source check logs for each fixture.

The YAML tests in test_checks.yml cannot confirm that a check fails: the SDK's pytest plugin only
reports a problem when a check fails while expected to pass.
"""

import asyncio
import json
from datetime import date
from pathlib import Path

import pytest

from checks import catalog_source_check
from checks.catalog_source_check import CatalogSourceCheck

FIXTURES = Path(__file__).parent / "fixtures"


def run_check(fixture: str) -> CatalogSourceCheck:
    data = json.loads((FIXTURES / fixture / "input.json").read_text())
    check = CatalogSourceCheck()
    asyncio.run(check.run(data=data))
    return check


# The SDK logs this message itself when a check passes.
SDK_PASS_MESSAGE = "Check succesfully completed"


def messages(check: CatalogSourceCheck, level: str) -> list[str]:
    return [
        log["message"] for log in check.logs if log["level"] == level and log["message"] != SDK_PASS_MESSAGE
    ]


def test_license_model_without_source_is_an_error() -> None:
    check = run_check("license_model_missing_source")
    assert check.passed is False
    assert messages(check, "ERROR") == [
        "Example Corp Example Product: the license model has no source. "
        "Add a license model source or remove the license model."
    ]


@pytest.mark.parametrize("fixture", ["license_model_with_source", "license_model_empty"])
def test_license_model_rule_passes(fixture: str) -> None:
    check = run_check(fixture)
    assert messages(check, "ERROR") == []


def test_old_source_is_reported_without_failing() -> None:
    check = run_check("source_old")
    assert check.passed is True
    assert messages(check, "INFO") == [
        "Due for review: Example documentation (https://example.org/docs) was last checked on "
        "2000-01-01, more than 6 months ago. Open the source, confirm the facts it supports and "
        "update the last-checked date."
    ]


def test_future_source_is_an_error() -> None:
    check = run_check("source_future")
    assert check.passed is False
    assert messages(check, "ERROR") == [
        "Example documentation (https://example.org/docs): the last-checked date 2099-01-01 is in "
        "the future. Correct the date."
    ]


def run_check_on_date(last_checked: str, today: str, monkeypatch: pytest.MonkeyPatch) -> CatalogSourceCheck:
    monkeypatch.setattr(catalog_source_check, "today", lambda: date.fromisoformat(today))
    data = json.loads((FIXTURES / "source_old" / "input.json").read_text())
    data["CatalogSource"]["edges"][0]["node"]["last_checked"]["value"] = last_checked
    check = CatalogSourceCheck()
    asyncio.run(check.run(data=data))
    return check


@pytest.mark.parametrize(
    ("last_checked", "today", "reported"),
    [
        ("2026-04-20T00:00:00+00:00", "2026-10-20", False),
        ("2026-04-19T23:59:59+00:00", "2026-10-20", True),
        ("2026-10-20T00:00:00+00:00", "2026-10-20", False),
        ("2026-02-28T00:00:00+00:00", "2026-08-31", False),
        ("2026-02-27T00:00:00+00:00", "2026-08-31", True),
    ],
)
def test_review_age_boundary(
    last_checked: str, today: str, reported: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    check = run_check_on_date(last_checked, today, monkeypatch)
    assert check.passed is True
    assert bool(messages(check, "INFO")) is reported


def test_date_after_today_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    check = run_check_on_date("2026-10-21T00:00:00+00:00", "2026-10-20", monkeypatch)
    assert check.passed is False


def test_months_before_uses_last_day_of_shorter_month() -> None:
    assert catalog_source_check.months_before(date(2026, 8, 31), 6) == date(2026, 2, 28)
    assert catalog_source_check.months_before(date(2028, 8, 31), 6) == date(2028, 2, 29)
    assert catalog_source_check.months_before(date(2027, 3, 15), 6) == date(2026, 9, 15)


def test_status_without_source_is_an_error() -> None:
    check = run_check("status_missing_source")
    assert check.passed is False
    assert messages(check, "ERROR") == [
        "Example Corp Example Product: the status is discontinued but has no source. Add a status source."
    ]


@pytest.mark.parametrize(
    "fixture",
    ["status_with_source", "license_model_with_source", "license_model_empty", "source_old"],
)
def test_status_rule_passes(fixture: str) -> None:
    check = run_check(fixture)
    assert not [message for message in messages(check, "ERROR") if "status" in message]
