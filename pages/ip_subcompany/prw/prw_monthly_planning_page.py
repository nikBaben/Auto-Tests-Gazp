from enum import StrEnum

from components.schemas.ant_table_schema import AntTableColumn
from pages.filtered_table_page import FilteredTablePage
from utils.value_matchers import (
    first_word,
    normalized_text,
    same_option_text,
    subcompany_code,
)


class PrwMonthlyPlanningFilterTitle(StrEnum):
    """Названия фильтров на странице Освоение ПИР ИП ДО."""
    SEARCH = "Поиск"
    SUBCOMPANY = "Код заказчика"
    REGION = "Регион"
    IP_VERSION = "Версия ИП"


class PrwMonthlyPlanningFilterId(StrEnum):
    SEARCH_ID = "search"
    SUBCOMPANY_ID = "subcompany_ids"
    REGION_ID = "region_ids"
    STAGE_ID = "stage_id"


class PrwMonthlyPlanningColumn:
    """Колонки таблицы на странице освоения ПИР."""

    STAGE = AntTableColumn(headers=("План/факт",))
    OBJECT_CODE = AntTableColumn(headers=("Код объекта",))
    SUBCOMPANY = AntTableColumn(headers=("Код заказчика", "Код зак."))
    REGION = AntTableColumn(headers=("Регион объекта", "Регион"))


class PrwMonthlyPlanningPage(FilteredTablePage):
    """
    Страница URL: /ip-subcompany/prw/monthly-planning
    Освоение ПИР ИП ДО.
    """
    PATH = "/ip-subcompany/prw/monthly-planning"
    FILTER_IDS = PrwMonthlyPlanningFilterId

    # Поиск
    def fill_search(self, value: str) -> None:
        self.text_input(PrwMonthlyPlanningFilterId.SEARCH_ID).fill(value)

    def search_value(self) -> str:
        return self.text_input(PrwMonthlyPlanningFilterId.SEARCH_ID).value()

    def object_codes(self) -> list[str]:
        return self.table_column_values_by_spec(
            PrwMonthlyPlanningColumn.OBJECT_CODE
        )

    def wait_object_codes(self) -> list[str]:
        return self.wait.until(lambda _: self.object_codes())

    def search_by_object_code(self, value: str) -> list[str]:
        return self.search_text_filter(
            input_id=PrwMonthlyPlanningFilterId.SEARCH_ID,
            value=value,
            result_getter=self.object_codes,
        )

    # Код заказчика
    def subcompany_codes(self) -> list[str]:
        return self.table_column_values_by_spec(PrwMonthlyPlanningColumn.SUBCOMPANY)

    def wait_subcompany_codes(self) -> list[str]:
        return self.wait.until(lambda _: self.subcompany_codes())

    def subcompany_options(self) -> list[str]:
        return self.dropdown_options(PrwMonthlyPlanningFilterId.SUBCOMPANY_ID)

    def subcompany_options_by_search(self, value: str) -> list[str]:
        return self.dropdown_options_by_search(
            PrwMonthlyPlanningFilterId.SUBCOMPANY_ID,
            value=value,
        )

    def apply_subcompany_filter(self, value: str) -> list[str]:
        code = subcompany_code(value)

        return self.apply_dropdown_filter(
            input_id=PrwMonthlyPlanningFilterId.SUBCOMPANY_ID,
            value=value,
            search_value=code,
            result_getter=self.subcompany_codes,
            result_matches=lambda result: normalized_text(result) == code,
        )

    # Регион
    def regions(self) -> list[str]:
        return self.table_column_values_by_spec(PrwMonthlyPlanningColumn.REGION)

    def wait_regions(self) -> list[str]:
        return self.wait.until(lambda _: self.regions())

    def region_options(self) -> list[str]:
        return self.dropdown_options(PrwMonthlyPlanningFilterId.REGION_ID)

    def region_options_by_search(self, value: str) -> list[str]:
        return self.dropdown_options_by_search(
            PrwMonthlyPlanningFilterId.REGION_ID,
            value=value,
        )

    def apply_region_filter(self, value: str) -> list[str]:
        return self.apply_dropdown_filter(
            input_id=PrwMonthlyPlanningFilterId.REGION_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.regions,
            result_matches=lambda result: same_option_text(result, value),
        )

    # Версия ИП
    def stages(self) -> list[str]:
        return self.table_column_values_by_spec(PrwMonthlyPlanningColumn.STAGE)

    def wait_stages(self) -> list[str]:
        return self.wait.until(lambda _: self.stages())

    def stage_options(self) -> list[str]:
        return self.dropdown_options(PrwMonthlyPlanningFilterId.STAGE_ID)

    def stage_options_by_search(self, value: str) -> list[str]:
        return self.dropdown_options_by_search(
            PrwMonthlyPlanningFilterId.STAGE_ID,
            value=value,
        )

    def apply_stage_filter(self, value: str) -> list[str]:
        return self.apply_dropdown_filter(
            input_id=PrwMonthlyPlanningFilterId.STAGE_ID,
            value=value,
            search_value=first_word(value),
            result_getter=self.stages,
            result_matches=lambda result: same_option_text(result, value),
        )
