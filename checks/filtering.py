"""
Проверки для тестов поиска и применения фильтров.
Модуль содержит общие assert-функции для тестов.
"""
from typing import Callable
from checks.utils import parse_date
from utils.value_matchers import normalized_text
from fixtures.reports import CsvReport


def assert_values_contain_substring(
    *,
    element: str,
    entered_value: str,
    values: list[str],
    report: CsvReport,
    ignore_case: bool = False,
) -> None:
    """
    Проверяет, что все найденные значения содержат введенную строку.

    Используется для тестов поиска по частичному совпадению в фильтрах.
    Проверка дополнительно убеждается, что поиск не выглядит как точное
    совпадение: среди результатов должно быть хотя бы одно значение,
    отличающееся от введенного текста.
    """
    normalized_entered_value = _normalize(entered_value, ignore_case)
    wrong_values = [
        value
        for value in values
        if normalized_entered_value not in _normalize(value, ignore_case)
    ]
    report.add(
        element=element,
        expected=_expected_message(entered_value, ignore_case),
        actual=values,
        message="Проверка поиска по частичному совпадению",
    )

    assert values, (
        "После поиска не найдено ни одного значения.\n"
        f"Введено: {entered_value}"
    )
    assert not wrong_values, (
        "Найдены значения, которые не содержат введенный текст.\n"
        f"Введено: {entered_value}\n"
        f"Некорректные значения: {wrong_values}\n"
        f"Все найденные значения: {values}"
    )
    assert any(
        _normalize(value, ignore_case) != normalized_entered_value
        for value in values
    ), (
        "Поиск выглядит как точное совпадение, а не поиск по части значения.\n"
        f"Введено: {entered_value}\n"
        f"Все найденные значения: {values}"
    )


def _normalize(value: str, ignore_case: bool) -> str:
    """Нормализует строку для сравнения в проверках поиска."""
    return value.casefold() if ignore_case else value


def _expected_message(entered_value: str, ignore_case: bool) -> str:
    """Формирует текст ожидаемого результата для CSV-отчета."""
    if ignore_case:
        return (
            f"Все найденные значения содержат '{entered_value}' "
            "без учета регистра"
        )

    return f"Все найденные значения содержат '{entered_value}'"


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
    """
    Проверяет, что значения таблицы соответствуют выбранному фильтру.

    Используется после применения фильтра через кнопку «Найти».
    По умолчанию значения сравниваются через переданный normalizer.
    Если нужно особое сравнение, например для ФИО или option/table текста,
    можно передать same_value.
    """
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


def assert_date_values_in_range(
    *,
    element: str,
    date_from: str,
    date_to: str,
    values: list[str],
    report: CsvReport,
) -> None:
    """
    Проверяет, что все даты таблицы находятся в выбранном диапазоне.

    Пустые значения считаются ошибкой: если фильтр по диапазону дат применился,
    в результате не должны оставаться строки без даты.
    """
    start = parse_date(date_from)
    end = parse_date(date_to)
    empty_values = [value for value in values if not normalized_text(value)]
    wrong_values = [
        value
        for value in values
        if normalized_text(value) and not start <= parse_date(value) <= end
    ]

    report.add(
        element=element,
        expected=(
            "После нажатия 'Найти' все строки имеют дату утверждения "
            f"с {date_from} по {date_to}"
        ),
        actual=values,
        message="Проверка применения фильтра по диапазону дат",
    )

    assert values, (
        "После применения фильтра по дате утверждения не найдено ни одной строки.\n"
        f"Дата с: {date_from}\n"
        f"Дата по: {date_to}"
    )
    assert not empty_values, (
        "После применения фильтра по дате утверждения остались строки без даты.\n"
        f"Пустые значения: {empty_values}\n"
        f"Все значения в колонке: {values}"
    )
    assert not wrong_values, (
        "Найдены строки с датой утверждения вне выбранного диапазона.\n"
        f"Дата с: {date_from}\n"
        f"Дата по: {date_to}\n"
        f"Некорректные значения: {wrong_values}\n"
        f"Все значения в колонке: {values}"
    )
