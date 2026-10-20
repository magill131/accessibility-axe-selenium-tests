"""Scans a real public site: the W3C "Before and After Demonstration".

W3C publishes the same fictional city site twice: once built with accessibility
problems ("before") and once fixed ("after"). The fixed pages should score better.
"""
import pytest

BASE_URL = "https://www.w3.org/WAI/demos/bad"
PAGES = ["home", "news", "tickets", "survey"]

pytestmark = pytest.mark.realworld


@pytest.fixture(scope="module")
def results(scanner):
    """Scan every page of both versions once."""
    scans = {}
    for version in ("before", "after"):
        for page in PAGES:
            scans[(version, page)] = scanner.scan(
                f"{BASE_URL}/{version}/{page}.html",
                label=f"W3C {version}: {page}",
            )
    return scans


@pytest.mark.parametrize("page", PAGES)
def test_fixed_page_is_no_worse_than_original(results, page):
    before = results[("before", page)]
    after = results[("after", page)]
    assert after.total_violations <= before.total_violations


def test_fixed_site_has_fewer_violations_overall(results):
    before_total = sum(results[("before", p)].total_violations for p in PAGES)
    after_total = sum(results[("after", p)].total_violations for p in PAGES)
    assert before_total > 0
    assert after_total < before_total


def test_original_site_has_serious_or_critical_violations(results):
    serious = 0
    for page in PAGES:
        counts = results[("before", page)].count_by_impact()
        serious += counts["critical"] + counts["serious"]
    assert serious > 0


def test_fixed_site_has_no_critical_violations(results):
    for page in PAGES:
        counts = results[("after", page)].count_by_impact()
        assert counts["critical"] == 0, f"{page}: {counts['critical']} critical violation(s)"
