"""Check that requirement verdicts have sources and belong to the claim's building block."""

from infrahub_sdk.checks import InfrahubCheck

VERDICT_LABELS = {"met": "met", "partly_met": "partly met", "not_met": "not met", "not_shown": "not shown"}


def block_name(relationship: dict) -> str | None:
    node = relationship["node"]
    return node["name"]["value"] if node else None


class CatalogVerdictCheck(InfrahubCheck):
    query = "catalog_verdict_check"

    def validate(self, data: dict) -> None:
        for edge in data["CatalogRequirementVerdict"]["edges"]:
            verdict = edge["node"]
            claim = verdict["claim"]["node"]
            requirement = verdict["requirement"]["node"]
            label = f"{claim['name']['value']}, {requirement['identifier']['value']}"
            value = verdict["verdict"]["value"]

            if value != "not_shown" and verdict["sources"]["count"] == 0:
                self.log_error(
                    message=(
                        f'{label}: the verdict "{VERDICT_LABELS.get(value, value)}" has no source. Add the '
                        'source that states it, or set the verdict to "not shown".'
                    ),
                    object_id=verdict["id"],
                    object_type=verdict["__typename"],
                )

            requirement_block = block_name(requirement["building_block"])
            claim_block = block_name(claim["building_block"])
            if requirement_block is not None and requirement_block != claim_block:
                self.log_error(
                    message=(
                        f"{label}: this requirement belongs to {requirement_block}, not to the claim's block "
                        f"{claim_block}. Delete the verdict."
                    ),
                    object_id=verdict["id"],
                    object_type=verdict["__typename"],
                )
