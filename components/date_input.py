from __future__ import annotations

from datetime import date, datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from components.element_actions import ElementActions


class DateInput:
    DATE_FORMAT = "%d.%m.%Y"
    MONTHS = {
        "Янв": 1,
        "Январь": 1,
        "Фев": 2,
        "Февраль": 2,
        "Мар": 3,
        "Март": 3,
        "Апр": 4,
        "Апрель": 4,
        "Май": 5,
        "Июн": 6,
        "Июнь": 6,
        "Июл": 7,
        "Июль": 7,
        "Авг": 8,
        "Август": 8,
        "Сен": 9,
        "Сентябрь": 9,
        "Окт": 10,
        "Октябрь": 10,
        "Ноя": 11,
        "Ноябрь": 11,
        "Дек": 12,
        "Декабрь": 12,
    }

    def __init__(self, driver: WebDriver, wait: WebDriverWait, input_id: str):
        self.driver = driver
        self.wait = wait
        self.input_id = input_id
        self.actions = ElementActions(driver)

    def fill(self, value: str) -> None:
        self.select_date(value)

    def select_date(self, value: str) -> None:
        target_date = self.parse_date(value)
        self.close_open_dropdown()
        element = self.wait.until(EC.element_to_be_clickable((By.ID, self.input_id)))
        self.actions.scroll_into_view(element)
        self.actions.click(element)
        self.go_to_month(target_date)
        self.click_day(target_date)
        self.wait.until(lambda _: self.value() == value)
        self.close_open_dropdown()

    def value(self) -> str:
        element = self.wait.until(EC.presence_of_element_located((By.ID, self.input_id)))
        return element.get_attribute("value") or ""

    def go_to_month(self, target_date: date) -> None:
        for _ in range(240):
            current_year, current_month = self.panel_year_month()
            month_delta = (
                (target_date.year - current_year) * 12
                + target_date.month
                - current_month
            )

            if month_delta == 0:
                return

            if month_delta > 0:
                button = self.visible_dropdown().find_element(
                    By.CSS_SELECTOR,
                    ".ant-picker-header-next-btn",
                )
            else:
                button = self.visible_dropdown().find_element(
                    By.CSS_SELECTOR,
                    ".ant-picker-header-prev-btn",
                )

            self.actions.click(button)

        raise AssertionError(f"Не удалось открыть месяц для даты {target_date}")

    def click_day(self, target_date: date) -> None:
        day = self.visible_dropdown().find_element(
            By.CSS_SELECTOR,
            f"td[title='{target_date.isoformat()}'] .ant-picker-cell-inner",
        )
        self.actions.click(day)

    def panel_year_month(self) -> tuple[int, int]:
        dropdown = self.visible_dropdown()
        month_text = dropdown.find_element(
            By.CSS_SELECTOR,
            ".ant-picker-month-btn",
        ).text.strip()
        year_text = dropdown.find_element(
            By.CSS_SELECTOR,
            ".ant-picker-year-btn",
        ).text.strip()

        return int(year_text), self.MONTHS[month_text]

    def visible_dropdown(self) -> WebElement:
        return self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".ant-picker-dropdown:not(.ant-picker-dropdown-hidden)",
                )
            )
        )

    def close_open_dropdown(self) -> None:
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    def parse_date(self, value: str) -> date:
        return datetime.strptime(value, self.DATE_FORMAT).date()
