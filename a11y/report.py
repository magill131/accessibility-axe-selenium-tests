"""Writes a Markdown summary of every accessibility scan from the test run."""
from pathlib import Path

from a11y.axe_scanner import IMPACTS, WCAG_TAGS


def write_summary(scans, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Accessibility scan summary",
        "",
        f"Engine: axe-core {scans[0].axe_version}. Standard: {', '.join(WCAG_TAGS)} (WCAG 2.1 A and AA).",
        "",
        "| Page | Violations | Affected elements | Critical | Serious | Moderate | Minor |",
        "|---|---|---|---|---|---|---|",
    ]
    for scan in scans:
        by_impact = scan.count_by_impact()
        cells = " | ".join(str(by_impact[i]) for i in IMPACTS)
        lines.append(
            f"| {scan.label} | {scan.total_violations} | {scan.affected_elements} | {cells} |"
        )

    for scan in scans:
        if not scan.violations:
            continue
        lines += ["", f"## {scan.label}", "", f"`{scan.url}`", ""]
        order = sorted(scan.violations, key=lambda v: IMPACTS.index(v["impact"]))
        for v in order:
            lines.append(
                f"- **{v['id']}** ({v['impact']}): {v['help']}. "
                f"{len(v['nodes'])} element(s). [Guidance]({v['helpUrl']})"
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
