"""Базовая логика фильтров и таблиц."""
from collections.abc import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from components.ant_select import AntSelect
from components.ant_table import AntTable
from components.schemas.ant_table_schema import AntTableColumn
from components.date_input import DateInput
from components.text_input import TextInput
from pages.base_page import BasePage


class FilteredTablePage(BasePage):
    """
    PageObject базовый.
    Описывает работу с фильтрами и таблицами.
    """
    SEARCH_BUTTON = (
        By.XPATH,
        "//button[@type='submit' and .//span[normalize-space()='Найти']]",
    )

    def filters_by_ids(self, filter_ids: list[str]) -> dict[str, WebElement]:
        """Возвращает фильтры страницы по списку ID."""
        return self.elements_by_ids(filter_ids)

    def text_input(self, input_id: str) -> TextInput:
        """Создает объект для работы с текстовым полем."""
        return TextInput(self.driver, self.wait, input_id)

    def date_input(self, input_id: str) -> DateInput:
        """Создает объект для работы с полем даты."""
        return DateInput(self.driver, self.wait, input_id)

    def dropdown_options(self, input_id: str) -> list[str]:
        """Возвращает видимые значения выпадающего списка."""
        return AntSelect(self.driver, self.wait, input_id).options()

    def dropdown_options_by_search(
        self, 
        input_id: str,
        value: str
    ) -> list[str]:
        """Возвращает значения выпадающего списка после ввода поиска."""
        return AntSelect(self.driver, self.wait, input_id).search_options(value)

    def select_dropdown_option(
        self,
        input_id: str,
        value: str,
        search_value: str | None = None,
    ) -> None:
        """Выбирает значение в выпадающем списке."""
        AntSelect(self.driver, self.wait, input_id).select_option(
            value=value,
            search_value=search_value,
        )

    def table_column_values(
        self,
        column_index: int,
        keep_empty: bool = False,
    ) -> list[str]:
        """Возвращает значения колонки таблицы по индексу."""
        return AntTable(self.driver, self.wait).column_values(
            column_index,
            keep_empty=keep_empty,
        )

    def table_column_index_by_header(self,header_texts: tuple[str, ...]) -> int | None:
        """ 
        Возвращает индекс колонки по текстам заголовков.

        Используется для таблиц со сложной шапкой,
        где колонка может определяться несколькими уровнями заголовков.
        """
        return AntTable(self.driver, self.wait).column_index_by_header(header_texts)

    def table_column_index(self, column: AntTableColumn) -> int | None:
        """Возвращает индекс колонки по спецификации."""
        return AntTable(self.driver, self.wait).column_index(column)

    def table_column_values_by_header(self,header_texts: tuple[str, ...],) -> list[str]:
        """Возвращает значения колонки по текстам заголовков."""
        return AntTable(self.driver, self.wait).column_values_by_header(header_texts)

    def table_column_values_by_spec(
        self,
        column: AntTableColumn,
        keep_empty: bool = False,
    ) -> list[str]:
        """
        Возвращает значения колонки по спецификации.

        Если колонка является опциональной, сначала включает ее
        через соответствующий checkbox.
        """
        self.enable_optional_table_columns(column)
        self.wait_table_column(column)

        return AntTable(self.driver, self.wait).column_values_by_spec(
            column,
            keep_empty=keep_empty,
        )

    def wait_table_column(self, column: AntTableColumn) -> int:
        """Ожидает появления колонки в таблице."""
        column_index_container = self.wait.until(
            lambda _: (
                (index,)
                if (index := self.table_column_index(column)) is not None
                else False
            )
        )

        return column_index_container[0]

    def enable_optional_table_columns(self, column: AntTableColumn) -> None:
        """Включает опциональную колонку таблицы, если для нее указан checkbox."""
        if column.checkbox_label:
            self.enable_table_columns_checkbox(column.checkbox_label)

    def enable_table_columns_checkbox(self, label: str) -> None:
        """Включает checkbox дополнительной колонки таблицы."""
        checkbox = self.find_table_columns_checkbox(label)

        if checkbox.is_selected():
            return

        self.js_click(self.find_table_columns_checkbox_label(label))
        self.wait.until(
            lambda _: self.find_table_columns_checkbox(label).is_selected()
        )

    def find_table_columns_checkbox(self, label: str) -> WebElement:
        """Находит input checkbox дополнительной колонки таблицы."""
        return self.find(
            (
                By.XPATH,
                "//label[contains(@class, 'ant-checkbox-wrapper')"
                f" and .//span[normalize-space()='{label}']]"
                "//input[@type='checkbox']",
            )
        )

    def find_table_columns_checkbox_label(self, label: str) -> WebElement:
        """
        Находит label checkbox дополнительной колонки таблицы.

        Используется для клика по checkbox через label.
        """
        return self.find(
            (
                By.XPATH,
                "//label[contains(@class, 'ant-checkbox-wrapper')"
                f" and .//span[normalize-space()='{label}']]",
            )
        )

    def submit_filters(self) -> None:
        """Нажимает кнопку 'Найти' для применения фильтров."""
        self.js_click(self.clickable(self.SEARCH_BUTTON))

    def search_text_filter(
        self,
        input_id: str,
        value: str,
        result_getter: Callable[[], list[str]],
        ignore_case: bool = False,
    ) -> list[str]:
        """Заполняет текстовый фильтр, применяет поиск и возвращает результат."""
        before_values = result_getter()

        self.text_input(input_id).fill(value)
        self.submit_filters()

        self.wait.until(
            lambda _: self._search_finished(
                current_values=result_getter(),
                before_values=before_values,
                expected_value=value,
                ignore_case=ignore_case,
            )
        )

        return result_getter()

    def _search_finished(
        self,
        current_values: list[str],
        before_values: list[str],
        expected_value: str,
        ignore_case: bool,
    ) -> bool:
        """Проверяет, завершился ли поиск по текстовому фильтру."""
        if current_values != before_values:
            return True

        if not current_values:
            return self.table_is_empty()

        if ignore_case:
            expected_value = expected_value.casefold()

            return all(
                expected_value in current_value.casefold()
                for current_value in current_values
            )

        return all(expected_value in current_value for current_value in current_values)

    def apply_dropdown_filter(
        self,
        input_id: str,
        value: str,
        result_getter: Callable[[], list[str]],
        result_matches: Callable[[str], bool],
        search_value: str | None = None,
    ) -> list[str]:
        """Выбирает значение в выпадающем фильтре и применяет поиск."""
        self.select_dropdown_option(
            input_id=input_id,
            value=value,
            search_value=search_value,
        )
        self.submit_filters()
        self.wait.until(
            lambda _: self._dropdown_filter_applied(
                current_values=result_getter(),
                result_matches=result_matches,
            )
        )

        return result_getter()

    def _dropdown_filter_applied(
        self,
        current_values: list[str],
        result_matches: Callable[[str], bool],
    ) -> bool:
        """Проверяет, применился ли выпадающий фильтр."""
        if current_values and all(result_matches(value) for value in current_values):
            return True

        return self.table_is_empty()

    def table_is_empty(self) -> bool:
        """Проверяет, отображается ли пустое состояние таблицы."""
        empty_blocks = self.driver.find_elements(
            By.CSS_SELECTOR,
            ".ant-empty-description",
        )

        return any(block.is_displayed() for block in empty_blocks)
