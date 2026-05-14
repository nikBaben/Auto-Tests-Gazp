"""
Обертка для работы с Ant Design DatePicker.
Модуль выбирает даты через календарь Ant DatePicker, а не через прямой ввод
строки.
"""
from datetime import date, datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from components.element_actions import ElementActions


class DateInput:
    """
    Компонент для выбора даты в Ant Design DatePicker.

    Экземпляр привязан к конкретному input по HTML id. Дата передается и
    проверяется в формате `ДД.ММ.ГГГГ`.
    """
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
        """
        Выбирает дату в поле.

        Метод является унифицированным alias для `select_date`, чтобы Page Object
        мог работать с датой так же, как с обычным input.
        """
        self.select_date(value)

    def select_date(self, value: str) -> None:
        """Выбирает дату через календарь DatePicker."""
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
        """Возвращает текущее значение input DatePicker."""
        element = self.wait.until(EC.presence_of_element_located((By.ID, self.input_id)))
        return element.get_attribute("value") or ""

    def go_to_month(self, target_date: date) -> None:
        """
        Переходит в календаре к месяцу целевой даты.

        Метод кликает кнопки предыдущего или следующего месяца, пока открытый
        календарь не покажет нужные месяц и год
        """
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
        """Кликает день целевой даты в открытом календаре."""
        day = self.visible_dropdown().find_element(
            By.CSS_SELECTOR,
            f"td[title='{target_date.isoformat()}'] .ant-picker-cell-inner",
        )
        self.actions.click(day)

    def panel_year_month(self) -> tuple[int, int]:
        """Возвращает год и месяц, которые сейчас открыты в DatePicker."""
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
        """Возвращает видимый dropdown текущего DatePicker."""
        return self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".ant-picker-dropdown:not(.ant-picker-dropdown-hidden)",
                )
            )
        )

    def close_open_dropdown(self) -> None:
        """Закрывает открытый DatePicker dropdown нажатием Escape."""
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    def parse_date(self, value: str) -> date:
        """Преобразует строку `ДД.ММ.ГГГГ` в объект date."""
        return datetime.strptime(value, self.DATE_FORMAT).date()
