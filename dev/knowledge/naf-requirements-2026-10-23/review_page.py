"""Build the review page (HTML) for the requirement verdicts from verdicts.json and review.json.

Run after merge.py: uv run python dev/knowledge/naf-requirements-2026-10-23/review_page.py <output.html>
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main() -> None:
    requirements = json.loads((HERE / "requirements.json").read_text())
    verdicts = json.loads((HERE / "verdicts.json").read_text())
    review = json.loads((HERE / "review.json").read_text())
    data = {
        "requirements": [
            {k: r[k] for k in ("identifier", "block", "level", "position", "summary", "statement", "reference_url")}
            for r in requirements
        ],
        "claims": review,
        "verdicts": [
            {
                "claim": v["claim"],
                "requirement": v["requirement"],
                "verdict": v["verdict"],
                "note": v.get("note") or "",
                "sources": [{"title": s["title"], "url": s["url"]} for s in v.get("sources", [])],
            }
            for v in verdicts
        ],
    }
    adjustments = json.loads((HERE / "adjustments.json").read_text())
    corrected = {(c["claim"], c["requirement"]) for c in adjustments["changes"] if "reason" in c}
    decided = corrected | set(KEPT_BY_USER)
    all_focus = focus(requirements, verdicts, review)
    framework_wide = {r["identifier"] for r in requirements if r["block"] is None}
    # Framework-wide verdicts do not count toward full coverage, so they are not worth a review.
    data["focus"] = [
        f for f in all_focus if (f["claim"], f["requirement"]) not in decided and f["requirement"] not in framework_wide
    ]
    data["decided"] = [
        {"claim": c, "requirement": r, "how": "changed by you" if (c, r) in corrected else "kept as researched"}
        for c, r in sorted(decided)
        if any(v["claim"] == c and v["requirement"] == r for v in verdicts)
    ]
    data["questioned"] = QUESTIONED
    data["removed"] = REMOVED
    page = TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    Path(sys.argv[1]).write_text(page)
    print(f"wrote {sys.argv[1]} ({len(page) // 1024} KB)")


# Coverage claims the research questions, with a recommendation for each.
QUESTIONED: list[dict] = []  # decided on 2026-10-27; see REMOVED

# Removed from the catalog by the user on 2026-10-27, after the research questioned them.
REMOVED = [
    "NUTS (Network Unit Testing System): the whole product, on Intent, Observability and Collector",
    "Spacelift: the whole product, on Orchestrator, Observability and Presentation",
    "Freshworks Device42 on Observability",
    "EfficientIP SOLIDserver DDI on Executor",
    "System Initiative on Executor",
    "Forward Networks Forward Enterprise on Intent",
    "NetBrain Agentic NetOps Platform on Intent",
    "Infoblox NIOS: the whole product, on Collector and Intent (2026-10-28)",
    "phpIPAM: the whole product, on Collector and Intent (2026-10-28)",
]

# Verdicts the user kept as researched after review (claim, requirement). Verdicts the user changed
# are in adjustments.json. Both are left out of "worth a look".
KEPT_BY_USER = [
    ("Cisco pyATS - Collector", "collector-must-1"),
    ("FireMon Security Manager - Collector", "collector-must-1"),
    ("IP Fabric IP Fabric - Collector", "collector-must-1"),
    ("Nokia Event-Driven Automation (EDA) - Observability", "observability-must-1"),
    ("SolarWinds Network Performance Monitor - Observability", "observability-should-2"),
    ("Stardust Systems SuzieQ - Observability", "observability-should-2"),
    ("Temporal Technologies Temporal - Orchestrator", "orchestrator-should-3"),
    ("Paessler PRTG Network Monitor - Collector", "collector-should-1"),
]

# Verdicts the research agents flagged as resting on weaker evidence (product, requirement).
WEAK = [
    ("Forward Networks Forward Enterprise", "framework-should-1", "The only source is a vendor statement that its API can be used in Jenkins pipelines."),
    ("Infoblox NIOS", "framework-should-2", "The API returns its own schema; no OpenAPI file was found."),
    ("Juniper Networks Apstra Data Center Director", "framework-should-2", "Rests on the REST API explorer page and a lab guide, not the user guide."),
    ("Gluware Gluware", "framework-should-1", "The only source is a news article quoting the company."),
    ("ServiceNow IT Service Management", "framework-should-2", "The source is a community forum post."),
    ("System Initiative System Initiative", "framework-should-2", "The documentation site no longer loads; the source is its API client package page."),
]


def focus(requirements: list[dict], verdicts: list[dict], review: list[dict]) -> list[dict]:
    """The verdicts worth a person's review, each with the reason."""
    counts = {r["identifier"]: r["level"] != "may" and r["block"] is not None for r in requirements}
    items, seen = [], set()

    def add(verdict: dict, group: str, why: str) -> None:
        key = (verdict["claim"], verdict["requirement"])
        if key not in seen:
            seen.add(key)
            items.append({"claim": verdict["claim"], "requirement": verdict["requirement"], "group": group, "why": why})

    for claim in review:
        if claim["after"] == "full":
            continue
        blocking = [v for v in verdicts if v["claim"] == claim["claim"] and counts[v["requirement"]] and v["verdict"] != "met"]
        if len(blocking) == 1:
            add(blocking[0], "decides", "The only MUST or SHOULD that keeps this claim from full. If it is wrong, the line becomes solid.")
    for product, requirement, why in WEAK:
        match = next((v for v in verdicts if v["product"] == product and v["requirement"] == requirement), None)
        if match:
            add(match, "weak", why)
    for verdict in verdicts:
        if any("illinois.edu" in s["url"] for s in verdict.get("sources", [])):
            add(verdict, "weak", "The source is a university-hosted copy of the vendor's API documentation.")
        if verdict["verdict"] == "not_met":
            add(verdict, "not_met", "One of the 3 verdicts that say the product does not do it.")
        if verdict["product"] == "OpsMill Infrahub":
            add(verdict, "own", "OpsMill's own product: worth checking that it got the same evidence bar as the others.")
    return items


