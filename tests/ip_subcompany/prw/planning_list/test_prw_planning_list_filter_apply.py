"""Тесты применения фильтров на странице ip-subcompany/prw/planning-list."""
from collections.abc import Callable

import pytest

from tests.ip_subcompany.prw.planning_list.config import (
    OBJECT_PRW_CODE_SEARCH_PART_LENGTH,
    TITLE_SEARCH_PART_LENGTH,
    CASE_INSENSITIVE_SEARCH_CASES,
)
from checks.filtering import (
    assert_filter_values_match,
    assert_values_contain_substring,
)
from fixtures.reports import CsvReport
from pages.ip_subcompany.prw import (
    PrwPlanningListFilterTitle,
    PrwPlanningListPage,
)
from checks.utils import (
    first_non_empty,
    first_non_empty_or_none,
    matching_option_text,
    matching_person_option,
    matching_subcompany_option,
    partial_filter_search_value,
)
from utils.value_matchers import (
    normalized_text,
    normalized_text_key,
    person_key,
    same_option_text,
)


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
    entered_value = partial_filter_search_value(
        options=prw_planning_list_page.wait_titles(),
        part_length=TITLE_SEARCH_PART_LENGTH,
        case_transform=str.lower,
    )

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

    return matching_option_text(
        options=options,
        table_value=status_from_table,
        option_name="Статус ПД",
    )


def test_prw_planning_list_object_code_prw_searches_by_partial_value(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что поиск по фильтру 'Код ПИР'
    работает при вводе части кода.

    Для проверки используется существующий 'Код ПИР',
    у которого берется часть в конце.
    """
    existing_code = prw_planning_list_page.wait_object_prw_codes()[0]
    entered_value = existing_code[-OBJECT_PRW_CODE_SEARCH_PART_LENGTH:]

    values = prw_planning_list_page.search_by_object_prw_code(entered_value)

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.OBJECT_PRW_CODE,
        entered_value=entered_value,
        values=values,
        report=test_report,
    )


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_planning_list_title_searches_by_partial_value_ignore_case(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск по фильтру 'Наименование объекта'
    работает при вводе части названия, игнорируя регистр.
    """
    entered_value = partial_filter_search_value(
        options=prw_planning_list_page.wait_titles(),
        part_length=TITLE_SEARCH_PART_LENGTH,
        case_transform=case_transform,
    )

    values = prw_planning_list_page.search_by_title(entered_value)

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.TITLE,
        entered_value=entered_value,
        values=values,
        report=test_report,
        ignore_case=True,
    )
