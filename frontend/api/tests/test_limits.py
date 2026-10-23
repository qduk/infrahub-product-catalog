"""Tests for the submission limits."""

from catalog_web.limits import WINDOW_SECONDS, SubmissionLimit


def test_each_address_is_limited_within_the_hour() -> None:
    limit = SubmissionLimit(per_address=2, total=100)
    assert limit.allow("203.0.113.1", now=0)
    assert limit.allow("203.0.113.1", now=10)
    assert not limit.allow("203.0.113.1", now=20)
    assert limit.allow("203.0.113.2", now=20)


def test_address_may_submit_again_after_an_hour() -> None:
    limit = SubmissionLimit(per_address=1, total=100)
    assert limit.allow("203.0.113.1", now=0)
    assert not limit.allow("203.0.113.1", now=WINDOW_SECONDS - 1)
    assert limit.allow("203.0.113.1", now=WINDOW_SECONDS)


def test_total_limit_applies_across_addresses() -> None:
    limit = SubmissionLimit(per_address=5, total=3)
    assert all(limit.allow(f"203.0.113.{n}", now=n) for n in range(3))
    assert not limit.allow("203.0.113.9", now=5)


def test_refused_submissions_are_not_counted() -> None:
    limit = SubmissionLimit(per_address=1, total=100)
    assert limit.allow("203.0.113.1", now=0)
    for second in range(1, 50):
        assert not limit.allow("203.0.113.1", now=second)
    assert limit.allow("203.0.113.1", now=WINDOW_SECONDS)


def test_service_refuses_submissions_over_the_limit(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from catalog_web import main
    from tests.test_submissions import VALID

    async def fake_submit(client, submission):
        return "submission-test"

    monkeypatch.setenv("INFRAHUB_API_TOKEN", "not-used")
    monkeypatch.setattr(main, "submit", fake_submit)
    monkeypatch.setattr(main, "get_client", lambda: None)
    monkeypatch.setattr(main, "limit", SubmissionLimit(per_address=1, total=100))
    client = TestClient(main.app)

    assert client.post("/api/submissions", json=VALID).status_code == 201
    refused = client.post("/api/submissions", json=VALID)
    assert refused.status_code == 429
    assert refused.json() == {"detail": main.TOO_MANY}
