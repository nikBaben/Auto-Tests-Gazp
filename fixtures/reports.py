from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

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
    element: str
    expected: Any
    actual: Any
    message: str = ""


class CsvReport(BaseModel):
    entries: list[ReportEntry] = Field(default_factory=list)

    def add(
        self,
        *,
        element: str,
        expected: Any,
        actual: Any,
        message: str = "",
    ) -> None:
        self.entries.append(
            ReportEntry(
                element=element,
                expected=expected,
                actual=actual,
                message=message,
            )
        )


def pytest_addoption(parser):
    parser.addoption(
        "--csv-report",
        action="store",
        default="reports/test_report.csv",
        help="Path to CSV report file.",
    )


def pytest_sessionstart(session):
    session.config.csv_report_rows = []


@pytest.fixture
def test_report(request) -> CsvReport:
    report = CsvReport()
    request.node.csv_report = report
    return report


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
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
    report_path = Path(session.config.getoption("--csv-report"))
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REPORT_HEADERS)
        writer.writeheader()
        writer.writerows(session.config.csv_report_rows)


def empty_entry() -> ReportEntry:
    return ReportEntry(
        element="",
        expected="",
        actual="",
        message="Test did not add report details.",
    )


def serialize(value: Any) -> str:
    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)
