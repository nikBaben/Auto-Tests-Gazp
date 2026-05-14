"""Объект страницы 'Объекты проектирования'."""
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


class PrwProjectsObjectsFilterTitle(StrEnum):
    """Отображаемые названия фильтров на странице."""
    SUBCOMPANY = "ДО"
    OBJECT_PLANNING_CODE = "Код ПИР"
    STAGE = "Версия ИП"
    TITLE = "Наименование объекта"
    DESIGN_ASSIGNMENT_STATUS = "Статус ЗнП"
    PROJECTOR_CURATOR = "Куратор проектир."
    PLANNING_CURATOR = "Куратор планир."
    PROJECTION_DOC_STATUS = "Статус ПД"


class PrwProjectsObjectsFilterId(StrEnum):
    """HTML id полей фильтров на странице."""
    SUBCOMPANY_IDS = "subcompany_ids"
    OBJECT_PLANNING_CODE_ID = "object_planning_code"
    STAGE_ID = "stage_id"
    TITLE_ID = "title"
    DESIGN_ASSIGNMENT_STATUS_ID = "design_assignment_status_id"
    PROJECTOR_CURATOR_ID = "projector_curator_id"
    PLANNING_CURATOR_ID = "planning_curator_id"
    PROJECTION_DOC_STATUS_ID = "projection_doc_status_id"


class PrwProjectsObjectsColumn:
    """Колонки таблицы на странице."""

    CURATORS_CHECKBOX = "Кураторы"

    SUBCOMPANY = AntTableColumn(headers=("Код зак.", "Код заказчика", "ДО"))
    OBJECT_PLANNING_CODE = AntTableColumn(headers=("Код объекта", "Код ПИР"))
    TITLE = AntTableColumn(headers=("Наименование объекта",))
    STAGE = AntTableColumn(
        headers=("Год ИП",),
        header_paths=(("Лимит ПИР", "Год ИП"),),
    )
    PROJECTION_DOC_STATUS = AntTableColumn(
        header_paths=(("Статус утверждения ПД", "Статус"),),
    )
    PROJECTOR_CURATOR = AntTableColumn(
        headers=(
            "Куратор проектир.",
            "Куратор проектир",
            "Куратор проектирования",
            "Куратор проектировщика",
        ),
        checkbox_label=CURATORS_CHECKBOX,
    )
    PLANNING_CURATOR = AntTableColumn(
        headers=(
            "Куратор планир.",
            "Куратор планир",
            "Куратор планирования",
        ),
        checkbox_label=CURATORS_CHECKBOX,
    )


