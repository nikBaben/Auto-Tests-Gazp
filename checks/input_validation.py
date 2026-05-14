"""
Проверки для тестов валидации полей формы.

Модуль содержит общие assert-функции, которые проверяют,
что после ввода некорректного значения поле показывает ожидаемые ошибки
валидации.
"""
from fixtures.reports import CsvReport


def assert_shows_validation_error(
    *,
    element: str,
    entered_value: str,
    field_value: str,
    expected_error: str,
    actual_error: str,
    report: CsvReport,
) -> None:
    """Проверяет, что поле показывает ожидаемую ошибку валидации."""
    report.add(
        element=element,
        expected=expected_error,
        actual={
            "entered": entered_value,
            "field_value": field_value,
            "error": actual_error,
        },
        message="Проверка ошибки валидации при вводе некорректного значения",
    )

    assert actual_error == expected_error, (
        "Некорректный текст ошибки валидации.\n"
        f"Введено: {entered_value}\n"
        f"Фактическое значение поля: {field_value}\n"
        f"Фактическая ошибка: {actual_error}\n"
        f"Ожидаемая ошибка: {expected_error}"
    )
