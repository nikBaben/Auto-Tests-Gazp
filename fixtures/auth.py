"""Фикстуры авторизации тестовой сессии."""
import pytest

from config.settings import BASE_URL, DEFAULT_USER_INDEX
from pages.login_page import LoginPage


@pytest.fixture(scope="session", autouse=True)
def authorized_session(driver, wait):
    """Авторизует браузерную сессию перед запуском тестов."""
    LoginPage(driver, wait, BASE_URL).open().login_as_user(DEFAULT_USER_INDEX)
