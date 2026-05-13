"""Тесты для страницы ip-subcompany/prw/planning-list."""
from collections.abc import Callable

import pytest

from planning_list.config import (
    NON_NEGATIVE_INTEGER_ERROR,
    OBJECT_PRW_CODE_SEARCH_PART_LENGTH,
    TITLE_SEARCH_PART_LENGTH, 
    CURATOR_SEARCH_PART_LENGTH, 
    SUBCOMPANY_CODE_SEARCH_PART_LENGTH, 
    SUBCOMPANY_NAME_SEARCH_PART_LENGTH, 
    PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH, 
    CASE_INSENSITIVE_SEARCH_CASES
)
from checks.filtering import assert_values_contain_substring
from checks.input_validation import assert_shows_validation_error
from checks.sorting import (
    assert_special_values_at_end,
    assert_sorted_alphabetically,
    assert_sorted_by_leading_number,
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
    entered_value = curator_search_value(
        options=prw_planning_list_page.projector_curator_options(),
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
    entered_value = curator_search_value(
        options=prw_planning_list_page.planning_curator_options(),
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
    entered_value = subcompany_code_search_value(
        prw_planning_list_page.subcompany_options()
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
    entered_value = subcompany_name_search_value(
        options=prw_planning_list_page.subcompany_options(),
        case_transform=case_transform,
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
        assert_sorted_by_leading_number,
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
    entered_value = projection_doc_status_search_value(
        options=prw_planning_list_page.projection_doc_status_options(),
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


def title_search_value(
    titles: list[str],
    case_transform: Callable[[str], str],
) -> str:
    """
    Возвращает значение для поиска по названию объекта.

    Берет часть существующего названия
    и применяет преобразование регистра.
    """
    return case_transform(base_title_search_value(titles))


def base_title_search_value(titles: list[str]) -> str:
    """
    Возвращает базовое значение для поиска по названию объекта.

    Использует первое слово подходящей длины
    из списка названий.
    """
    for title in titles:
        for word in title.split():
            if len(word) >= TITLE_SEARCH_PART_LENGTH:
                return word[:TITLE_SEARCH_PART_LENGTH]

    raise AssertionError(
        "Не найдено наименование объекта, из которого можно взять часть "
        "для поиска.\n"
        f"Значения: {titles}"
    )


def curator_search_value(
    options: list[str],
    case_transform: Callable[[str], str],
) -> str:
    """
    Возвращает значение для поиска по куратору.

    Берет часть существующего имени
    и применяет преобразование регистра.
    """
    return case_transform(base_partial_search_value(options))


def base_partial_search_value(options: list[str]) -> str:
    """
    Возвращает базовое значение для поиска
    по выпадающему списку.

    Использует первое слово подходящей длины.
    """
    for option in options:
        word = option.split()[0].strip()

        if len(word) >= CURATOR_SEARCH_PART_LENGTH:
            return word[:CURATOR_SEARCH_PART_LENGTH]

    raise AssertionError(
        "Не найдено значение, из которого можно взять часть для поиска.\n"
        f"Значения: {options}"
    )


def subcompany_code_search_value(options: list[str]) -> str:
    """
    Возвращает часть кода ДО для поиска.

    Из значения формата:
        '123 | Название'
    извлекается часть числового кода.
    """
    for option in options:
        code = option.split("|", maxsplit=1)[0].strip()

        if len(code) >= SUBCOMPANY_CODE_SEARCH_PART_LENGTH:
            return code[-SUBCOMPANY_CODE_SEARCH_PART_LENGTH:]

    raise AssertionError(
        "Не найдено ДО, из которого можно взять часть кода для поиска.\n"
        f"Значения: {options}"
    )


def subcompany_name_search_value(
    options: list[str],
    case_transform: Callable[[str], str],
) -> str:
    """
    Возвращает значение для поиска по названию ДО.

    Берет часть существующего названия
    и применяет преобразование регистра.
    """
    return case_transform(base_subcompany_name_search_value(options))


def base_subcompany_name_search_value(options: list[str]) -> str:
    """
    Возвращает базовое значение для поиска по названию ДО.

    Из значения формата:
        '123 | Название'
    извлекается часть названия.
    """
    for option in options:
        name = option.split("|", maxsplit=1)[-1]

        for word in name.split():
            if len(word) >= SUBCOMPANY_NAME_SEARCH_PART_LENGTH:
                return word[:SUBCOMPANY_NAME_SEARCH_PART_LENGTH]

    raise AssertionError(
        "Не найдено ДО, из которого можно взять часть названия для поиска.\n"
        f"Значения: {options}"
    )


def projection_doc_status_search_value(
    options: list[str],
    case_transform: Callable[[str], str],
) -> str:
    """
    Возвращает значение для поиска по статусу ПД.

    Берет часть существующего статуса
    и применяет преобразование регистра.
    """
    return case_transform(base_projection_doc_status_search_value(options))


def base_projection_doc_status_search_value(options: list[str]) -> str:
    """
    Возвращает базовое значение для поиска по статусу ПД.

    Удаляет служебные символы
    и берет часть подходящего слова.
    """
    for option in options:
        for word in option.replace("\u200b", "").split():
            if len(word) >= PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH:
                return word[:PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH]

    raise AssertionError(
        "Не найден статус ПД, из которого можно взять часть для поиска.\n"
        f"Значения: {options}"
    )
