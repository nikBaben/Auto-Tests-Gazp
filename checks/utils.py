from collections.abc import Callable


def partial_filter_search_value(
    options: list[str],
    part_length: int,
    case_transform: Callable[[str], str] = lambda value: value,
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
    separator: str = "|",
    case_transform: Callable[[str], str] = lambda value: value,
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

