"""Scans two local sample pages: one built to pass, one built with known failures."""
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
ACCESSIBLE_URL = (FIXTURES / "accessible.html").as_uri()
INACCESSIBLE_URL = (FIXTURES / "inaccessible.html").as_uri()

# The failures deliberately built into fixtures/inaccessible.html, with axe's impact level.
EXPECTED_VIOLATIONS = {
    "image-alt": "critical",
    "button-name": "critical",
    "label": "critical",
    "html-has-lang": "serious",
    "document-title": "serious",
    "link-name": "serious",
    "color-contrast": "serious",
}


@pytest.fixture(scope="module")
def accessible(scanner):
    return scanner.scan(ACCESSIBLE_URL, label="Local: accessible page")


@pytest.fixture(scope="module")
def inaccessible(scanner):
    return scanner.scan(INACCESSIBLE_URL, label="Local: inaccessible page")


def test_axe_engine_runs(accessible):
    assert accessible.axe_version.startswith("4.")
    assert accessible.passes > 0


def test_accessible_page_has_no_wcag_violations(accessible):
    assert accessible.total_violations == 0, (
        f"Unexpected violations: {sorted(accessible.violation_ids)}"
    )


def test_inaccessible_page_has_violations(inaccessible):
    assert inaccessible.total_violations > 0


@pytest.mark.parametrize("rule, impact", EXPECTED_VIOLATIONS.items())
def test_inaccessible_page_flags_rule(inaccessible, rule, impact):
    violation = inaccessible.violation(rule)
    assert violation is not None, (
        f"{rule} was not reported. Found: {sorted(inaccessible.violation_ids)}"
    )
    assert violation["impact"] == impact


def test_inaccessible_page_reports_nothing_unexpected(inaccessible):
    assert inaccessible.violation_ids == set(EXPECTED_VIOLATIONS)


def test_every_violation_links_to_guidance(inaccessible):
    for violation in inaccessible.violations:
        assert violation["helpUrl"].startswith("https://dequeuniversity.com/rules/axe/")


def test_every_violation_identifies_the_failing_elements(inaccessible):
    for violation in inaccessible.violations:
        assert violation["nodes"], f"{violation['id']} has no elements"
        assert all(node["target"] for node in violation["nodes"])
