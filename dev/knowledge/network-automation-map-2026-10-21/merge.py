"""Turn the research batches into catalog object files.

Usage: python3 merge.py <repo root>
Reads batch*.json next to this script, validates every entry, and appends new sources, publishers
and products to objects/02_sources.yml, 03_publishers.yml and 04_products.yml. Prints a review
table and every problem found. Writes nothing if any entry fails validation.
"""

import json
import sys
from datetime import date
from pathlib import Path

import yaml

BLOCKS = {"Intent", "Observability", "Orchestrator", "Executor", "Collector", "Presentation"}
LICENSES = {"open_source", "open_core", "commercial", None}
EXTENTS = {"full", "partial"}
TODAY = date.today().isoformat() + "T00:00:00Z"

# Decisions made with the user on 2026-10-21.
PUBLISHER_NAMES = {"Cisco Systems, Inc.": "Cisco", "Nokia (SRL Labs)": "Nokia"}
LEGAL_SUFFIXES = (", Inc.", " Inc.", ", LLC", " LLC", " GmbH", " Ltd")
# The catalog's full name is "<publisher> <product>", so drop the brand from product names.
PRODUCT_NAMES = {
    "SolarWinds Network Performance Monitor": "Network Performance Monitor",
    "Infoblox NIOS": "NIOS",
    "Nokia Event-Driven Automation (EDA)": "Event-Driven Automation (EDA)",
    "Cisco Modeling Labs": "Modeling Labs",
    "Cisco Crosswork Network Services Orchestrator (NSO)": "Crosswork Network Services Orchestrator (NSO)",
    "NetBrain Agentic NetOps Platform": "Agentic NetOps Platform",
    "Skybox Firewall Assurance": "Firewall Assurance",
    "Tufin Orchestration Suite": "Orchestration Suite",
    "FireMon Security Manager": "Security Manager",
    "Itential Platform": "Platform",
    "ServiceNow IT Service Management": "IT Service Management",
    "NUTS (Network Unit Testing System)": "NUTS",
}
PUBLISHER_HOMEPAGES = {"Nokia": "https://www.nokia.com/", "Cisco": "https://www.cisco.com/"}
PRODUCT_HOMEPAGES = {
    "Pliant": "https://newsroom.ibm.com/Blog-IBM-Acquires-Pliant-to-Further-Enhance-Network-IT-Automation-Capabilities",
}
STATUS = {
    "Skybox Firewall Assurance": ("discontinued", "2025-02-24T00:00:00Z", [
        "https://www.tufin.com/tufin-expresspath-program",
        "https://www.securityweek.com/skybox-security-shuts-down-lays-off-entire-workforce/",
    ]),
    "System Initiative": ("discontinued", None, ["https://github.com/systeminit/si"]),
    "Pliant": ("acquired", None, [
        "https://newsroom.ibm.com/Blog-IBM-Acquires-Pliant-to-Further-Enhance-Network-IT-Automation-Capabilities",
    ]),
}

here = Path(__file__).parent
repo = Path(sys.argv[1])
objects = repo / "objects"


def load_docs(path: Path) -> list[dict]:
    return [doc for doc in yaml.safe_load_all(path.read_text()) if doc]


existing_sources = {
    entry["url"]: entry for doc in load_docs(objects / "02_sources.yml") for entry in doc["spec"]["data"]
}
existing_publishers = {
    entry["name"]: entry for doc in load_docs(objects / "03_publishers.yml") for entry in doc["spec"]["data"]
}
existing_products = {
    (entry["publisher"], entry["name"]) for doc in load_docs(objects / "04_products.yml") for entry in doc["spec"]["data"]
}

problems: list[str] = []
new_sources: dict[str, dict] = {}
new_publishers: dict[str, dict] = {}
new_products: list[dict] = []
review: list[tuple] = []


