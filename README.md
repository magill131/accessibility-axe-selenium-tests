# Accessibility Testing with axe-core and Selenium

Automated accessibility (WCAG 2.1 A and AA) scans run with the axe-core engine inside Selenium and pytest. Each run writes a summary report of every issue found, and runs in CI with GitHub Actions.

[![Accessibility Tests](https://github.com/magill131/accessibility-axe-selenium-tests/actions/workflows/accessibility.yml/badge.svg)](https://github.com/magill131/accessibility-axe-selenium-tests/actions/workflows/accessibility.yml)

## What was tested

20 tests in two groups.

**1. Local sample pages (`tests/test_local_fixtures.py`, 13 tests)**

- `fixtures/accessible.html` is built to pass: it must produce zero violations.
- `fixtures/inaccessible.html` has seven deliberate failures. Each one must be detected, at the right impact level, and nothing unexpected may be reported.

| Rule | Impact | The problem built into the page |
|---|---|---|
| `image-alt` | critical | Image with no alternative text |
| `button-name` | critical | Button with no accessible name |
| `label` | critical | Text field with no label |
| `html-has-lang` | serious | No `lang` attribute on `<html>` |
| `document-title` | serious | No page `<title>` |
| `link-name` | serious | Link with no text |
| `color-contrast` | serious | Light grey text on white |

Every violation must also link to guidance and identify the failing elements.

**2. Real website (`tests/test_w3c_before_after.py`, 7 tests)**

W3C publishes the same fictional city site twice: [with accessibility problems](https://www.w3.org/WAI/demos/bad/before/home.html) and [fixed](https://www.w3.org/WAI/demos/bad/after/home.html). The suite scans the home, news, tickets and survey pages of both versions and checks that each fixed page is no worse than the original, the fixed site has fewer violations overall, the original has serious or critical issues, and the fixed site has no critical issues.

## Summary report

After every run, `reports/accessibility-summary.md` lists each page scanned with its violation counts by impact (critical, serious, moderate, minor), followed by every rule that failed, how many elements were affected, and a link to the fix guidance. In CI the same summary is shown on the job page.

## How it works

- `a11y/axe_scanner.py` opens a page with Selenium, injects axe-core, runs it against the WCAG 2.1 A and AA rules, and returns the results.
- `vendor/axe.min.js` is axe-core 4.14.0, included in the repo so runs are repeatable and do not depend on a CDN.
- `a11y/report.py` writes the Markdown summary.
- `conftest.py` starts one headless Chrome for the whole run.

To scan any page, add a test that calls `scanner.scan("https://your-site.example")`.

## Limits

Automated scans find only part of all accessibility problems. Keyboard navigation, screen reader behavior and content quality still need manual testing.

## Tools

Python, Selenium WebDriver (Chrome), axe-core, pytest, pytest-html, GitHub Actions

## How to run

Requires Python and Google Chrome.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

pytest                             # all 20 tests
pytest tests/test_local_fixtures.py   # offline tests only
pytest --headed                    # watch the browser
```

Reports are written to `reports/`: `report.html` (test results) and `accessibility-summary.md` (accessibility findings).

## CI

`.github/workflows/accessibility.yml` runs all tests on every push and pull request, shows the summary on the job page, and uploads the reports.
