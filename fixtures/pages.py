import pytest

from config.settings import BASE_URL
from pages.base_page import BasePage
from pages import (
    PrwPlanningListPage,
    PrwMonthlyPlanningPage,
    PrwDesignAssignmentPage,
    PrwProjectsObjectsPage,
    CcFiveYearsConstructionPage,
    CcMonthlyPlanningPage,
    CcAmortizationPage,
    OnnaPriorityPage,
    OnnaDetailsPage,
    LtiPlanningListPage,
    LtiMonthlyPlanningPage,
    PncaPlanningListPage,
    PncaMonthlyPlanningPage,
)


def open_page(page_class: type[BasePage], driver, wait):
    page = page_class(driver, wait, BASE_URL)
    page.open()
    return page


@pytest.fixture
def prw_planning_list_page(driver, wait):
    return open_page(PrwPlanningListPage, driver, wait)


@pytest.fixture
def prw_monthly_planning_page(driver, wait):
    return open_page(PrwMonthlyPlanningPage, driver, wait)


@pytest.fixture
def prw_design_assignment_page(driver, wait):
    return open_page(PrwDesignAssignmentPage, driver, wait)


@pytest.fixture
def prw_projects_objects_page(driver, wait):
    return open_page(PrwProjectsObjectsPage, driver, wait)


@pytest.fixture
def cc_five_years_construction_page(driver, wait):
    return open_page(CcFiveYearsConstructionPage, driver, wait)


@pytest.fixture
def cc_monthly_planning_page(driver, wait):
    return open_page(CcMonthlyPlanningPage, driver, wait)


@pytest.fixture
def cc_amortization_page(driver, wait):
    return open_page(CcAmortizationPage, driver, wait)


@pytest.fixture
def onna_priority_page(driver, wait):
    return open_page(OnnaPriorityPage, driver, wait)


@pytest.fixture
def onna_details_page(driver, wait):
    return open_page(OnnaDetailsPage, driver, wait)


@pytest.fixture
def lti_planning_list_page(driver, wait):
    return open_page(LtiPlanningListPage, driver, wait)


@pytest.fixture
def lti_monthly_planning_page(driver, wait):
    return open_page(LtiMonthlyPlanningPage, driver, wait)


@pytest.fixture
def pnca_planning_list_page(driver, wait):
    return open_page(PncaPlanningListPage, driver, wait)


@pytest.fixture
def pnca_monthly_planning_page(driver, wait):
    return open_page(PncaMonthlyPlanningPage, driver, wait)
