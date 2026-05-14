"""Тесты применения фильтров на странице ip-subcompany/prw/monthly-planning."""
import pytest

from checks.filtering import (
    assert_filter_values_match,
    assert_values_contain_substring,
)
from checks.utils import (
    first_non_empty,
    first_non_empty_or_none,
    matching_option_text,
    matching_subcompany_option,
)
from fixtures.reports import CsvReport
from pages.ip_subcompany.prw.prw_monthly_planning_page import (
    PrwMonthlyPlanningFilterTitle,
    PrwMonthlyPlanningPage,
)
from utils.value_matchers import (
    normalized_text,
    normalized_text_key,
    same_option_text,
)


OBJECT_CODE_SEARCH_PART_LENGTH = 3


def test_prw_monthly_planning_applies_search_filter(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет применения фильтра 'Поиск'.

    Берет существующий код из таблицы, вводит его часть в фильтр
    и проверяет, что все найденные значения содержат введенный фрагмент.
    """
    existing_code = first_non_empty(prw_monthly_planning_page.wait_object_codes())
    entered_value = existing_code[-OBJECT_CODE_SEARCH_PART_LENGTH:]

    values = prw_monthly_planning_page.search_by_object_code(entered_value)

    assert_values_contain_substring(
        element=PrwMonthlyPlanningFilterTitle.SEARCH,
        entered_value=entered_value,
        values=values,
        report=test_report,
    )


def test_prw_monthly_planning_applies_subcompany_filter(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет применения фильтра 'Код заказчика'.
    
    Берет существующий код из выпадающего списка,
    вводит его часть в фильтр
    и проверяет, что все найденные значения содержат введенный фрагмент.
    """
    code = first_non_empty(prw_monthly_planning_page.wait_subcompany_codes())
    selected_option = matching_subcompany_option(
        options=prw_monthly_planning_page.subcompany_options(),
        code=code,
    )

    values = prw_monthly_planning_page.apply_subcompany_filter(selected_option)

    assert_filter_values_match(
        element=PrwMonthlyPlanningFilterTitle.SUBCOMPANY,
        selected_value=code,
        values=values,
        report=test_report,
        normalizer=normalized_text,
    )


def test_prw_monthly_planning_applies_region_filter(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет применения фильтра 'Регион'.
    
    Берет существующий регион из выпадающего списка,
    вводит его часть в фильтр
    и проверяет, что все найденные значения содержат введенный фрагмент.
    """
    selected_option = region_for_filter(prw_monthly_planning_page)

    values = prw_monthly_planning_page.apply_region_filter(selected_option)

    assert_filter_values_match(
        element=PrwMonthlyPlanningFilterTitle.REGION,
        selected_value=selected_option,
        values=values,
        report=test_report,
        normalizer=normalized_text_key,
        same_value=same_option_text,
    )


def test_prw_monthly_planning_applies_stage_filter(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет применения фильтра 'Версия ИП'.
    
    Берет существующий дату из выпадающего списка,
    вводит ее часть в фильтр
    и проверяет, что все найденные значения содержат введенный фрагмент.
    """
    table_value = first_non_empty(prw_monthly_planning_page.wait_stages())
    selected_option = matching_option_text(
        options=prw_monthly_planning_page.stage_options(),
        table_value=table_value,
        option_name="Версия ИП",
    )

    values = prw_monthly_planning_page.apply_stage_filter(selected_option)

    assert_filter_values_match(
        element=PrwMonthlyPlanningFilterTitle.IP_VERSION,
        selected_value=selected_option,
        values=values,
        report=test_report,
        normalizer=normalized_text_key,
        same_value=same_option_text,
    )


def region_for_filter(page: PrwMonthlyPlanningPage) -> str:
    """Возвращает option региона для проверки применения фильтра."""
    region_from_table = first_non_empty_or_none(page.wait_regions())
    options = [
        option
        for option in page.region_options()
        if normalized_text(option)
    ]

    if not region_from_table:
        pytest.skip(
            "В текущей таблице нет непустого значения 'Регион объекта', "
            "поэтому нельзя честно проверить применение фильтра."
        )

    for option in options:
        if same_option_text(region_from_table, option):
            return option

    pytest.skip(
        "В таблице найден регион, но в выпадающем списке нет "
        "соответствующей опции.\n"
        f"Регион в таблице: {region_from_table}"
    )