class PrwProjectsObjectsPage(FilteredTablePage):
    """
    PageObject.

    URL: /ip-subcompany/prw/project-objects.
    Класс описывает фильтры и видимые значения на странице.
    """
    PATH = "/ip-subcompany/prw/project-objects"
    FILTER_IDS = PrwProjectsObjectsFilterId

    def fill_object_planning_code(self, value: str) -> None:
        """Заполнить поле фильтра «Код ПИР» без отправки формы."""
        self.text_input(PrwProjectsObjectsFilterId.OBJECT_PLANNING_CODE_ID).fill(
            value
        )

    def object_planning_code_value(self) -> str:
        """Вернуть текущее значение поля фильтра «Код ПИР»."""
        return self.text_input(
            PrwProjectsObjectsFilterId.OBJECT_PLANNING_CODE_ID
        ).value()

    def object_planning_code_error(self) -> str:
        """Вернуть текст ошибки валидации поля «Код ПИР»."""
        return self.text_input(
            PrwProjectsObjectsFilterId.OBJECT_PLANNING_CODE_ID
        ).error_text()

    def fill_title(self, value: str) -> None:
        """Заполнить поле фильтра «Наименование объекта» без отправки формы."""
        self.text_input(PrwProjectsObjectsFilterId.TITLE_ID).fill(value)

    def titles(self) -> list[str]:
        """Вернуть видимые значения колонки «Наименование объекта»."""
        return self.table_column_values_by_spec(PrwProjectsObjectsColumn.TITLE)

    def wait_titles(self) -> list[str]:
        """Дождаться появления значений в колонке «Наименование объекта»."""
        return self.wait.until(lambda _: self.titles())

    def search_by_title(self, value: str) -> list[str]:
        """Применить фильтр по наименованию объекта и вернуть значения колонки."""
        return self.search_text_filter(
            input_id=PrwProjectsObjectsFilterId.TITLE_ID,
            value=value,
            result_getter=self.titles,
            ignore_case=True,
        )

    def projector_curators(self) -> list[str]:
        """Вернуть видимые значения колонки «Куратор проектировщика»."""
        return self.table_column_values_by_spec(
            PrwProjectsObjectsColumn.PROJECTOR_CURATOR
        )

    def projector_curator_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Куратор проектировщика»."""
        return self.dropdown_options(
            PrwProjectsObjectsFilterId.PROJECTOR_CURATOR_ID
        )

    def projector_curator_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска куратора проектировщика."""
        return self.dropdown_options_by_search(
            PrwProjectsObjectsFilterId.PROJECTOR_CURATOR_ID,
            value,
        )

    def apply_projector_curator_filter(self, value: str) -> list[str]:
        """
        Выбрать куратора проектировщика, нажать «Найти» и вернуть колонку.

        Ожидание завершится, когда все видимые строки таблицы будут относиться
        к выбранному куратору или таблица станет пустой.
        """
        self.enable_curators_columns()

        return self.apply_dropdown_filter(
            input_id=PrwProjectsObjectsFilterId.PROJECTOR_CURATOR_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.projector_curators,
            result_matches=lambda result: same_person(result, value),
        )

    def planning_curators(self) -> list[str]:
        """Вернуть видимые значения колонки «Куратор планирования»."""
        return self.table_column_values_by_spec(
            PrwProjectsObjectsColumn.PLANNING_CURATOR
        )

    def planning_curator_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Куратор планирования»."""
        return self.dropdown_options(
            PrwProjectsObjectsFilterId.PLANNING_CURATOR_ID
        )

    def planning_curator_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска куратора планирования."""
        return self.dropdown_options_by_search(
            PrwProjectsObjectsFilterId.PLANNING_CURATOR_ID,
            value,
        )

    def apply_planning_curator_filter(self, value: str) -> list[str]:
        """
        Выбрать куратора планирования, нажать «Найти» и вернуть колонку.

        Ожидание завершится, когда все видимые строки таблицы будут относиться
        к выбранному куратору или таблица станет пустой.
        """
        self.enable_curators_columns()

        return self.apply_dropdown_filter(
            input_id=PrwProjectsObjectsFilterId.PLANNING_CURATOR_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.planning_curators,
            result_matches=lambda result: same_person(result, value),
        )

    def subcompanies(self) -> list[str]:
        """Вернуть видимые значения колонки 'ДО'."""
        return self.table_column_values_by_spec(PrwProjectsObjectsColumn.SUBCOMPANY)

    def subcompany_options(self) -> list[str]:
        """Вернуть полный список опций фильтра 'ДО'."""
        return self.dropdown_options(PrwProjectsObjectsFilterId.SUBCOMPANY_IDS)

    def subcompany_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска 'ДО'."""
        return self.dropdown_options_by_search(
            PrwProjectsObjectsFilterId.SUBCOMPANY_IDS,
            value,
        )

    def apply_subcompany_filter(self, value: str) -> list[str]:
        """
        Выбрать 'ДО', нажать «Найти» и вернуть колонку.

        Для проверки таблицы используется код ДО из выбранной опции, потому что
        в таблице отображается короткий код, а в выпадающем списке код может
        идти вместе с названием.
        """
        code = subcompany_code(value)

        return self.apply_dropdown_filter(
            input_id=PrwProjectsObjectsFilterId.SUBCOMPANY_IDS,
            value=value,
            search_value=code,
            result_getter=self.subcompanies,
            result_matches=lambda result: normalized_text(result) == code,
        )

    def projection_doc_statuses(self) -> list[str]:
        """Вернуть видимые значения колонки «Статус ПД»."""
        return self.table_column_values_by_spec(
            PrwProjectsObjectsColumn.PROJECTION_DOC_STATUS
        )

    def projection_doc_status_options(self) -> list[str]:
        """Вернуть полный список опций фильтра «Статус ПД»."""
        return self.dropdown_options(
            PrwProjectsObjectsFilterId.PROJECTION_DOC_STATUS_ID
        )

    def projection_doc_status_options_by_search(self, value: str) -> list[str]:
        """Вернуть опции, показанные UI после поиска статуса ПД."""
        return self.dropdown_options_by_search(
            PrwProjectsObjectsFilterId.PROJECTION_DOC_STATUS_ID,
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
            input_id=PrwProjectsObjectsFilterId.PROJECTION_DOC_STATUS_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.projection_doc_statuses,
            result_matches=lambda result: same_option_text(result, value),
        )

    def stages(self) -> list[str]:
        return self.table_column_values_by_spec(PrwProjectsObjectsColumn.STAGE)

    def wait_stages(self) -> list[str]:
        return self.wait.until(lambda _: self.stages())

    def stage_options(self) -> list[str]:
        return self.dropdown_options(PrwProjectsObjectsFilterId.STAGE_ID)

    def stage_options_by_search(self, value: str) -> list[str]:
        return self.dropdown_options_by_search(
            PrwProjectsObjectsFilterId.STAGE_ID,
            value=value,
        )

    def apply_stage_filter(self, value: str) -> list[str]:
        return self.apply_dropdown_filter(
            input_id=PrwProjectsObjectsFilterId.STAGE_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.stages,
            result_matches=lambda result: same_option_text(result, value),
        )

    def enable_curators_columns(self) -> None:
        """Включить отображение колонок кураторов в таблице."""
        self.enable_optional_table_columns(PrwProjectsObjectsColumn.PROJECTOR_CURATOR)
        self.wait_table_column(PrwProjectsObjectsColumn.PROJECTOR_CURATOR)
        self.wait_table_column(PrwProjectsObjectsColumn.PLANNING_CURATOR)
