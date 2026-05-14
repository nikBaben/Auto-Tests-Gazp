"""Конфиг тестов montly planning"""
import pytest


SUBCOMPANY_CODE_SEARCH_PART_LENGTH = 2
SUBCOMPANY_NAME_SEARCH_PART_LENGTH = 4
REGION_NAME_SEARCH_PART_LENGTH = 4
STAGE_YEAR_SEARCH_PART_LENGTH = 2
STAGE_NAME_SEARCH_PART_LENGTH = 4
CASE_INSENSITIVE_SEARCH_CASES = (
    pytest.param(str.lower, id="lower"),
    pytest.param(str.upper, id="upper"),
    pytest.param(str.swapcase, id="mixed"),
)
