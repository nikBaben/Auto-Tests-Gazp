import re

from fixtures.reports import CsvReport


SPECIAL_LAST_VALUES = ("", "Не указан", "Не указано", "Не представлялась")
REGION_CATEGORY_PREFIXES = (
    "Республика ",
    "г.",
    "г. ",
    "город ",
)
REGION_CATEGORY_SUFFIXES = (
    " автономная область",
    " автономный округ",
    " область",
    " край",
    " Республика",
)
IP_VERSION_TYPE_ORDER = {
    "range": 0,
    "уточн": 1,
    "кварт": 2,
    "полуг": 3,
}


def assert_sorted_alphabetically(
    *,
    element: str,
    values: list[str],
    report: CsvReport,
) -> None:
    expected = sorted(values, key=alphabetic_with_special_last)

    report.add(
        element=element,
        expected=expected,
        actual=values,
        message="Проверка сортировки по алфавиту, спец-значения в конце",
    )

    assert values == expected, (
        "Список не отсортирован по алфавиту.\n"
        "Пустые значения, 'Не указан' и 'Не указано' должны быть в конце списка.\n"
        f"Фактический порядок: {values}\n"
        f"Ожидаемый порядок: {expected}"
    )


def assert_sorted_by_leading_number(
    *,
    element: str,
    values: list[str],
    report: CsvReport,
) -> None:
    numeric_values = [value for value in values if has_leading_number(value)]
    text_values = [
        value
        for value in values
        if not has_leading_number(value)
        and not is_special_last_value(value)
    ]
    special_values = [
        value
        for value in values
        if is_special_last_value(value)
    ]
    expected = sorted(numeric_values, key=leading_number) + sorted(
        text_values,
        key=str.casefold,
    ) + special_values

    report.add(
        element=element,
        expected=expected,
        actual=values,
        message=(
            "Проверка сортировки: сначала числовые коды по возрастанию, "
            "затем буквенные коды по алфавиту, затем спец-значения"
        ),
    )

    assert values == expected, (
        "Список отсортирован некорректно.\n"
        "Ожидается: сначала значения с числовым кодом по возрастанию, "
        "затем значения с буквенным кодом по алфавиту, "
        "затем пустые значения, 'Не указан' и 'Не указано'.\n"
        f"Фактический порядок: {values}\n"
        f"Ожидаемый порядок: {expected}"
    )


def assert_special_values_at_end(
    *,
    element: str,
    values: list[str],
    report: CsvReport,
) -> None:
    expected = [
        value for value in values
        if not is_special_last_value(value)
    ] + [
        value for value in values
        if is_special_last_value(value)
    ]
    special_values = [
        value for value in values
        if is_special_last_value(value)
    ]

    report.add(
        element=element,
        expected=expected,
        actual={
            "values": values,
            "special_values": special_values,
        },
        message=(
            "Проверка расположения пустых значений, "
            "'Не указан' и 'Не указано' в конце списка"
        ),
    )

    assert values == expected, (
        "Спец-значения расположены не в конце списка.\n"
        "Пустые значения, 'Не указан' и 'Не указано' должны идти после "
        "всех обычных значений.\n"
        f"Фактический порядок: {values}\n"
        f"Ожидаемый порядок: {expected}"
    )


def alphabetic_with_special_last(value: str) -> tuple[bool, str]:
    return is_special_last_value(value), value.casefold()


def is_special_last_value(value: str) -> bool:
    return value.strip() in SPECIAL_LAST_VALUES


def has_leading_number(value: str) -> bool:
    return re.match(r"^\s*\d+", value) is not None


def leading_number(value: str) -> int:
    match = re.match(r"^\s*(\d+)", value)
    assert match is not None
    return int(match.group(1))


def assert_sorted_regions_by_name(
    *,
    element: str,
    values: list[str],
    report: CsvReport,
) -> None:
    expected = sorted(values, key=region_name_with_special_last)

    report.add(
        element=element,
        expected=expected,
        actual=values,
        message=(
            "Проверка сортировки регионов по названию без учета типа региона"
        ),
    )

    assert values == expected, (
        "Список регионов отсортирован некорректно.\n"
        "Сортировка должна идти по названию региона без учета слов "
        "'Республика', 'область', 'край', 'автономный округ' и подобных.\n"
        f"Фактический порядок: {values}\n"
        f"Ожидаемый порядок: {expected}"
    )


def region_name_with_special_last(value: str) -> tuple[bool, str]:
    return is_special_last_value(value), normalized_region_name(value)


def normalized_region_name(value: str) -> str:
    region_name = value.strip()

    parenthesized_name = re.search(r"\(([^()]+)\)\s*$", region_name)
    if parenthesized_name:
        region_name = parenthesized_name.group(1)

    for prefix in REGION_CATEGORY_PREFIXES:
        if region_name.startswith(prefix):
            region_name = region_name[len(prefix):]
            break

    for suffix in REGION_CATEGORY_SUFFIXES:
        if region_name.endswith(suffix):
            region_name = region_name[:-len(suffix)]
            break

    return region_name.strip().casefold()


def assert_sorted_ip_versions(
    *,
    element: str,
    values: list[str],
    report: CsvReport,
) -> None:
    expected = sorted(values, key=ip_version_with_special_last)

    report.add(
        element=element,
        expected=expected,
        actual=values,
        message=(
            "Проверка сортировки версий ИП: диапазон, уточн., кварт., полуг."
        ),
    )

    assert values == expected, (
        "Список версий ИП отсортирован некорректно.\n"
        "Ожидается сортировка пачками по году: сначала диапазон лет, "
        "затем 'уточн.', затем 'кварт.', затем 'полуг.'.\n"
        f"Фактический порядок: {values}\n"
        f"Ожидаемый порядок: {expected}"
    )


def ip_version_with_special_last(value: str) -> tuple[bool, int, int, str]:
    year, version_type_order = ip_version_sort_parts(value)
    return is_special_last_value(value), year, version_type_order, value.casefold()


def ip_version_sort_parts(value: str) -> tuple[int, int]:
    version = value.strip().casefold()
    year_match = re.match(r"^(\d{4})", version)

    if not year_match:
        return 9999, 99

    year = int(year_match.group(1))

    if re.match(r"^\d{4}\s*-\s*\d{4}", version):
        return year, IP_VERSION_TYPE_ORDER["range"]

    for version_type, version_type_order in IP_VERSION_TYPE_ORDER.items():
        if version_type in version:
            return year, version_type_order

    return year, 99
