"""
CSV-отчетность для pytest-тестов.

Модуль добавляет pytest-опцию `--csv-report`, предоставляет фикстуру
`test_report` для записи деталей проверок и сохраняет итоговый CSV-файл
после завершения тестовой сессии.
"""
from typing import Any
from pathlib import Path
import csv
from datetime import datetime

import json
import pytest
from pydantic import BaseModel, Field


REPORT_HEADERS = [
    "time",
    "test",
    "status",
    "element",
    "expected",
    "actual",
    "message",
]


class ReportEntry(BaseModel):
    """Одна строка детализированного отчета проверки."""
    element: str
    expected: Any
    actual: Any
    message: str = ""


class CsvReport(BaseModel):
    """Накопитель строк отчета для одного теста."""
    entries: list[ReportEntry] = Field(default_factory=list)

    def add(
        self,
        *,
        element: str,
        expected: Any,
        actual: Any,
        message: str = "",
    ) -> None:
        """Добавляет строку проверки в отчет текущего теста."""
        self.entries.append(
            ReportEntry(
                element=element,
                expected=expected,
                actual=actual,
                message=message,
            )
        )


def pytest_addoption(parser):
    """Регистрирует CLI-опцию для пути к CSV-отчету."""
    parser.addoption(
        "--csv-report",
        action="store",
        default="reports/test_report.csv",
        help="Path to CSV report file.",
    )


def pytest_sessionstart(session):
    """Инициализирует общий список строк CSV-отчета перед запуском тестов."""
    session.config.csv_report_rows = []


@pytest.fixture
def test_report(request) -> CsvReport:
    """Создает отчет для текущего теста."""
    report = CsvReport()
    request.node.csv_report = report
    return report


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Переносит строки отчета теста в общий CSV-накопитель."""
    outcome = yield
    result = outcome.get_result()

    if result.when != "call":
        return

    report = getattr(item, "csv_report", None)
    entries = report.entries if report and report.entries else [empty_entry()]
    status = "passed" if result.passed else "failed" if result.failed else "skipped"
    message = result.longreprtext if result.failed else ""

    for entry in entries:
        item.config.csv_report_rows.append(
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "test": item.nodeid,
                "status": status,
                "element": entry.element,
                "expected": serialize(entry.expected),
                "actual": serialize(entry.actual),
                "message": entry.message or message,
            }
        )


def pytest_sessionfinish(session):
    """Сохраняет накопленные строки отчета в CSV-файл после завершения сессии."""
    report_path = Path(session.config.getoption("--csv-report"))
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REPORT_HEADERS)
        writer.writeheader()
        writer.writerows(session.config.csv_report_rows)


def empty_entry() -> ReportEntry:
    """Создает техническую строку отчета для тестов без деталей проверки."""
    return ReportEntry(
        element="",
        expected="",
        actual="",
        message="Test did not add report details.",
    )


def serialize(value: Any) -> str:
    """Сериализует значение для записи в CSV."""
    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)
