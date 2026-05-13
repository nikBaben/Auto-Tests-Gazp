"""Тесты для страницы ip-subcompany/prw/planning-list."""
from collections.abc import Callable

import pytest

from planning_list.config import (
    NON_NEGATIVE_INTEGER_ERROR,
    CASE_INSENSITIVE_SEARCH_CASES, 
    PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH, 
    CURATOR_SEARCH_PART_LENGTH, 
    SUBCOMPANY_NAME_SEARCH_PART_LENGTH,
)
from checks.filtering import assert_values_contain_substring
from checks.input_validation import assert_shows_validation_error
from checks.sorting import (
    assert_special_values_at_end,
    assert_sorted_alphabetically,
    assert_sorted_by_leading_number,
)
from checks.utils import (
    partial_filter_search_value,
    partial_filter_code_search_value,
    partial_filter_name_search_value,
)
from fixtures.reports import CsvReport
from pages.ip_subcompany.prw import (
    PrwPlanningListFilterTitle,
    PrwPlanningListPage,
)


def test_prw_planning_list_object_code_prw_shows_error_for_text(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что при вводе текста в поле фильтра 'Код ПИР'
    отображается ошибка валидации.
    """
    entered_value = "Код ПИР"

    prw_planning_list_page.fill_object_prw_code(entered_value)
    field_value = prw_planning_list_page.object_prw_code_value()
    actual_error = prw_planning_list_page.object_prw_code_error()

    assert_shows_validation_error(
        element=PrwPlanningListFilterTitle.OBJECT_PRW_CODE,
        entered_value=entered_value,
        field_value=field_value,
        expected_error=NON_NEGATIVE_INTEGER_ERROR,
        actual_error=actual_error,
        report=test_report,
    )


def test_prw_planning_list_curator_projector_sorted(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что в фильтре 'Куратор проектировщика' 
    значения отсортированы по алфавиту.
    """
    options = prw_planning_list_page.projector_curator_options()
    errors = []

    for check in (
        assert_special_values_at_end,
        assert_sorted_alphabetically,
    ):
        try:
            check(
                element=PrwPlanningListFilterTitle.PROJECTOR_CURATOR,
                values=options,
                report=test_report,
            )
        except AssertionError as error:
            errors.append(str(error))

    assert not errors, "\n\n".join(errors)


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_planning_list_curator_projector_searches_by_partial_value_ignore_case(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск в фильтре 'Куратор проектировщика'
    работает при вводе части имени куратора,
    игнорируя регистр.

    Для проверки используется существующий куратор,
    у которого берется часть имени.
    """
    entered_value = partial_filter_search_value(
        options=prw_planning_list_page.projector_curator_options(),
        part_length = CURATOR_SEARCH_PART_LENGTH,
        case_transform=case_transform,
    )
    options = prw_planning_list_page.projector_curator_options_by_search(
        entered_value
    )

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.PROJECTOR_CURATOR,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )


def test_prw_planning_list_curator_planning_sorted(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """
    Тест проверяет, что в фильтре 'Куратор планирования' 
    значения отсортированы по алфавиту.
    """
    options = prw_planning_list_page.planning_curator_options()

    errors = []

    for check in (
        assert_special_values_at_end,
        assert_sorted_alphabetically,
    ):
        try:
            check(
                element=PrwPlanningListFilterTitle.PLANNING_CURATOR,
                values=options,
                report=test_report,
            )
        except AssertionError as error:
            errors.append(str(error))

    assert not errors, "\n\n".join(errors)


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_planning_list_curator_planning_searches_by_partial_value_ignore_case(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск в фильтру 'Куратор планирования'
    работает при вводе части имени куратора,
    игнорируя регистр.

    Для проверки используется существующий куратор,
    у которого берется часть имени.
    """
    entered_value = partial_filter_search_value(
        options=prw_planning_list_page.planning_curator_options(),
        part_length= CURATOR_SEARCH_PART_LENGTH,
        case_transform=case_transform,
    )
    options = prw_planning_list_page.planning_curator_options_by_search(
        entered_value
    )

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.PLANNING_CURATOR,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )


def test_prw_planning_list_subcompany_sorted(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """Тест проверяет, что в фильтре 'ДО' значения отсортированы по возрастанию."""
    options = prw_planning_list_page.subcompany_options()
    errors = []

    for check in (
        assert_special_values_at_end,
        assert_sorted_by_leading_number,
    ):
        try:
            check(
                element=PrwPlanningListFilterTitle.SUBCOMPANY,
                values=options,
                report=test_report,
            )
        except AssertionError as error:
            errors.append(str(error))

    assert not errors, "\n\n".join(errors)


def test_prw_planning_list_subcompany_searches_by_partial_code(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """Тест проверяет, что поиск в фильтре 'ДО' работает при вводе части кода."""
    entered_value = partial_filter_code_search_value(
        options = prw_planning_list_page.subcompany_options(),
        part_length = SUBCOMPANY_CODE_SEARCH_PART_LENGTH
    )
    options = prw_planning_list_page.subcompany_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.SUBCOMPANY,
        entered_value=entered_value,
        values=options,
        report=test_report,
    )


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_planning_list_subcompany_searches_by_partial_name_ignore_case(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск по фильтру 'ДО' работает при вводе части названия,
    игнорируя регистр.
    """
    entered_value = partial_filter_name_search_value(
        options = prw_planning_list_page.subcompany_options(),
        part_length = SUBCOMPANY_NAME_SEARCH_PART_LENGTH,
        case_transform = case_transform
    )
    options = prw_planning_list_page.subcompany_options_by_search(entered_value)

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.SUBCOMPANY,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )


def test_prw_planning_list_projection_doc_status_sorted(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
):
    """Тест проверяет, что фильтр 'Статус ДП' отсортирован корректно"""
    options = prw_planning_list_page.projection_doc_status_options()
    errors = []

    for check in (
        assert_special_values_at_end,
        assert_sorted_alphabetically,
    ):
        try:
            check(
                element=PrwPlanningListFilterTitle.PROJECTION_DOC_STATUS,
                values=options,
                report=test_report,
            )
        except AssertionError as error:
            errors.append(str(error))

    assert not errors, "\n\n".join(errors)


@pytest.mark.parametrize("case_transform", CASE_INSENSITIVE_SEARCH_CASES)
def test_prw_projection_doc_status_searches_by_partial_value_ignore_case(
    prw_planning_list_page: PrwPlanningListPage,
    test_report: CsvReport,
    case_transform: Callable[[str], str],
):
    """
    Тест проверяет, что поиск по филтру 'Статус ПД' работает при вводе части
    значения, игнорируя регистр.
    """
    entered_value = partial_filter_search_value(
        options=prw_planning_list_page.projection_doc_status_options(),
        part_length = PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH,
        case_transform=case_transform,
    )
    options = prw_planning_list_page.projection_doc_status_options_by_search(
        entered_value
    )

    assert_values_contain_substring(
        element=PrwPlanningListFilterTitle.PROJECTION_DOC_STATUS,
        entered_value=entered_value,
        values=options,
        report=test_report,
        ignore_case=True,
    )