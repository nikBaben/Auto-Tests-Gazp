"""Фикстуры Page Object для UI-тестов."""
import pytest

from config.settings import BASE_URL
from pages.base_page import BasePage
from pages import (
    PrwPlanningListPage,
    PrwMonthlyPlanningPage,
    PrwDesignAssignmentPage,
    PrwProjectsObjectsPage,
)


def open_page(page_class: type[BasePage], driver, wait):
    """Фабрика Page Object."""
    page = page_class(driver, wait, BASE_URL)
    page.open()
    return page


@pytest.fixture
def prw_planning_list_page(driver, wait):
    """Открывает страницу «План ПИР» и возвращает ее Page Object."""
    return open_page(PrwPlanningListPage, driver, wait)


@pytest.fixture
def prw_monthly_planning_page(driver, wait):
    """Открывает страницу 'Освоение ПИР ИП ДО' и возвращает ее Page Object."""
    return open_page(PrwMonthlyPlanningPage, driver, wait)


@pytest.fixture
def prw_design_assignment_page(driver, wait):
    """Открывает страницу 'Задания на проектирование' и возвращает ее Page Object."""
    return open_page(PrwDesignAssignmentPage, driver, wait)


@pytest.fixture
def prw_projects_objects_page(driver, wait):
    """Открывает страницу 'Объекты проектирования' и возвращает ее Page Object."""
    return open_page(PrwProjectsObjectsPage, driver, wait)

