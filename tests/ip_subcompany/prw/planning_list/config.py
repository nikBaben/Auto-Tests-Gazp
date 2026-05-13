"""Конфиг тестов planning list"""
import pytest


NON_NEGATIVE_INTEGER_ERROR = "Укажите целое неотрицательное число"
OBJECT_PRW_CODE_SEARCH_PART_LENGTH = 3
TITLE_SEARCH_PART_LENGTH = 4
CURATOR_SEARCH_PART_LENGTH = 4
SUBCOMPANY_CODE_SEARCH_PART_LENGTH = 2
SUBCOMPANY_NAME_SEARCH_PART_LENGTH = 4
PROJECTION_DOC_STATUS_SEARCH_PART_LENGTH = 4


CASE_INSENSITIVE_SEARCH_CASES = (
    pytest.param(str.lower, id="lower"),
    pytest.param(str.upper, id="upper"),
    pytest.param(str.swapcase, id="mixed"),
)
