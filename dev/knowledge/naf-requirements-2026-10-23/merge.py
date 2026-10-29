"""Merge the research results into one set of verdicts, validate them, and write the outputs.

Inputs: requirements.json, research-input/*.json, research-output/*.json, and the catalog's
object files. Outputs:
- verdicts.json: every verdict, one per claim and applying requirement;
- review.json: per claim, the extent before (as recorded on main) and after (computed);
- objects/06_requirement_verdicts.yml: new sources and the verdicts, for loading (--write-objects).

Run: uv run python dev/knowledge/naf-requirements-2026-10-23/merge.py [--write-objects]
"""

import json
import re
import subprocess
import sys
import textwrap
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
TODAY = "2026-10-23T00:00:00Z"
VERDICTS = {"met", "partly_met", "not_met", "not_shown"}
REQUIRED_LEVELS = {"must", "should"}


def normalise_link(url: str) -> str:
    """Same rule as catalog_duplicate_check."""
    return re.sub(r"^https?://", "", url.strip().lower()).rstrip("/")


def catalog_sources() -> dict[str, str]:
    sources = {}
    for doc in yaml.safe_load_all((ROOT / "objects/02_sources.yml").read_text()):
        if doc and doc["spec"]["kind"] == "CatalogSource":
            for source in doc["spec"]["data"]:
                sources[source["url"]] = source["title"]
    return sources


def products_file_claims() -> tuple[set[str], set[str]]:
    """Claims in objects/04_products.yml now, and every source URL the products and claims use."""
    claims, used = set(), set()
    for doc in yaml.safe_load_all((ROOT / "objects/04_products.yml").read_text()):
        if not doc:
            continue
        for product in doc["spec"]["data"]:
            publisher = product["publisher"] if isinstance(product["publisher"], str) else product["publisher"][0]
            for field in ("publisher_sources", "description_sources", "license_model_sources", "status_sources"):
                used.update(product.get(field) or [])
            entries = product.get("coverage_claims", {})
            entries = entries.get("data", entries) if isinstance(entries, dict) else entries
            for claim in entries or []:
                claims.add(f"{publisher} {product['name']} - {claim['building_block']}")
                used.update(claim.get("sources") or [])
    return claims, used


