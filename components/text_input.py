"""
Обертка для работы с текстовыми input-полями.

Модуль скрывает Selenium-детали заполнения обычных input'ов:
ожидание появления поля, прокрутку к элементу, устойчивый клик,
чтение текущего значения и текста ошибки валидации.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from components.element_actions import ElementActions


class TextInput:
    """Компонент для работы с текстовым input по HTML id."""
    def __init__(self, driver: WebDriver, wait: WebDriverWait, input_id: str):
        self.driver = driver
        self.wait = wait
        self.input_id = input_id
        self.actions = ElementActions(driver)

    def fill(self, value: str) -> None:
        """
        Заполняет input указанным значением.

        Метод ждет появления элемента, прокручивает к нему страницу, кликает,
        очищает текущее значение и вводит новый текст.
        """
        element = self.wait.until(EC.presence_of_element_located((By.ID, self.input_id)))
        self.actions.scroll_into_view(element)
        self.actions.click(element)
        element.clear()
        element.send_keys(value)

    def value(self) -> str:
        """Возвращает текущее значение input."""
        element = self.wait.until(EC.presence_of_element_located((By.ID, self.input_id)))
        return element.get_attribute("value") or ""

    def error_text(self, timeout: float | None = None) -> str:
        """Возвращает текст ошибки валидации для input."""
        wait = WebDriverWait(self.driver, timeout) if timeout is not None else self.wait
        error = wait.until(
            EC.visibility_of_element_located((By.ID, f"{self.input_id}_help"))
        )
        return error.text.strip()
