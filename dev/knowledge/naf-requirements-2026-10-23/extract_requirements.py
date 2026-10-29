"""Builds the requirement records from the saved framework page (framework-page-2026-10-23.html).

Each requirement is found by the start of its sentence, and the statement is taken from the page
as written. Run: uv run python dev/knowledge/naf-requirements-2026-10-23/extract_requirements.py
"""

import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
PAGE = "https://reference.networkautomation.forum/Framework/Framework/"

# Short summaries in the catalog's own words, shown as the title of each requirement. They tell
# apart the two requirements recorded from one sentence.
SUMMARIES = {
    "framework-should-1": "Follows software engineering practices such as version control and CI/CD",
    "framework-should-2": "Exposes machine-friendly APIs documented by a schema",
    "intent-must-1": "Represents any network-related aspect in a structured form",
    "intent-must-2": "Supports create, read, update and delete on the data",
    "intent-must-3": "Exposes the data through a standardized, documented API",
    "intent-should-1": "Uses a vendor-neutral model that is turned into vendor configuration",
    "intent-should-2": "Gives one consistent view of the desired state across data sources",
    "intent-should-3": "Records governance metadata: timestamps, origin, ownership, validity",
    "intent-should-4": "Offers transactional changes, custom validation and versioned data",
    "intent-may-1": "Includes intended-state logic such as validation and artifact generation",
    "executor-must-1": "Writes to the network over SSH, NETCONF, gNMI/gNOI and REST APIs",
    "executor-should-1": "Supports any operation that changes the network state",
    "executor-should-2": "Takes task input from the intended state",
    "executor-should-3": "Offers a dry run of an execution",
    "executor-should-4": "Applies changes as a transaction",
    "executor-should-5": "Runs operations idempotently",
    "executor-may-1": "Supports both imperative and declarative tasks",
    "collector-must-1": "Reads live network data, including SNMP, Syslog, flows and packets",
    "collector-should-1": "Normalizes data across vendors and collection methods",
    "observability-must-1": "Stores historical data with powerful programmatic access",
    "observability-should-1": "Offers a capable query language",
    "observability-should-2": "Detects drift from the intended state and generates events",
    "observability-may-1": "Sends drift events to people or to the Orchestrator",
    "observability-may-2": "Enriches data with intended state and third-party context",
    "orchestrator-must-1": "Coordinates processes across the building blocks into workflows",
    "orchestrator-should-1": "Runs workflows from events, synchronous, asynchronous or scheduled",
    "orchestrator-should-2": "Supports compensating actions for a controlled rollback",
    "orchestrator-should-3": "Offers a dry run of a workflow",
    "orchestrator-should-4": "Schedules workflows on a regular basis or at a set time",
    "orchestrator-should-5": "Gives logging and traceability of past and current workflows",
    "orchestrator-may-1": "Correlates events to decide the course of action",
    "presentation-must-1": "Provides robust authentication and authorization",
    "presentation-may-1": "Takes forms such as GUIs, ITSM, chat, portals or dashboards",
    "presentation-may-2": "Supports both read and write interactions",
}

