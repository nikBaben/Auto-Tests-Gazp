"""Объект страницы 'План ПИР'."""
from enum import StrEnum

from components.schemas.ant_table_schema import AntTableColumn
from pages.filtered_table_page import FilteredTablePage
from utils.value_matchers import (
    first_word,
    normalized_text,
    same_option_text,
    same_person,
    subcompany_code,
)


class PrwPlanningListFilterTitle(StrEnum):
    """Отображаемые названия фильтров на странице."""
    OBJECT_PRW_CODE = "Код ПИР"
    TITLE = "Наименование объекта"
    PROJECTOR_CURATOR = "Куратор проектировщика"
    PLANNING_CURATOR = "Куратор планирования"
    SUBCOMPANY = "ДО"
    PROJECTION_DOC_STATUS = "Статус ПД"


class PrwPlanningListFilterId(StrEnum):
    """HTML id полей фильтров на странице."""
    OBJECT_PRW_CODE_ID = "object_prw_code"
    TITLE_ID = "title"
    PROJECTOR_CURATOR_ID = "projector_curator_id"
    PLANNING_CURATOR_ID = "planning_curator_id"
    SUBCOMPANY_ID = "subcompany_ids"
    PROJECTION_DOC_STATUS_ID = "projection_doc_status_id"


class PrwPlanningListColumn:
    """Колонки таблицы на странице."""
    OBJECT_PRW_CODE_COLUMN = AntTableColumn(headers=("Код ПИР",))
    TITLE_COLUMN = AntTableColumn(headers=("Объект проектирования",))
    SUBCOMPANY_COLUMN = AntTableColumn(headers=("Зак Т.",))
    PROJECTION_DOC_STATUS_COLUMN = AntTableColumn(headers=("Статус ПД",))
    PROJECTOR_CURATOR_COLUMN = AntTableColumn(headers=("Куратор проектирования",))
    PLANNING_CURATOR_COLUMN = AntTableColumn(headers=("Куратор планирования",))


