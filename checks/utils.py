"""Утилиты подготовки тестовых данных для проверок фильтров."""
from collections.abc import Callable
from datetime import date, datetime

from utils.value_matchers import (
    normalized_text,
    person_key,
    same_option_text,
    subcompany_code,
)


DATE_FORMAT = "%d.%m.%Y"


def identity(value: str) -> str:
    """
    Возвращает значение без изменений.
    Используется как преобразование регистра по умолчанию.
    """
    return value


def partial_filter_search_value(
    options: list[str],
    part_length: int,
    case_transform: Callable[[str], str] = identity,
) -> str:
    """
    Возвращает часть существующего значения фильтра для поиска.

    Удаляет служебные символы, берет часть первого подходящего слова
    и применяет преобразование регистра.
    """
    for option in options:
        for word in search_words(option):
            if len(word) >= part_length:
                return case_transform(word[:part_length])

    raise AssertionError(
        "Не найдено значение фильтра, из которого можно взять часть для поиска.\n"
        f"Значения: {options}"
    )


def search_words(value: str) -> list[str]:
    """
    Возвращает слова из строки для поиска.

    Удаляет служебные символы и разбивает строку на слова.
    """
    return value.replace("\u200b", "").split()


def partial_filter_code_search_value(
    options: list[str],
    part_length: int,
    separator: str = "|",
) -> str:
    """
    Возвращает часть кода из значения фильтра.

    Подходит для значений формата:
        'код | название'

    Для поиска берется окончание кода.
    """
    for option in options:
        code = option.split(separator, maxsplit=1)[0].strip()

        if len(code) >= part_length:
            return code[-part_length:]

    raise AssertionError(
        "Не найдено значение фильтра, из которого можно взять часть кода.\n"
        f"Значения: {options}"
    )


def partial_filter_name_search_value(
    options: list[str],
    part_length: int,
    case_transform: Callable[[str], str] = identity,
    separator: str = "|",
) -> str:
    """
    Возвращает часть названия из значения фильтра.

    Подходит для значений формата:
        'код | название'

    Извлекает часть после разделителя, затем берет часть первого
    подходящего слова.
    """
    names = [
        option.split(separator, maxsplit=1)[-1].strip()
        for option in options
    ]

    return partial_filter_search_value(
        options=names,
        part_length=part_length,
        case_transform=case_transform,
    )


def first_non_empty(values: list[str]) -> str:
    """
    Возвращает первое непустое значение из списка.
    Значение считается непустым после нормализации 
    через normalized_text.
    """
    for value in values:
        if normalized_text(value):
            return value

    raise AssertionError(f"Не найдено непустое значение в таблице: {values}")


def first_non_empty_or_none(values: list[str]) -> str | None:
    """Возвращает первое непустое значение из списка или None.

    Используется в тестах, где отсутствие данных должно приводить не к падению,
    а к контролируемому skip или отдельной обработке.
    """
    for value in values:
        if normalized_text(value):
            return value

    return None


def matching_person_option(options: list[str], table_value: str) -> str:
    """
    Находит option куратора, соответствующую значению из таблицы.

    Сравнение выполняется через person_key, чтобы учитывать разные форматы
    отображения ФИО в таблице и dropdown.
    """
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
    """
    Находит option дочернего общества по коду из таблицы.

    Подходит для случаев, когда в таблице отображается только код,
    а в dropdown значение имеет формат вроде «036 | ГД Уренгой».
    """
    for option in options:
        if subcompany_code(option) == code:
            return option

    raise AssertionError(
        "Не найдено ДО в выпадающем списке по коду из таблицы.\n"
        f"Код в таблице: {code}\n"
        f"Опции: {options}"
    )


def matching_option_text(options: list[str], table_value: str, option_name: str) -> str:
    """
    Находит option, соответствующую текстовому значению из таблицы.

    Используется для статусов, регионов, версий ИП и похожих значений,
    где текст в таблице и dropdown может отличаться пробелами или форматом.
    """
    for option in options:
        if same_option_text(table_value, option):
            return option

    raise AssertionError(
        f"В таблице найдено значение '{option_name}', но в выпадающем "
        "списке нет соответствующей опции.\n"
        f"Значение в таблице: {table_value}\n"
        f"Опции: {options}"
    )


def date_range_from_values(values: list[str]) -> tuple[str, str]:
    """
    Возвращает минимальную и максимальную дату из списка значений.
    Пустые значения игнорируются. Даты ожидаются в формате ДД.ММ.ГГГГ.
    """
    dates = sorted(
        parse_date(value)
        for value in values
        if normalized_text(value)
    )

    if not dates:
        raise AssertionError(f"Не найдено непустое значение в таблице: {values}")

    return format_date(dates[0]), format_date(dates[-1])


def parse_date(value: str) -> date:
    """Преобразует строку формата ДД.ММ.ГГГГ в date."""
    return datetime.strptime(value, DATE_FORMAT).date()


def format_date(value: date) -> str:
    """Форматирует date в строку ДД.ММ.ГГГГ."""
    return value.strftime(DATE_FORMAT)