def page_title(url: str, title: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    product = title.split(":")[0]
    return f"{product}: {parsed.netloc}{parsed.path}".rstrip("/")[:250]


def source(url: str | None, title: str, where: str) -> str | None:
    if not url:
        problems.append(f"{where}: missing source URL")
        return None
    url = url.strip()
    if url not in existing_sources and url not in new_sources:
        new_sources[url] = {"title": page_title(url, title), "url": url, "last_checked": TODAY}
    return url


for batch in sorted(here.glob("batch*.json")):
    for item in json.loads(batch.read_text()):
        original_name, publisher = item.get("name"), item.get("publisher")
        publisher = PUBLISHER_NAMES.get(publisher, publisher)
        for suffix in LEGAL_SUFFIXES:
            if publisher and publisher.endswith(suffix):
                publisher = publisher[: -len(suffix)]
        name = PRODUCT_NAMES.get(original_name, original_name)
        if publisher in PUBLISHER_HOMEPAGES:
            item["publisher_homepage"] = PUBLISHER_HOMEPAGES[publisher]
        if original_name in PRODUCT_HOMEPAGES:
            item["homepage"] = PRODUCT_HOMEPAGES[original_name]
        where = f"{batch.name}: {name}"
        if not name or not publisher:
            problems.append(f"{where}: missing name or publisher")
            continue
        if (publisher, name) in existing_products or name in {"Infrahub", "Ansible"}:
            review.append((name, publisher, "already in the catalog, skipped", "", ""))
            continue
        if item.get("license_model") not in LICENSES:
            problems.append(f"{where}: unknown license model {item.get('license_model')!r}")
        if not item.get("description"):
            problems.append(f"{where}: missing description")
        if publisher not in existing_publishers and publisher not in new_publishers:
            new_publishers[publisher] = {"name": publisher, "homepage_url": item.get("publisher_homepage")}
            if not item.get("publisher_homepage"):
                problems.append(f"{where}: missing publisher home page")

        pub_src = source((item.get("publisher_source") or {}).get("url"), f"{name}: publisher", where)
        desc_src = source((item.get("description_source") or {}).get("url"), f"{name}: description", where)
        entry = {
            "name": name,
            "publisher": publisher,
            "description": item.get("description"),
            "homepage_url": item.get("homepage"),
        }
        if not item.get("homepage"):
            problems.append(f"{where}: missing product home page")
        if item.get("license_model"):
            lic_src = source((item.get("license_source") or {}).get("url"), f"{name}: license", where)
            entry["license_model"] = item["license_model"]
            entry["license_model_sources"] = [lic_src]
        entry["publisher_sources"] = [pub_src]
        entry["description_sources"] = [desc_src]
        if original_name in STATUS:
            status, status_date, status_urls = STATUS[original_name]
            entry["status"] = status
            if status_date:
                entry["status_date"] = status_date
            entry["status_sources"] = [source(url, f"{name}: status", where) for url in status_urls]

        claims = []
        seen_blocks = set()
        for claim in item.get("claims") or []:
            block, extent = claim.get("block"), claim.get("extent")
            if block not in BLOCKS:
                problems.append(f"{where}: unknown building block {block!r}")
                continue
            if extent not in EXTENTS:
                problems.append(f"{where}: unknown extent {extent!r} for {block}")
                continue
            if block in seen_blocks:
                problems.append(f"{where}: two claims for {block}")
                continue
            seen_blocks.add(block)
            claim_src = source(claim.get("source_url"), f"{name}: {block}", where)
            claims.append({"building_block": block, "extent": extent,
                           "note": (claim.get("reasoning") or "").strip() or None, "sources": [claim_src]})
        if claims:
            entry["coverage_claims"] = {"data": [{k: v for k, v in c.items() if v} for c in claims]}
        new_products.append(entry)
        review.append((f"{publisher} {name}" + (f" [{STATUS[original_name][0]}]" if original_name in STATUS else ""), publisher, item.get("license_model") or "-",
                       ", ".join(f"{c['building_block']} ({c['extent']})" for c in claims) or "no claims",
                       (item.get("notes") or "")[:120]))

for row in review:
    print(" | ".join(str(cell) for cell in row))
print(f"\n{len(new_products)} new products, {len(new_publishers)} new publishers, {len(new_sources)} new sources")
if problems:
    print("\nPROBLEMS:")
    for problem in problems:
        print(" -", problem)
    sys.exit(1)

if "--write" in sys.argv:
    def append(path: Path, kind: str, data: list[dict], comment: str) -> None:
        if not data:
            return
        doc = {"apiVersion": "infrahub.app/v1", "kind": "Object", "spec": {"kind": kind, "data": data}}
        text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100)
        with path.open("a") as handle:
            handle.write(f"---\n# {comment}\n{text}")
    append(objects / "02_sources.yml", "CatalogSource", list(new_sources.values()),
           "Sources for the products added from the Network Automation Map (2026-10-21).")
    append(objects / "03_publishers.yml", "CatalogPublisher", list(new_publishers.values()),
           "Publishers of the products added from the Network Automation Map (2026-10-21).")
    append(objects / "04_products.yml", "CatalogProduct", new_products,
           "Products added from the Network Automation Map (2026-10-21).")
    print("object files updated")
