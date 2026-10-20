import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from a11y.axe_scanner import SCAN_LOG, AxeScanner
from a11y.report import write_summary


def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Show the Chrome window (default is headless).",
    )


@pytest.fixture(scope="session")
def driver(request):
    options = Options()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


@pytest.fixture(scope="session")
def scanner(driver):
    return AxeScanner(driver)


def pytest_sessionfinish(session, exitstatus):
    """Write reports/accessibility-summary.md covering every page scanned."""
    if SCAN_LOG:
        write_summary(SCAN_LOG, "reports/accessibility-summary.md")