def old_extents() -> dict[str, str]:
    """Extents as recorded on main before this feature, from Git."""
    text = subprocess.run(
        ["git", "show", "main:objects/04_products.yml"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    extents = {}
    for doc in yaml.safe_load_all(text):
        if not doc:
            continue
        for product in doc["spec"]["data"]:
            publisher = product["publisher"] if isinstance(product["publisher"], str) else product["publisher"][0]
            claims = product.get("coverage_claims", {})
            claims = claims.get("data", claims) if isinstance(claims, dict) else claims
            for claim in claims or []:
                extents[f"{publisher} {product['name']} - {claim['building_block']}"] = claim["extent"]
    return extents


def extent(block: str, verdicts: dict[str, str], requirements: list[dict]) -> str:
    # Framework-wide requirements are shown but do not count toward full (user decision, 2026-10-27).
    applying = [r for r in requirements if r["block"] == block and r["level"] in REQUIRED_LEVELS]
    return "full" if verdicts and all(verdicts.get(r["identifier"]) == "met" for r in applying) else "partial"


def main() -> None:
    requirements = json.loads((HERE / "requirements.json").read_text())
    by_id = {r["identifier"]: r for r in requirements}
    problems: list[str] = []

    # Claims still in the catalog. Claims and products the user removed on 2026-10-27 are skipped.
    current, used_by_products = products_file_claims()
    claims: dict[str, dict] = {}  # claim -> {"block", "product"}
    for path in sorted((HERE / "research-input").glob("*.json")):
        data = json.loads(path.read_text())
        for claim in data.get("claims", []):
            if claim["claim"] in current:
                claims[claim["claim"]] = {"block": data["block"], "product": claim["product"]}
    missing = current - set(claims)
    if missing:
        problems.append(f"claims without research: {sorted(missing)}")

    verdicts: dict[tuple[str, str], dict] = {}
    framework: dict[tuple[str, str], dict] = {}
    for path in sorted((HERE / "research-output").glob("*.json")):
        for entry in json.loads(path.read_text()):
            if entry.get("verdict") not in VERDICTS:
                problems.append(f"{path.name}: invalid verdict {entry}")
                continue
            if entry["verdict"] != "not_shown" and not entry.get("sources"):
                problems.append(f"{path.name}: no source for {entry.get('claim') or entry.get('product')} {entry['requirement']}")
            if path.name == "framework.json":
                framework[(entry["product"], entry["requirement"])] = entry
            elif entry["claim"] not in claims:
                continue
            else:
                key = (entry["claim"], entry["requirement"])
                if key in verdicts:
                    problems.append(f"duplicate verdict {key}")
                verdicts[key] = entry

    # Framework-wide verdicts apply to every claim of the product.
    for claim, info in claims.items():
        for identifier in ("framework-should-1", "framework-should-2"):
            entry = framework.get((info["product"], identifier))
            if entry:
                verdicts[(claim, identifier)] = {**entry, "claim": claim}

    # Changes decided after the research (adjustments.json): the looser reading of two requirements,
    # and corrections from the user's knowledge of the products, which carry their own note and sources.
    adjustments = json.loads((HERE / "adjustments.json").read_text())

    def apply_change(key: tuple[str, str], change: dict) -> None:
        if key not in verdicts:
            problems.append(f"adjustment for an unknown verdict: {key}")
            return
        updated = {**verdicts[key], "verdict": change["verdict"]}
        for field in ("note", "sources"):
            if field in change:
                updated[field] = change[field]
        updated["adjusted"] = change.get("reason") or adjustments["rules"].get(change["requirement"], "")
        if updated["verdict"] != "not_shown" and not updated.get("sources"):
            problems.append(f"adjusted verdict without a source: {key}")
        verdicts[key] = updated

    for change in adjustments["changes"]:
        if change["claim"] not in claims:
            continue  # a claim the user removed
        # A framework-wide verdict belongs to the product, so its correction applies to every claim.
        if change["requirement"].startswith("framework-"):
            product = claims[change["claim"]]["product"]
            keys = [(c, change["requirement"]) for c, info in claims.items() if info["product"] == product]
        else:
            keys = [(change["claim"], change["requirement"])]
        for key in keys:
            apply_change(key, change)

    # Every claim needs one verdict for each requirement that applies to its block.
    for claim, info in claims.items():
        for requirement in requirements:
            if requirement["block"] in (None, info["block"]) and (claim, requirement["identifier"]) not in verdicts:
                problems.append(f"missing verdict: {claim} / {requirement['identifier']}")
    for claim, identifier in verdicts:
        requirement = by_id.get(identifier)
        if claim not in claims or requirement is None or requirement["block"] not in (None, claims[claim]["block"]):
            problems.append(f"verdict does not apply: {claim} / {identifier}")

    # Reuse catalog sources whose link matches after normalisation; collect the new ones.
    existing = catalog_sources()
    existing_by_key = {normalise_link(url): url for url in existing}
    new_sources: dict[str, dict] = {}
    for entry in verdicts.values():
        resolved = []
        for source in entry.get("sources", []):
            key = normalise_link(source["url"])
            url = existing_by_key.get(key) or new_sources.get(key, {}).get("url") or source["url"]
            if key not in existing_by_key and key not in new_sources:
                new_sources[key] = {"title": source["title"].strip()[:200], "url": url}
            if url not in resolved:
                resolved.append(url)
        entry["source_urls"] = resolved

    before = old_extents()
    review = []
    for claim, info in sorted(claims.items()):
        claim_verdicts = {identifier: v["verdict"] for (c, identifier), v in verdicts.items() if c == claim}
        review.append(
            {
                "claim": claim,
                "product": info["product"],
                "block": info["block"],
                "before": before.get(claim),
                "after": extent(info["block"], claim_verdicts, requirements),
            }
        )

    for (claim, _), entry in verdicts.items():
        entry["product"], entry["block"] = claims[claim]["product"], claims[claim]["block"]

    ordered = sorted(verdicts.values(), key=lambda v: (v["claim"], by_id[v["requirement"]]["position"]))
    (HERE / "verdicts.json").write_text(json.dumps(ordered, indent=2) + "\n")
    (HERE / "review.json").write_text(json.dumps(review, indent=2) + "\n")

    print(f"claims: {len(claims)}, verdicts: {len(verdicts)}, new sources: {len(new_sources)}")
    print("verdicts:", dict(Counter(v["verdict"] for v in verdicts.values())))
    print("extent before:", dict(Counter(r["before"] for r in review)), "after:", dict(Counter(r["after"] for r in review)))
    print("full before, partial after:", sum(1 for r in review if r["before"] == "full" and r["after"] == "partial"))
    print("partial before, full after:", sum(1 for r in review if r["before"] == "partial" and r["after"] == "full"))
    for problem in problems[:40]:
        print("PROBLEM:", problem)
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)

    if "--write-objects" in sys.argv:
        write_objects(ordered, sorted(new_sources.values(), key=lambda s: s["url"]))
        used = used_by_products | {url for v in ordered for url in v["source_urls"]}
        remove_unused_sources(used)


def block_scalar(text: str, indent: int) -> list[str]:
    pad = " " * indent
    return [pad + line for line in textwrap.wrap(text, 96 - indent, break_on_hyphens=False, break_long_words=False)]


def write_objects(verdicts: list[dict], new_sources: list[dict]) -> None:
    lines = [
        "---",
        "# Sources that support requirement verdicts and were not yet in objects/02_sources.yml.",
        "# Generated by dev/knowledge/naf-requirements-2026-10-23/merge.py from the approved research.",
        "apiVersion: infrahub.app/v1",
        "kind: Object",
        "spec:",
        "  kind: CatalogSource",
        "  data:",
    ]
    for source in new_sources:
        lines += [
            f"    - title: {json.dumps(source['title'])}",
            f"      url: {source['url']}",
            f'      last_checked: "{TODAY}"',
        ]
    lines += [
        "---",
        "# Verdicts: whether each product meets each framework requirement that applies to a building",
        "# block it covers. Researched on 2026-10-23 and approved by the user before loading.",
        "# Generated by dev/knowledge/naf-requirements-2026-10-23/merge.py.",
        "apiVersion: infrahub.app/v1",
        "kind: Object",
        "spec:",
        "  kind: CatalogRequirementVerdict",
        "  data:",
    ]
    for verdict in verdicts:
        lines += [
            f"    - claim: {json.dumps([verdict['product'], verdict['block']])}",
            f"      requirement: {verdict['requirement']}",
            f"      verdict: {verdict['verdict']}",
        ]
        if verdict.get("note"):
            lines += ["      note: >-", *block_scalar(verdict["note"], 8)]
        if verdict["source_urls"]:
            lines += ["      sources:", *[f"        - {url}" for url in verdict["source_urls"]]]
    (ROOT / "objects/06_requirement_verdicts.yml").write_text("\n".join(lines) + "\n")
    print(f"wrote objects/06_requirement_verdicts.yml: {len(new_sources)} sources, {len(verdicts)} verdicts")


def remove_unused_sources(used: set[str]) -> None:
    """Drop entries of objects/02_sources.yml that no product fact, claim or verdict uses any more."""
    path = ROOT / "objects/02_sources.yml"
    lines = path.read_text().split("\n")
    kept, removed, i = [], [], 0
    while i < len(lines):
        item = re.match(r"^(\s*)- title:", lines[i])
        if item:
            body = " " * (len(item.group(1)) + 2)
            j = i + 1
            while j < len(lines) and lines[j].startswith(body):
                j += 1
            url = next(line.split("url:", 1)[1].strip() for line in lines[i:j] if line.strip().startswith("url:"))
            (kept.extend(lines[i:j]) if url in used else removed.append(url))
            i = j
        else:
            kept.append(lines[i])
            i += 1
    path.write_text("\n".join(kept))
    print(f"removed {len(removed)} unused sources from objects/02_sources.yml: {removed}")
    # Keep a record of every source removed, so apply_removals.py deletes exactly these in Infrahub.
    record = HERE / "removed-sources.json"
    earlier = json.loads(record.read_text()) if record.exists() else []
    record.write_text(json.dumps(sorted(set(earlier) | set(removed)), indent=2) + "\n")


if __name__ == "__main__":
    main()
