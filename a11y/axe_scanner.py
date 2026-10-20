"""Runs axe-core (the accessibility engine from Deque) inside a Selenium browser."""
from dataclasses import dataclass
from pathlib import Path

AXE_SOURCE = (Path(__file__).resolve().parent.parent / "vendor" / "axe.min.js").read_text(
    encoding="utf-8"
)

# Standard target: WCAG 2.1 levels A and AA.
WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]
IMPACTS = ["critical", "serious", "moderate", "minor"]

# Runs in the browser. Returns a compact, JSON-safe copy of axe's results.
_RUN_AXE = """
const done = arguments[arguments.length - 1];
const options = arguments[0];
axe.run(document, options).then(function (r) {
  done({
    axeVersion: axe.version,
    url: location.href,
    title: document.title,
    violations: r.violations.map(function (v) {
      return {
        id: v.id,
        impact: v.impact,
        help: v.help,
        helpUrl: v.helpUrl,
        tags: v.tags,
        nodes: v.nodes.map(function (n) {
          return {target: n.target, html: n.html.slice(0, 200)};
        })
      };
    }),
    passes: r.passes.length,
    incomplete: r.incomplete.length
  });
}).catch(function (e) { done({error: String(e)}); });
"""

# Every scan made during the test run, used to write the summary report.
SCAN_LOG = []


@dataclass
class ScanResult:
    label: str
    url: str
    title: str
    axe_version: str
    violations: list
    passes: int
    incomplete: int

    @property
    def violation_ids(self):
        return {v["id"] for v in self.violations}

    @property
    def total_violations(self):
        return len(self.violations)

    @property
    def affected_elements(self):
        return sum(len(v["nodes"]) for v in self.violations)

    def count_by_impact(self):
        counts = {impact: 0 for impact in IMPACTS}
        for violation in self.violations:
            counts[violation["impact"]] += 1
        return counts

    def violation(self, rule_id):
        """Return the violation for a rule id, or None if that rule did not fire."""
        return next((v for v in self.violations if v["id"] == rule_id), None)


class AxeScanner:
    """Open a page, inject axe-core, and return what it found."""

    def __init__(self, driver):
        self.driver = driver
        self.driver.set_script_timeout(60)

    def scan(self, url, label=None, tags=WCAG_TAGS):
        self.driver.get(url)
        self.driver.execute_script(AXE_SOURCE)
        raw = self.driver.execute_async_script(
            _RUN_AXE, {"runOnly": {"type": "tag", "values": tags}}
        )
        if "error" in raw:
            raise RuntimeError(f"axe failed on {url}: {raw['error']}")
        result = ScanResult(
            label=label or url,
            url=raw["url"],
            title=raw["title"],
            axe_version=raw["axeVersion"],
            violations=raw["violations"],
            passes=raw["passes"],
            incomplete=raw["incomplete"],
        )
        SCAN_LOG.append(result)
        return result
