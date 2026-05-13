from collections.abc import Callable

from planning_list.config import (
    TITLE_SEARCH_PART_LENGTH,
    CURATOR_SEARCH_PART_LENGTH,
    SUBCOMPANY_CODE_SEARCH_PART_LENGTH,
    SUBCOMPANY_NAME_SEARCH_PART_LENGTH,
    PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH,
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
