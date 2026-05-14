"""Фикстуры браузера и Selenium-ожиданий."""
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import HEADLESS, SELENIUM_TIMEOUT


@pytest.fixture(scope="session")
def driver():
    """Создает Chrome WebDriver на время тестовой сессии."""
    options = webdriver.ChromeOptions()

    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    browser = webdriver.Chrome(options=options)

    if not options.arguments:
        browser.maximize_window()

    yield browser

    browser.quit()


@pytest.fixture(scope="session")
def wait(driver):
    """Создает общий WebDriverWait для тестовой сессии."""
    return WebDriverWait(driver, SELENIUM_TIMEOUT)
