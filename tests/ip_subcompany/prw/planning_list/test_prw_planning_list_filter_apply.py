"""Тесты применения фильтров на странице ip-subcompany/prw/planning-list."""

from collections.abc import Callable

import pytest

from checks.filtering import assert_values_contain_substring
from fixtures.reports import CsvReport
from pages.ip_subcompany.prw.prw_planning_list_page import (
    PrwPlanningListFilterTitle,
    PrwPlanningListPage,
)
from utils.value_matchers import (
    normalized_text,
    normalized_text_key,
    person_key,
    same_option_text,
    subcompany_code,
)


OBJECT_PRW_CODE_SEARCH_PART_LENGTH = 3
TITLE_SEARCH_PART_LENGTH = 4


def test_prw_planning_list_applies_object_prw_code_filter(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    existing_code = first_non_empty(prw_planning_list_page.wait_object_prw_codes())
    entered_value = existing_code[-OBJECT_PRW_CODE_SEARCH_PART_LENGTH:]

    values = prw_planning_list_page.search_by_object_prw_code(entered_value)

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.OBJECT_PRW_CODE,
        entered_value=entered_value,
        values=values,
        report=test_report,
    )


def test_prw_planning_list_applies_title_filter(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    entered_value = title_search_value(prw_planning_list_page.wait_titles())

    values = prw_planning_list_page.search_by_title(entered_value)

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.TITLE,
        entered_value=entered_value,
        values=values,
        report=test_report,
        ignore_case=True,
    )


def test_prw_planning_list_applies_projector_curator_filter(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    table_value = first_non_empty(prw_planning_list_page.projector_curators())
    selected_option = matching_person_option(
        options=prw_planning_list_page.projector_curator_options(),
        table_value=table_value,
    )

    values = prw_planning_list_page.apply_projector_curator_filter(selected_option)

    assert_filter_values_match(
        element=PrwPlanningListFilterTitle.PROJECTOR_CURATOR,
        selected_value=selected_option,
        values=values,
        report=test_report,
        normalizer=person_key,
    )


def test_prw_planning_list_applies_planning_curator_filter(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    table_value = first_non_empty(prw_planning_list_page.planning_curators())
    selected_option = matching_person_option(
        options=prw_planning_list_page.planning_curator_options(),
        table_value=table_value,
    )

    values = prw_planning_list_page.apply_planning_curator_filter(selected_option)

    assert_filter_values_match(
        element=PrwPlanningListFilterTitle.PLANNING_CURATOR,
        selected_value=selected_option,
        values=values,
        report=test_report,
        normalizer=person_key,
    )


def test_prw_planning_list_applies_subcompany_filter(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    code = first_non_empty(prw_planning_list_page.subcompany_codes())
    selected_option = matching_subcompany_option(
        options=prw_planning_list_page.subcompany_options(),
        code=code,
    )

    values = prw_planning_list_page.apply_subcompany_filter(selected_option)

    assert_filter_values_match(
        element=PrwPlanningListFilterTitle.SUBCOMPANY,
        selected_value=code,
        values=values,
        report=test_report,
        normalizer=normalized_text,
    )


def test_prw_planning_list_applies_projection_doc_status_filter(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    selected_option = projection_doc_status_for_filter(prw_planning_list_page)

    values = prw_planning_list_page.apply_projection_doc_status_filter(
        selected_option
    )

    assert_filter_values_match(
        element=PrwPlanningListFilterTitle.PROJECTION_DOC_STATUS,
        selected_value=selected_option,
        values=values,
        report=test_report,
        normalizer=normalized_text_key,
        same_value=same_option_text,
    )


def assert_filter_values_match(
    *,
    element: str,
    selected_value: str,
    values: list[str],
    report: CsvReport,
    normalizer: Callable[[str], str],
    allow_empty: bool = False,
    same_value: Callable[[str, str], bool] | None = None,
) -> None:
    same_value = same_value or (
        lambda current_value, expected_value: normalizer(current_value)
        == normalizer(expected_value)
    )
    wrong_values = [
        value for value in values if not same_value(value, selected_value)
    ]

    report.add(
        element=element,
        expected=f"После нажатия 'Найти' все строки соответствуют '{selected_value}'",
        actual=values,
        message="Проверка применения фильтра к таблице",
    )

    if allow_empty and not values:
        return

    assert values, (
        "После применения фильтра не найдено ни одной строки.\n"
        f"Фильтр: {element}\n"
        f"Выбрано: {selected_value}"
    )
    assert not wrong_values, (
        "Найдены строки, которые не соответствуют выбранному фильтру.\n"
        f"Фильтр: {element}\n"
        f"Выбрано: {selected_value}\n"
        f"Некорректные значения: {wrong_values}\n"
        f"Все значения в колонке: {values}"
    )


def first_non_empty(values: list[str]) -> str:
    for value in values:
        if normalized_text(value):
            return value

    raise AssertionError(f"Не найдено непустое значение в таблице: {values}")


def title_search_value(titles: list[str]) -> str:
    for title in titles:
        for word in title.split():
            if len(word) >= TITLE_SEARCH_PART_LENGTH:
                return word[:TITLE_SEARCH_PART_LENGTH].lower()

    raise AssertionError(
        "Не найдено наименование объекта, из которого можно взять часть "
        "для применения фильтра.\n"
        f"Значения: {titles}"
    )


def matching_person_option(options: list[str], table_value: str) -> str:
    table_key = person_key(table_value)

    for option in options:
        if person_key(option) == table_key:
            return option

    raise AssertionError(
        "Не найдено значение куратора в выпадающем списке, "
        "которое соответствует значению из таблицы.\n"
        f"Значение в таблице: {table_value}\n"
        f"Опции: {options}"
    )


def matching_subcompany_option(options: list[str], code: str) -> str:
    for option in options:
        if subcompany_code(option) == code:
            return option

    raise AssertionError(
        "Не найдено ДО в выпадающем списке по коду из таблицы.\n"
        f"Код в таблице: {code}\n"
        f"Опции: {options}"
    )


def projection_doc_status_for_filter(
    page: PrwPlanningListPage,
) -> str:
    status_from_table = first_non_empty_or_none(page.projection_doc_statuses())
    options = [
        option
        for option in page.projection_doc_status_options()
        if normalized_text(option)
    ]

    if not status_from_table:
        pytest.skip(
            "В текущей таблице нет непустого значения 'Статус ПД', "
            "поэтому нельзя честно проверить применение этого фильтра."
        )

    if not options:
        raise AssertionError("В фильтре 'Статус ПД' нет доступных значений.")

    for option in options:
        if same_option_text(status_from_table, option):
            return option

    raise AssertionError(
        "В таблице найден статус ПД, но в выпадающем списке нет "
        "соответствующей опции.\n"
        f"Статус в таблице: {status_from_table}\n"
        f"Опции: {options}"
    )


def first_non_empty_or_none(values: list[str]) -> str | None:
    for value in values:
        if normalized_text(value):
            return value

    return None
