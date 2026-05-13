from fixtures.reports import CsvReport


def assert_values_contain_substring(
    *,
    element: str,
    entered_value: str,
    values: list[str],
    report: CsvReport,
    ignore_case: bool = False,
) -> None:
    normalized_entered_value = normalize(entered_value, ignore_case)
    wrong_values = [
        value
        for value in values
        if normalized_entered_value not in normalize(value, ignore_case)
    ]
    report.add(
        element=element,
        expected=expected_message(entered_value, ignore_case),
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
        normalize(value, ignore_case) != normalized_entered_value
        for value in values
    ), (
        "Поиск выглядит как точное совпадение, а не поиск по части значения.\n"
        f"Введено: {entered_value}\n"
        f"Все найденные значения: {values}"
    )


def normalize(value: str, ignore_case: bool) -> str:
    return value.casefold() if ignore_case else value


def expected_message(entered_value: str, ignore_case: bool) -> str:
    if ignore_case:
        return (
            f"Все найденные значения содержат '{entered_value}' "
            "без учета регистра"
        )

    return f"Все найденные значения содержат '{entered_value}'"
