from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from components.ant_table_dom import AntTableDom
from components.ant_table_schemas import AntTableColumn


class AntTable:
    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait
        self.dom = AntTableDom(driver)

    def column_values(
        self,
        column_index: int,
        keep_empty: bool = False,
    ) -> list[str]:
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table"))
        )
        return self.dom.column_values(column_index, keep_empty=keep_empty)

    def column_index_by_header(self, header_texts: tuple[str, ...]) -> int | None:
        return self.column_index(AntTableColumn(headers=header_texts))

    def column_index(self, column: AntTableColumn) -> int | None:
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table"))
        )
        return self.dom.column_index(column)

    def column_values_by_header(
        self,
        header_texts: tuple[str, ...],
        keep_empty: bool = False,
    ) -> list[str]:
        return self.column_values_by_spec(
            AntTableColumn(headers=header_texts),
            keep_empty=keep_empty,
        )

    def column_values_by_spec(
        self,
        column: AntTableColumn,
        keep_empty: bool = False,
    ) -> list[str]:
        column_index = self.column_index(column)

        if column_index is None:
            raise AssertionError(
                "Не найдена колонка таблицы по заголовку.\n"
                f"Ожидалась колонка: {column}"
            )

        return self.column_values(column_index, keep_empty=keep_empty)