TEMPLATE = r"""<title>Framework Verdict Review</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root {
  --ground: #f4f5f7; --panel: #ffffff; --ink: #18202c; --muted: #5a6475; --line: #dde1e8; --accent: #2b55c7;
  --met: #1d7f53; --partly: #a86a12; --notmet: #b93a32; --notshown: #7b8494;
  --met-bg: #e3f3eb; --partly-bg: #fbefd9; --notmet-bg: #f9e2e0; --notshown-bg: #eceef2;
  --intent: #e8670f; --executor: #5458e0; --collector: #e03357; --observability: #1f9d4f; --orchestrator: #0796b0; --presentation: #c99a06;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --ground: #0f131a; --panel: #171d27; --ink: #e7ebf1; --muted: #98a2b3; --line: #2a3342; --accent: #8fb0ff;
    --met: #4fd197; --partly: #f2b84b; --notmet: #f07a70; --notshown: #9aa3b2;
    --met-bg: #12372a; --partly-bg: #3a2c10; --notmet-bg: #3d1a18; --notshown-bg: #232a36;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --ground: #0f131a; --panel: #171d27; --ink: #e7ebf1; --muted: #98a2b3; --line: #2a3342; --accent: #8fb0ff;
  --met: #4fd197; --partly: #f2b84b; --notmet: #f07a70; --notshown: #9aa3b2;
  --met-bg: #12372a; --partly-bg: #3a2c10; --notmet-bg: #3d1a18; --notshown-bg: #232a36;
}
body { background: var(--ground); color: var(--ink); font: 15px/1.5 "IBM Plex Sans", system-ui, sans-serif; }
.wrap { max-width: 1100px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 64px; }
h1, h2 { font-family: "IBM Plex Sans Condensed", "IBM Plex Sans", system-ui, sans-serif; text-wrap: balance; }
h1 { font-size: 1.9rem; margin: 0 0 6px; }
.lede { color: var(--muted); max-width: 70ch; margin: 0 0 20px; }
code, .mono { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 0.86em; }
.stats { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.stat { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; min-width: 130px; }
.stat b { display: block; font: 600 1.4rem/1.2 "IBM Plex Sans Condensed", sans-serif; font-variant-numeric: tabular-nums; }
.stat span { color: var(--muted); font-size: 0.8rem; }
.rule { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; margin-bottom: 18px; font-size: 0.9rem; }
.controls { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; margin-bottom: 14px; position: sticky; top: env(safe-area-inset-top, 0px); background: var(--ground); padding-block: 8px; z-index: 2; }
.controls label { font-size: 0.8rem; color: var(--muted); display: flex; gap: 6px; align-items: center; }
select, input[type="search"] { font: inherit; font-size: 0.85rem; padding: 4px 8px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); color: var(--ink); }
.claim { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--block); border-radius: 8px; margin-bottom: 8px; }
.claim > summary { list-style: none; cursor: pointer; display: grid; grid-template-columns: 1fr auto; gap: 4px 12px; padding: 10px 14px; align-items: center; }
.claim > summary::-webkit-details-marker { display: none; }
.claim > summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.claim-name { font-weight: 600; }
.claim-block { color: var(--block); font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.change { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; white-space: nowrap; }
.ext { padding: 1px 8px; border-radius: 999px; font-weight: 600; border: 1px solid var(--line); }
.ext-full { color: var(--met); border-color: var(--met); }
.ext-partial { color: var(--muted); }
.ext-changed { box-shadow: 0 0 0 2px var(--partly-bg); }
.tally { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 4px; }
.pip { font-size: 0.72rem; padding: 0 6px; border-radius: 4px; font-variant-numeric: tabular-nums; }
.table-wrap { overflow-x: auto; border-top: 1px solid var(--line); }
table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
td, th { text-align: left; vertical-align: top; padding: 8px 14px; border-bottom: 1px solid var(--line); }
th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 600; }
tr:last-child td { border-bottom: none; }
.lvl { font: 600 0.7rem "IBM Plex Mono", monospace; color: var(--muted); }
.lvl-must { color: var(--ink); }
.v { display: inline-block; padding: 1px 8px; border-radius: 999px; font-weight: 600; font-size: 0.75rem; white-space: nowrap; }
.v-met { color: var(--met); background: var(--met-bg); }
.v-partly_met { color: var(--partly); background: var(--partly-bg); }
.v-not_met { color: var(--notmet); background: var(--notmet-bg); }
.v-not_shown { color: var(--notshown); background: var(--notshown-bg); }
.req-sum { font-weight: 500; }
.req-id { color: var(--muted); white-space: nowrap; }
.note { color: var(--ink); max-width: 60ch; }
.src a { color: var(--accent); font-size: 0.8rem; word-break: break-word; }
.empty { color: var(--muted); padding: 20px 0; }
h2 { font-size: 1.3rem; margin: 28px 0 4px; }
.section-lede { color: var(--muted); margin: 0 0 12px; max-width: 70ch; }
.cards { display: grid; gap: 8px; }
.card { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--block); border-radius: 8px; padding: 10px 14px; display: grid; gap: 4px; }
.card-top { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: baseline; justify-content: space-between; }
.rec { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 1px 8px; border-radius: 999px; }
.rec-remove { color: var(--notmet); background: var(--notmet-bg); }
.rec-keep { color: var(--met); background: var(--met-bg); }
.why { color: var(--muted); font-size: 0.85rem; }
.group-title { font: 600 0.8rem "IBM Plex Sans", sans-serif; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 16px 0 6px; }
.all-head { margin-top: 36px; }
.decided-box { margin-top: 20px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; }
.decided-box summary { cursor: pointer; font-weight: 600; }
.decided-box li { font-size: 0.85rem; margin: 2px 0; }
@media (max-width: 640px) { td, th { padding: 6px 8px; } .claim > summary { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto; } }
</style>
<div class="wrap">
  <h1>Framework requirement verdicts</h1>
  <p class="lede">Proposed verdicts for every coverage claim in the Network Automation Product Catalog, against the MUST, SHOULD and MAY requirements of the Network Automation Framework. Nothing is loaded until approved.</p>
  <div class="stats" id="stats"></div>
  <div class="rule">A claim is <b>full</b> only when every MUST and SHOULD requirement of its block is <b>met</b>. The two framework-wide SHOULD requirements are shown but do not count. Partly met, not met and not shown by any source all count against full. MAY requirements are shown but do not change the extent. The Executor and Collector MUSTs use your looser reading: at least one of the listed write interfaces, and live reads plus at least one kind of metrics, logs, flows, packets or traces.</div>
  <h2>Removed on your decision</h2>
  <ul class="section-lede" id="removed"></ul>
  <h2>Verdicts worth a look</h2>
  <p class="section-lede">The verdicts that are questionable to me, grouped by reason. Everything else follows from sources the research opened and is listed in full below.</p>
  <div id="focus"></div>
  <details class="decided-box">
    <summary id="decided-summary">Already decided by you</summary>
    <ul id="decided"></ul>
  </details>
  <h2 class="all-head">All verdicts</h2>
  <div class="controls">
    <label for="f-block">Block <select id="f-block"><option value="">All</option></select></label>
    <label for="f-change">Change <select id="f-change"><option value="">All claims</option><option value="down">Full → partial</option><option value="up">Partial → full</option><option value="same">Unchanged</option></select></label>
    <label for="f-verdict">Has verdict <select id="f-verdict"><option value="">Any</option><option value="not_met">Not met</option><option value="partly_met">Partly met</option><option value="not_shown">Not shown</option></select></label>
    <label for="f-text">Product <input type="search" id="f-text" placeholder="NetBox, Infrahub…"></label>
  </div>
  <div id="list"></div>
</div>
<script>
const DATA = __DATA__;
const LABEL = { met: "Met", partly_met: "Partly met", not_met: "Not met", not_shown: "Not shown" };
const BLOCKS = ["Presentation", "Observability", "Orchestrator", "Intent", "Collector", "Executor"];
const reqs = new Map(DATA.requirements.map(r => [r.identifier, r]));
const byClaim = new Map();
for (const v of DATA.verdicts) { if (!byClaim.has(v.claim)) byClaim.set(v.claim, []); byClaim.get(v.claim).push(v); }
for (const list of byClaim.values()) list.sort((a, b) => order(a) - order(b));
function order(v) { const r = reqs.get(v.requirement); const rank = { must: 0, should: 1, may: 2 }[r.level]; const short = r.level !== "may" && v.verdict !== "met" ? 0 : 1; return short * 1000 + rank * 100 + r.position; }
function el(tag, attrs = {}, ...kids) { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "style") e.setAttribute("style", v); else e.setAttribute(k, v); } for (const k of kids) e.append(k); return e; }
const blockSel = document.getElementById("f-block");
for (const b of BLOCKS) blockSel.append(el("option", { value: b }, b));
function stats() {
  const c = DATA.claims; const n = (f) => c.filter(f).length;
  const counts = {}; for (const v of DATA.verdicts) counts[v.verdict] = (counts[v.verdict] || 0) + 1;
  const box = document.getElementById("stats");
  const add = (num, text) => box.append(el("div", { class: "stat" }, el("b", {}, String(num)), el("span", {}, text)));
  add(c.length, "coverage claims");
  add(`${n(x => x.before === "full")} → ${n(x => x.after === "full")}`, "full claims, before → after");
  add(n(x => x.before === "full" && x.after === "partial"), "full claims becoming partial");
  add(DATA.verdicts.length, "verdicts");
  for (const k of ["met", "partly_met", "not_met", "not_shown"]) add(counts[k] || 0, LABEL[k].toLowerCase());
}
function render() {
  const block = blockSel.value, change = document.getElementById("f-change").value, verdict = document.getElementById("f-verdict").value;
  const text = document.getElementById("f-text").value.trim().toLowerCase();
  const list = document.getElementById("list"); list.replaceChildren();
  const claims = DATA.claims.filter(c => (!block || c.block === block)
    && (!text || c.product.toLowerCase().includes(text))
    && (!change || (change === "down" ? c.before === "full" && c.after === "partial" : change === "up" ? c.before === "partial" && c.after === "full" : c.before === c.after))
    && (!verdict || (byClaim.get(c.claim) || []).some(v => v.verdict === verdict)))
    .sort((a, b) => BLOCKS.indexOf(a.block) - BLOCKS.indexOf(b.block) || a.product.localeCompare(b.product));
  if (!claims.length) { list.append(el("p", { class: "empty" }, "No claims match these filters.")); return; }
  for (const c of claims) {
    const vs = byClaim.get(c.claim) || [];
    const tally = el("div", { class: "tally" });
    const counts = {}; for (const v of vs) { const r = reqs.get(v.requirement); if (r.level !== "may" && r.block !== null) counts[v.verdict] = (counts[v.verdict] || 0) + 1; }
    for (const k of ["met", "partly_met", "not_met", "not_shown"]) if (counts[k]) tally.append(el("span", { class: `pip v-${k}` }, `${counts[k]} ${LABEL[k].toLowerCase()}`));
    tally.append(el("span", { class: "pip", style: "color: var(--muted)" }, `MUST and SHOULD of ${c.block}`));
    const changed = c.before !== c.after ? " ext-changed" : "";
    const summary = el("summary", {},
      el("div", {}, el("div", { class: "claim-block" }, c.block), el("div", { class: "claim-name" }, c.product)),
      el("div", { class: "change" }, el("span", { class: `ext ext-${c.before}` }, c.before), "→", el("span", { class: `ext ext-${c.after}${changed}` }, c.after)),
      tally);
    const tbody = el("tbody");
    for (const v of vs) {
      const r = reqs.get(v.requirement);
      const src = el("td", { class: "src" });
      v.sources.forEach((s, i) => { if (i) src.append(el("br")); src.append(el("a", { href: s.url, target: "_blank", rel: "noopener noreferrer" }, s.title || s.url)); });
      tbody.append(el("tr", {},
        el("td", {}, el("div", { class: `lvl lvl-${r.level}` }, r.level.toUpperCase()), el("div", { class: "req-id mono" }, r.identifier),
          r.block === null ? el("div", { class: "req-id" }, "framework-wide, not counted") : ""),
        el("td", {}, el("div", { class: "req-sum", title: r.statement }, r.summary)),
        el("td", {}, el("span", { class: `v v-${v.verdict}` }, LABEL[v.verdict])),
        el("td", { class: "note" }, v.note), src));
    }
    const table = el("table", {}, el("thead", {}, el("tr", {}, ...["Level", "Requirement", "Verdict", "Note", "Sources"].map(h => el("th", {}, h)))), tbody);
    const details = el("details", { class: "claim", style: `--block: var(--${c.block.toLowerCase()})` }, summary, el("div", { class: "table-wrap" }, table));
    list.append(details);
  }
}
for (const id of ["f-block", "f-change", "f-verdict", "f-text"]) document.getElementById(id).addEventListener("input", render);
function decidedSection() {
  document.getElementById("decided-summary").textContent = `Already decided by you (${DATA.decided.length})`;
  const ul = document.getElementById("decided");
  for (const d of DATA.decided) {
    const v = DATA.verdicts.find(x => x.claim === d.claim && x.requirement === d.requirement);
    ul.append(el("li", {}, `${d.claim} · ${reqs.get(d.requirement).summary}: ${LABEL[v.verdict]} (${d.how})`));
  }
}
function focusSections() {
  for (const text of DATA.removed) document.getElementById("removed").append(el("li", {}, text));
  const q = document.getElementById("questioned");
  for (const item of (q ? DATA.questioned : [])) {
    const claim = DATA.claims.find(c => c.claim === item.claim);
    q.append(el("div", { class: "card", style: `--block: var(--${claim.block.toLowerCase()})` },
      el("div", { class: "card-top" }, el("div", {}, el("div", { class: "claim-block" }, claim.block), el("div", { class: "claim-name" }, claim.product)),
        el("span", { class: `rec rec-${item.recommend}` }, `Recommend: ${item.recommend}`)),
      el("div", { class: "why" }, item.why)));
  }
  const groups = { decides: "One verdict decides solid or dashed", weak: "Weaker evidence", not_met: "Not met", own: "OpsMill Infrahub" };
  const box = document.getElementById("focus");
  for (const [key, title] of Object.entries(groups)) {
    const items = DATA.focus.filter(f => f.group === key);
    if (!items.length) continue;
    box.append(el("div", { class: "group-title" }, `${title} (${items.length})`));
    const cards = el("div", { class: "cards" });
    for (const f of items) {
      const v = DATA.verdicts.find(x => x.claim === f.claim && x.requirement === f.requirement);
      const r = reqs.get(f.requirement); const claim = DATA.claims.find(c => c.claim === f.claim);
      const src = el("div", { class: "src" });
      v.sources.forEach((s, i) => { if (i) src.append(" · "); src.append(el("a", { href: s.url, target: "_blank", rel: "noopener noreferrer" }, s.title || s.url)); });
      cards.append(el("div", { class: "card", style: `--block: var(--${claim.block.toLowerCase()})` },
        el("div", { class: "card-top" },
          el("div", {}, el("div", { class: "claim-block" }, `${claim.block} · ${claim.product}`), el("div", { class: "req-sum", title: r.statement }, `${r.level.toUpperCase()} · ${r.summary}`)),
          el("span", { class: `v v-${v.verdict}` }, LABEL[v.verdict])),
        v.note ? el("div", { class: "note" }, v.note) : "", src,
        el("div", { class: "why" }, f.why)));
    }
    box.append(cards);
  }
}
stats(); focusSections(); decidedSection(); render();
</script>
"""

if __name__ == "__main__":
    main()
