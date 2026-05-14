"""Тесты фильтров для страницы ip-subcompany/prw/monthly-planning."""
import re
from typing import Callable

import pytest

from checks.filtering import assert_values_contain_substring
from checks.sorting import (
    assert_special_values_at_end,
    assert_sorted_by_leading_number,
    assert_sorted_ip_versions,
    assert_sorted_regions_by_name,
)
from checks.utils import (
    partial_filter_code_search_value,
    partial_filter_name_search_value,
)
from fixtures.reports import CsvReport
from pages.ip_subcompany.prw.prw_monthly_planning_page import (
    PrwMonthlyPlanningFilterTitle,
    PrwMonthlyPlanningPage,
)
from tests.ip_subcompany.prw.monthly_planning.config import ( 
    CASE_INSENSITIVE_SEARCH_CASES,
    SUBCOMPANY_CODE_SEARCH_PART_LENGTH,
    SUBCOMPANY_NAME_SEARCH_PART_LENGTH,
    REGION_NAME_SEARCH_PART_LENGTH,
    STAGE_YEAR_SEARCH_PART_LENGTH,
    STAGE_NAME_SEARCH_PART_LENGTH
)


def test_prw_monthly_planning_subcompany_sorted(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что значения в фильтре 'Код заказчика'
    отсортированы по возрастанию в нумерном порядке,
    а также, специальные значения находятся в конце списка и отсортированы.

    Пример отсортированного списка:
        001 | ГД Астрахань
        002 | ГТ Уфа
        003 | ГТ Беларусь
        ARM | Армения
        KZT | Казахстан
        Не указан
        Не указано 
        Не представлялась
        Пустое значение
    """
    options = prw_monthly_planning_page.subcompany_options()
    errors = []

    for check in (
        assert_special_values_at_end,
        assert_sorted_by_leading_number,
    ):
        try:
            check(
                element=PrwMonthlyPlanningFilterTitle.SUBCOMPANY,
                values=options,
                report=test_report,
            )
        except AssertionError as error:
            errors.append(str(error))

    assert not errors, "\n\n".join(errors)


def test_prw_monthly_planning_region_sorted_by_name(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что значения в фильтре 'Регион'
    отсртированы по возрастанию в алфавитном порядке
    по названию региона без учета типа региона, 
    а также, специальные значения находятся в конце списка и отсортированы.

    Пример отсортированного списка:
        Республика Адыгея 
        Республика Бурятия 
        Республика Дагестан 
    """
    options = prw_monthly_planning_page.region_options()

    assert_sorted_regions_by_name(
        element=PrwMonthlyPlanningFilterTitle.REGION,
        values=options,
        report=test_report,
    )

def test_prw_monthly_planning_stage_sorted(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что значения в фильтре 'Версия ИП' 
    отсортированы по возрастанию в нумерном порядке
    бакетами: диапазон лет, уточн., кварт., полуг.
    а также, специальные значения находятся в конце списка и отсортированы.

    Пример отсортированного списка:
        2023-2027
        2023 уточн.
        2023 кварт.
        2023 полуг.
        2024-2028.
    """
    options = prw_monthly_planning_page.stage_options()

    assert_sorted_ip_versions(
        element=PrwMonthlyPlanningFilterTitle.IP_VERSION,
        values=options,
        report=test_report,
    )


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_monthly_planning_region_searches_by_partial_name_ignore_case(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск в фильтре 'Регион' 
    работает при вводе части названия,
    игнорируя регистр.
    """
    entered_value = region_name_search_value(
        options=prw_monthly_planning_page.region_options(),
        case_transform=case_transform,
    )
    options = prw_monthly_planning_page.region_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwMonthlyPlanningFilterTitle.REGION,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )


def test_prw_monthly_planning_stage_searches_by_partial_year(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что поиск в фильтре 'Версия ИП' 
    работает при вводе части года.
    """
    entered_value = stage_year_search_value(
        prw_monthly_planning_page.stage_options()
    )
    options = prw_monthly_planning_page.stage_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwMonthlyPlanningFilterTitle.IP_VERSION,
        entered_value=entered_value,
        values=options,
        report=test_report,
    )


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_monthly_planning_stage_searches_by_partial_name_ignore_case(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск в фильтре 'Версия ИП' 
    работает при вводе части названия,
    игнорируя регистр.
    """
    entered_value = stage_name_search_value(
        options=prw_monthly_planning_page.stage_options(),
        case_transform=case_transform,
    )
    options = prw_monthly_planning_page.stage_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwMonthlyPlanningFilterTitle.IP_VERSION,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )


def test_prw_monthly_planning_subcompany_searches_by_partial_code(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что поиск в фильтре 'Код заказчика'
    работает при вводе части кода.
    """
    entered_value = partial_filter_code_search_value(
        options=prw_monthly_planning_page.subcompany_options(),
        part_length=SUBCOMPANY_CODE_SEARCH_PART_LENGTH,
    )
    options = prw_monthly_planning_page.subcompany_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwMonthlyPlanningFilterTitle.SUBCOMPANY,
        entered_value=entered_value,
        values=options,
        report=test_report,
    )


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_monthly_planning_subcompany_searches_by_partial_name_ignore_case(
    prw_monthly_planning_page: PrwMonthlyPlanningPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск в фильтре 'Код заказчика' 
    работает при вводе части названия,
    игнорируя регистр.
    """
    entered_value = partial_filter_name_search_value(
        options=prw_monthly_planning_page.subcompany_options(),
        part_length=SUBCOMPANY_NAME_SEARCH_PART_LENGTH,
        case_transform=case_transform,
    )
    options = prw_monthly_planning_page.subcompany_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwMonthlyPlanningFilterTitle.SUBCOMPANY,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )


def region_name_search_value(
    options: list[str],
    case_transform: Callable[[str], str],
) -> str:
    """Возвращает часть названия региона для проверки поиска."""
    return case_transform(base_region_name_search_value(options))


def base_region_name_search_value(options: list[str]) -> str:
    """Возвращает базовый фрагмент названия региона без изменения регистра."""
    for option in options:
        words = re.findall(r"[А-Яа-яЁё]+", option)

        for word in words:
            if len(word) >= REGION_NAME_SEARCH_PART_LENGTH:
                return word[:REGION_NAME_SEARCH_PART_LENGTH]

    raise AssertionError(
        "Не найден регион, из которого можно взять часть названия для поиска.\n"
        f"Значения: {options}"
    )


def stage_year_search_value(options: list[str]) -> str:
    """Возвращает часть года из значения версии ИП."""
    for option in options:
        year = re.search(r"\d{4}", option)

        if year:
            return year.group(0)[-STAGE_YEAR_SEARCH_PART_LENGTH:]

    raise AssertionError(
        "Не найдена версия ИП, из которой можно взять часть года для поиска.\n"
        f"Значения: {options}"
    )


def stage_name_search_value(
    options: list[str],
    case_transform: Callable[[str], str],
) -> str:
    """Возвращает часть названия версии ИП для проверки поиска."""
    return case_transform(base_stage_name_search_value(options))


def base_stage_name_search_value(options: list[str]) -> str:
    """Возвращает базовый фрагмент названия версии ИП без изменения регистра."""
    for option in options:
        words = re.findall(r"[А-Яа-яЁё]+", option)

        for word in words:
            if len(word) >= STAGE_NAME_SEARCH_PART_LENGTH:
                return word[:STAGE_NAME_SEARCH_PART_LENGTH]

    raise AssertionError(
        "Не найдена версия ИП, из которой можно взять часть названия "
        "для поиска.\n"
        f"Значения: {options}"
    )