# identifier, block (None = framework-wide), level, section anchor, start of the sentence on the page
REQUIREMENTS = [
    ("framework-should-1", None, "should", "context", "All components SHOULD follow modern software engineering practices"),
    ("framework-should-2", None, "should", "context", "All components SHOULD follow modern software engineering practices"),
    ("intent-must-1", "Intent", "must", "intent", "It MUST be capable of representing, in a structured form"),
    ("intent-must-2", "Intent", "must", "intent", "The data MUST support create, read, update, and delete"),
    ("intent-must-3", "Intent", "must", "intent", "Access to this information MUST be exposed"),
    ("intent-should-1", "Intent", "should", "intent", "The modeling SHOULD use a neutral representation"),
    ("intent-should-2", "Intent", "should", "intent", "It SHOULD provide a consistent and unified view"),
    ("intent-should-3", "Intent", "should", "intent", "In addition to the core network data, it SHOULD include metadata"),
    ("intent-should-4", "Intent", "should", "intent", "Ideally, these operations SHOULD be transactional"),
    ("intent-may-1", "Intent", "may", "intent", "It MAY include all the logic related to intended state management"),
    ("executor-must-1", "Executor", "must", "executor", "It MUST be capable of interacting with any of the supported network write interfaces"),
    ("executor-should-1", "Executor", "should", "executor", "It SHOULD support any network operation that alters the network state"),
    ("executor-should-2", "Executor", "should", "executor", "The task input SHOULD come from the intended state"),
    ("executor-should-3", "Executor", "should", "executor", "It SHOULD provide a dry-run operation to check the expected result of the execution"),
    ("executor-should-4", "Executor", "should", "executor", "It SHOULD support transactional execution"),
    ("executor-may-1", "Executor", "may", "executor", "It MAY support both imperative approaches"),
    ("executor-should-5", "Executor", "should", "executor", "It MAY support both imperative approaches"),
    ("collector-must-1", "Collector", "must", "collector", "It MUST includes capabilities for retrieving live data"),
    ("collector-should-1", "Collector", "should", "collector", "The data values SHOULD be normalized"),
    ("observability-must-1", "Observability", "must", "observability", "It MUST support historical data persistence"),
    ("observability-should-1", "Observability", "should", "observability", "It SHOULD offer a capable query language"),
    ("observability-should-2", "Observability", "should", "observability", "It SHOULD expose relevant insights"),
    ("observability-may-1", "Observability", "may", "observability", "It SHOULD expose relevant insights"),
    ("observability-may-2", "Observability", "may", "observability", "Retrieved data MAY be enriched"),
    ("orchestrator-must-1", "Orchestrator", "must", "orchestrator", "It MUST enable the coordination and integration of processes"),
    ("orchestrator-should-1", "Orchestrator", "should", "orchestrator", "Process execution SHOULD follow an event-driven approach"),
    ("orchestrator-should-2", "Orchestrator", "should", "orchestrator", "Execution logic SHOULD allow for reverse/compensating actions"),
    ("orchestrator-should-3", "Orchestrator", "should", "orchestrator", "It SHOULD provide a dry-run operation to check the expected result of the workflow"),
    ("orchestrator-should-4", "Orchestrator", "should", "orchestrator", "It SHOULD provide the ability to schedule"),
    ("orchestrator-should-5", "Orchestrator", "should", "orchestrator", "It SHOULD provide end users with an understanding"),
    ("orchestrator-may-1", "Orchestrator", "may", "orchestrator", "It MAY include logic to correlate multiple events"),
    ("presentation-must-1", "Presentation", "must", "presentation", "It MUST provide robust and flexible authentication"),
    ("presentation-may-1", "Presentation", "may", "presentation", "This component MAY take various forms"),
    ("presentation-may-2", "Presentation", "may", "presentation", "It MAY support both read and write interactions"),
]


def page_text() -> str:
    raw = (HERE / "framework-page-2026-10-23.html").read_text()
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", text)


def sentence(text: str, start: str) -> str:
    begin = text.index(start)
    # A statement ends where the next statement or a section heading starts. The sentences that
    # follow a statement without a keyword of their own ("This broad scope ...", "In both cases ...",
    # "These events MAY ...") stay part of it.
    rest = text[begin:]
    end = re.search(r"(?<=[.)]) (?=(It|The|In addition|Access|Ideally|Process|Execution|This component|Retrieved|Moreover|Intent|Executor|Collector|Observability|Orchestrator|Presentation|Brand)\b)", rest)
    statement = rest[: end.start()] if end else rest
    return statement.strip()


def main() -> None:
    text = page_text()
    records = []
    for position, (identifier, block, level, anchor, start) in enumerate(REQUIREMENTS, start=1):
        statement = sentence(text, start)
        assert level.upper() in statement, (identifier, statement)
        records.append(
            {
                "identifier": identifier,
                "block": block,
                "level": level,
                "position": position,
                "summary": SUMMARIES[identifier],
                "statement": statement,
                "reference_url": f"{PAGE}#{anchor}",
            }
        )
    (HERE / "requirements.json").write_text(json.dumps(records, indent=2) + "\n")
    for record in records:
        print(f"{record['identifier']:24} {record['statement'][:150]}")


if __name__ == "__main__":
    main()
