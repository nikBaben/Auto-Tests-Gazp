"""Объект страницы 'Задание на проектирование'."""
from datetime import date, datetime
from enum import StrEnum

from selenium.common.exceptions import TimeoutException
from components.schemas.ant_table_schema import AntTableColumn
from pages.filtered_table_page import FilteredTablePage

from utils.value_matchers import normalized_text


class PrwDesignAssignmentFilterTitle(StrEnum):
    """Отображаемые названия фильтров на странице."""
    OBJECT_CODE = "Код ПИР"
    SUBCOMPANY = "Заказчик"
    DESIGN_ASSIGNMENT_TYPE = "Вид ЗнП"
    CHANGE = "Изменения"
    STATUS = "Статус"
    PROJECTOR_CURATOR = "Куратор"
    APPROVAL_DATE_FROM = "Дата утверждения с"
    APPROVAL_DATE_TO = "Дата утверждения по"
    SEARCH = "Поиск"


class PrwDesignAssignmentFilterId(StrEnum):
    """HTML id полей фильтров на странице."""
    OBJECT_CODE_ID = "object_code"
    SUBCOMPANY_IDS = "subcompany_ids"
    DESIGN_ASSIGNMENT_TYPE_ID = "design_assignment_type"
    CHANGE_ID = "change"
    STATUS_ID = "status"
    PROJECTOR_CURATOR_ID = "projector_curator_id"
    APPROVAL_DATE_FROM_ID = "approval_date_from"
    APPROVAL_DATE_TO = "approval_date_to"
    SEARCH_ID = "search"


class PrwDesignAssignmentColumn:
    """Колонки таблицы на странице."""
    SUBCOMPANY = AntTableColumn(headers=("Заказчик",))
    OBJECT_CODE = AntTableColumn(headers=("Код ПИР",))
    DESIGN_ASSIGNMENT_TYPE = AntTableColumn(headers=("Вид",))
    CHANGE = AntTableColumn(headers=("Изм",))
    STATUS = AntTableColumn(headers=("Статус",))
    TITLE = AntTableColumn(headers=("Наименование",))
    RECEIPT_DATE = AntTableColumn(headers=("Дата поступления",))
    APPROVAL_DATE = AntTableColumn(headers=("Дата утверждения",))
    ASSIGNMENT_NUMBER = AntTableColumn(headers=("№ задания",))
    PROJECTOR_CURATOR = AntTableColumn(headers=("Куратор",))
    EA_PROJECT = AntTableColumn(headers=("ЭА проект",))
    EA_APPROVAL = AntTableColumn(headers=("ЭА утв",))


class PrwDesignAssignmentPage(FilteredTablePage):
    """
    PageObject.
    URL: /ip-subcompany/prw/design-assignments
    Класс описывает фильтры и видимые значения на странице.
    """
    PATH = "/ip-subcompany/prw/design-assignments"
    FILTER_IDS = PrwDesignAssignmentFilterId
    CODE_PRW = PrwDesignAssignmentFilterTitle.OBJECT_CODE
    PROJECT_CURATOR = PrwDesignAssignmentFilterTitle.PROJECTOR_CURATOR
    DATE_FORMAT = "%d.%m.%Y"

    def fill_object_code(self, value: str) -> None:
        """Заполнить поле фильтра «Код ПИР» без отправки формы."""
        self.text_input(PrwDesignAssignmentFilterId.OBJECT_CODE_ID).fill(value)

    def object_code_value(self) -> str:
        """Вернуть текущее значение поля фильтра «Код ПИР»."""
        return self.text_input(PrwDesignAssignmentFilterId.OBJECT_CODE_ID).value()

    def object_code_error(self) -> str:
        """Вернуть текст ошибки валидации поля «Код ПИР»."""
        try:
            return self.text_input(
                PrwDesignAssignmentFilterId.OBJECT_CODE_ID
            ).error_text(timeout=5)
        except TimeoutException:
            return ""

    def object_codes(self) -> list[str]:
        """Вернуть видимые значения колонки «Код ПИР»."""
        return self.table_column_values_by_spec(
            PrwDesignAssignmentColumn.OBJECT_CODE
        )

    def approval_dates(self, keep_empty: bool = False) -> list[str]:
        """Вернуть значения колонки «Дата утверждения»."""
        return self.table_column_values_by_spec(
            PrwDesignAssignmentColumn.APPROVAL_DATE,
            keep_empty=keep_empty,
        )

    def wait_approval_dates(self, keep_empty: bool = False) -> list[str]:
        """Дождаться появления колонки «Дата утверждения» и вернуть значения."""
        return self.wait.until(lambda _: self.approval_dates(keep_empty=keep_empty))

    def fill_approval_date_from(self, value: str) -> None:
        """Заполнить фильтр «Дата утверждения с» без отправки формы."""
        self.date_input(PrwDesignAssignmentFilterId.APPROVAL_DATE_FROM_ID).fill(value)

    def approval_date_from_value(self) -> str:
        """Вернуть текущее значение фильтра «Дата утверждения с»."""
        return self.date_input(
            PrwDesignAssignmentFilterId.APPROVAL_DATE_FROM_ID
        ).value()

    def fill_approval_date_to(self, value: str) -> None:
        """Заполнить фильтр «Дата утверждения по» без отправки формы."""
        self.date_input(PrwDesignAssignmentFilterId.APPROVAL_DATE_TO).fill(value)

    def approval_date_to_value(self) -> str:
        """Вернуть текущее значение фильтра «Дата утверждения по»."""
        return self.date_input(PrwDesignAssignmentFilterId.APPROVAL_DATE_TO).value()

    def apply_approval_date_range_filter(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[str]:
        """
        Применить диапазон дат утверждения и вернуть значения колонки.

        Пустые даты в таблице считаются несоответствием диапазону, поэтому
        после фильтра они не должны оставаться среди видимых строк.
        """
        if date_from:
            self.fill_approval_date_from(date_from)
        if date_to:
            self.fill_approval_date_to(date_to)

        self.submit_filters()
        self.wait.until(
            lambda _: self._approval_date_range_filter_applied(
                date_from=date_from,
                date_to=date_to,
            )
        )

        return self.approval_dates(keep_empty=True)

    def projector_curator_id_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Куратор»."""
        return self.dropdown_options(
            PrwDesignAssignmentFilterId.PROJECTOR_CURATOR_ID
        )

    def projector_curators(self) -> list[str]:
        """Вернуть видимые значения колонки «Куратор»."""
        return self.table_column_values_by_spec(
            PrwDesignAssignmentColumn.PROJECTOR_CURATOR
        )

    def _approval_date_range_filter_applied(
        self,
        date_from: str | None,
        date_to: str | None,
    ) -> bool:
        values = self.approval_dates(keep_empty=True)

        if not values:
            return self.table_is_empty()

        return all(
            self._date_in_range(value, date_from=date_from, date_to=date_to)
            for value in values
        )

    def _date_in_range(
        self,
        value: str,
        date_from: str | None,
        date_to: str | None,
    ) -> bool:
        normalized_value = normalized_text(value)

        if not normalized_value:
            return False

        current_date = self._parse_date(normalized_value)

        if date_from and current_date < self._parse_date(date_from):
            return False
        if date_to and current_date > self._parse_date(date_to):
            return False

        return True

    def _parse_date(self, value: str) -> date:
        return datetime.strptime(value, self.DATE_FORMAT).date()
