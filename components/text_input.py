from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from components.element_actions import ElementActions


class TextInput:
    def __init__(self, driver: WebDriver, wait: WebDriverWait, input_id: str):
        self.driver = driver
        self.wait = wait
        self.input_id = input_id
        self.actions = ElementActions(driver)

    def fill(self, value: str) -> None:
        element = self.wait.until(EC.presence_of_element_located((By.ID, self.input_id)))
        self.actions.scroll_into_view(element)
        self.actions.click(element)
        element.clear()
        element.send_keys(value)

    def value(self) -> str:
        element = self.wait.until(EC.presence_of_element_located((By.ID, self.input_id)))
        return element.get_attribute("value") or ""

    def error_text(self, timeout: float | None = None) -> str:
        wait = WebDriverWait(self.driver, timeout) if timeout is not None else self.wait
        error = wait.until(
            EC.visibility_of_element_located((By.ID, f"{self.input_id}_help"))
        )
        return error.text.strip()