class PrwPlanningListPage(FilteredTablePage):
    """
    PageObject.

    URL: /ip-subcompany/prw/planning-list.
    Класс описывает фильтры и видимые значения на странице.
    """
    PATH = "/ip-subcompany/prw/planning-list"
    FILTER_IDS = PrwPlanningListFilterId

    def fill_object_prw_code(self, value: str) -> None:
        """Заполнить поле фильтра «Код ПИР» без отправки формы."""
        self.text_input(PrwPlanningListFilterId.OBJECT_PRW_CODE_ID).fill(value)

    def object_prw_code_value(self) -> str:
        """Вернуть текущее значение поля фильтра «Код ПИР»."""
        return self.text_input(PrwPlanningListFilterId.OBJECT_PRW_CODE_ID).value()

    def object_prw_code_error(self) -> str:
        """Вернуть текст ошибки валидации поля «Код ПИР»."""
        return self.text_input(
            PrwPlanningListFilterId.OBJECT_PRW_CODE_ID
        ).error_text()

    def object_prw_codes(self) -> list[str]:
        """Вернуть видимые значения колонки таблицы «Код ПИР»."""
        return self.table_column_values_by_spec(
            PrwPlanningListColumn.OBJECT_PRW_CODE_COLUMN
        )

    def wait_object_prw_codes(self) -> list[str]:
        """Дождаться появления значений в колонке «Код ПИР» и вернуть их."""
        return self.wait.until(lambda _: self.object_prw_codes())

    def search_by_object_prw_code(self, value: str) -> list[str]:
        """Применить текстовый фильтр «Код ПИР» и вернуть значения колонки."""
        return self.search_text_filter(
            input_id=PrwPlanningListFilterId.OBJECT_PRW_CODE_ID,
            value=value,
            result_getter=self.object_prw_codes,
        )

    def fill_title(self, value: str) -> None:
        """Заполнить поле фильтра «Наименование объекта» без отправки формы."""
        self.text_input(PrwPlanningListFilterId.TITLE_ID).fill(value)

    def titles(self) -> list[str]:
        """Вернуть видимые значения колонки «Наименование объекта»."""
        return self.table_column_values_by_spec(PrwPlanningListColumn.TITLE_COLUMN)

    def wait_titles(self) -> list[str]:
        """Дождаться появления значений в колонке «Наименование объекта»."""
        return self.wait.until(lambda _: self.titles())

    def search_by_title(self, value: str) -> list[str]:
        """Применить фильтр по наименованию объекта и вернуть значения колонки."""
        return self.search_text_filter(
            input_id=PrwPlanningListFilterId.TITLE_ID,
            value=value,
            result_getter=self.titles,
            ignore_case=True,
        )

    def projector_curators(self) -> list[str]:
        """Вернуть видимые значения колонки «Куратор проектировщика»."""
        return self.table_column_values_by_spec(
            PrwPlanningListColumn.PROJECTOR_CURATOR_COLUMN
        )

    def projector_curator_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Куратор проектировщика»."""
        return self.dropdown_options(PrwPlanningListFilterId.PROJECTOR_CURATOR_ID)

    def projector_curator_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска куратора проектировщика."""
        return self.dropdown_options_by_search(
            PrwPlanningListFilterId.PROJECTOR_CURATOR_ID,
            value,
        )

    def apply_projector_curator_filter(self, value: str) -> list[str]:
        """
        Выбрать куратора проектировщика, нажать «Найти» и вернуть колонку.

        Ожидание завершится, когда все видимые строки таблицы будут относиться
        к выбранному куратору или таблица станет пустой.
        """
        return self.apply_dropdown_filter(
            input_id=PrwPlanningListFilterId.PROJECTOR_CURATOR_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.projector_curators,
            result_matches=lambda result: same_person(result, value),
        )

    def planning_curators(self) -> list[str]:
        """Вернуть видимые значения колонки «Куратор планирования»."""
        return self.table_column_values_by_spec(
            PrwPlanningListColumn.PLANNING_CURATOR_COLUMN
        )

    def planning_curator_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Куратор планирования»."""
        return self.dropdown_options(PrwPlanningListFilterId.PLANNING_CURATOR_ID)

    def planning_curator_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска куратора планирования."""
        return self.dropdown_options_by_search(
            PrwPlanningListFilterId.PLANNING_CURATOR_ID,
            value,
        )

    def apply_planning_curator_filter(self, value: str) -> list[str]:
        """
        Выбрать куратора планирования, нажать «Найти» и вернуть колонку.

        Ожидание завершится, когда все видимые строки таблицы будут относиться
        к выбранному куратору или таблица станет пустой.
        """
        return self.apply_dropdown_filter(
            input_id=PrwPlanningListFilterId.PLANNING_CURATOR_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.planning_curators,
            result_matches=lambda result: same_person(result, value),
        )

    def subcompany_codes(self) -> list[str]:
        """Вернуть видимые значения колонки «Дочернее общество»."""
        return self.table_column_values_by_spec(PrwPlanningListColumn.SUBCOMPANY_COLUMN)

    def subcompany_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Дочернее общество»."""
        return self.dropdown_options(PrwPlanningListFilterId.SUBCOMPANY_ID)

    def subcompany_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска дочернего общества."""
        return self.dropdown_options_by_search(
            PrwPlanningListFilterId.SUBCOMPANY_ID,
            value,
        )

    def apply_subcompany_filter(self, value: str) -> list[str]:
        """
        Выбрать дочернее общество, нажать «Найти» и вернуть колонку.

        Для проверки таблицы используется код ДО из выбранной опции, потому что
        в таблице отображается короткий код, а в выпадающем списке код может
        идти вместе с названием.
        """
        code = subcompany_code(value)

        return self.apply_dropdown_filter(
            input_id=PrwPlanningListFilterId.SUBCOMPANY_ID,
            value=value,
            search_value=code,
            result_getter=self.subcompany_codes,
            result_matches=lambda result: normalized_text(result) == code,
        )

    def projection_doc_statuses(self) -> list[str]:
        """Вернуть видимые значения колонки «Статус ПД»."""
        return self.table_column_values_by_spec(
            PrwPlanningListColumn.PROJECTION_DOC_STATUS_COLUMN
        )

    def projection_doc_status_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Статус ПД»."""
        return self.dropdown_options(
            PrwPlanningListFilterId.PROJECTION_DOC_STATUS_ID
        )

    def projection_doc_status_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска статуса ПД."""
        return self.dropdown_options_by_search(
            PrwPlanningListFilterId.PROJECTION_DOC_STATUS_ID,
            value,
        )

    def apply_projection_doc_status_filter(self, value: str) -> list[str]:
        """
        Выбрать статус ПД, нажать «Найти» и вернуть значения колонки.

        Сравнение допускает различия в пробелах и частичное совпадение текста,
        потому что текст в опции и в таблице может отображаться не полностью
        одинаково.
        """
        return self.apply_dropdown_filter(
            input_id=PrwPlanningListFilterId.PROJECTION_DOC_STATUS_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.projection_doc_statuses,
            result_matches=lambda result: same_option_text(result, value),
        )
