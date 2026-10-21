"""Check that product facts have sources and that sources are reviewed regularly."""

import calendar
from datetime import UTC, date, datetime

from infrahub_sdk.checks import InfrahubCheck

REVIEW_AGE_MONTHS = 6


def today() -> date:
    return datetime.now(UTC).date()


def months_before(day: date, months: int) -> date:
    """Return the same day the given number of calendar months earlier.

    When that month is shorter, return its last day (31 August minus 6 months is 28 February).
    """
    month_index = day.year * 12 + day.month - 1 - months
    year, month = divmod(month_index, 12)
    month += 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last_day))


class CatalogSourceCheck(InfrahubCheck):
    query = "catalog_source_check"

    def validate(self, data: dict) -> None:
        for edge in data["CatalogProduct"]["edges"]:
            self.check_license_model_source(edge["node"])
            self.check_status_source(edge["node"])

        current_day = today()
        cutoff = months_before(current_day, REVIEW_AGE_MONTHS)
        for edge in data["CatalogSource"]["edges"]:
            self.check_last_checked(edge["node"], current_day, cutoff)

    def check_license_model_source(self, product: dict) -> None:
        if not product["license_model"]["value"] or product["license_model_sources"]["count"] > 0:
            return
        self.log_error(
            message=(
                f"{product['full_name']['value']}: the license model has no source. "
                "Add a license model source or remove the license model."
            ),
            object_id=product["id"],
            object_type=product["__typename"],
        )

    def check_status_source(self, product: dict) -> None:
        status = product["status"]["value"]
        if status == "active" or product["status_sources"]["count"] > 0:
            return
        self.log_error(
            message=(
                f"{product['full_name']['value']}: the status is {status} but has no source. "
                "Add a status source."
            ),
            object_id=product["id"],
            object_type=product["__typename"],
        )

    def check_last_checked(self, source: dict, current_day: date, cutoff: date) -> None:
        checked = datetime.fromisoformat(source["last_checked"]["value"]).astimezone(UTC).date()
        label = f"{source['title']['value']} ({source['url']['value']})"

        if checked > current_day:
            self.log_error(
                message=(
                    f"{label}: the last-checked date {checked.isoformat()} is in the future. "
                    "Correct the date."
                ),
                object_id=source["id"],
                object_type=source["__typename"],
            )
        elif checked < cutoff:
            self.log_info(
                message=(
                    f"Due for review: {label} was last checked on {checked.isoformat()}, more than "
                    f"{REVIEW_AGE_MONTHS} months ago. Open the source, confirm the facts it supports "
                    "and update the last-checked date."
                ),
                object_id=source["id"],
                object_type=source["__typename"],
            )
