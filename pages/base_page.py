"""Базовая логика страницы."""
from typing import ClassVar, Self
from collections.abc import Iterable

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


Locator = tuple[str, str]


class BasePage:
    """
    PageObject базовый.
    Описывает общую логику работы со страницей.
    """
    PATH: ClassVar[str] = ""
    FILTER_IDS: ClassVar[Iterable[str]] = ()

    def __init__(
        self, 
        driver: WebDriver, 
        wait: WebDriverWait, 
        base_url: str
    ):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url.rstrip("/")

    def open(self) -> Self:
        """Открывает страницу по пути PATH."""
        self.open_path(self.PATH)
        return self

    def open_path(self, path: str) -> None:
        """Открывает страницу по указанному пути."""
        normalized_path = path if path.startswith("/") else f"/{path}"
        self.driver.get(f"{self.base_url}{normalized_path}")

    def filters(self) -> dict[str, WebElement]:
        """ Возвращает словарь фильтров страницы."""
        return self.elements_by_ids(self.FILTER_IDS)

    def find(self, locator: Locator) -> WebElement:
        """Ожидает появления элемента в DOM"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def clickable(self, locator: Locator) -> WebElement:
        """Ожидает, пока элемент станет кликабельным."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def js_click(self, element: WebElement) -> None:
        """
        Выполняет клик через JavaScript.

        Используется для элементов,
        которые некорректно нажимаются
        обычным Selenium click().
        """
        self.driver.execute_script("arguments[0].click();", element)

    def elements_by_ids(self,element_ids: Iterable[str]) -> dict[str, WebElement]:
        """
        Находит элементы по списку ID
        и возвращает их словарем.
        """
        elements = {}

        for element_id in element_ids:
            element = self.find((By.ID, element_id))
            elements[self.element_title(element_id, element)] = element

        return elements

    def element_title(
        self, 
        element_id: str,
        element: WebElement
    ) -> str:
        """Определяет отображаемое название элемента."""
        label = self.driver.find_elements(By.CSS_SELECTOR, f"label[for='{element_id}']")

        if label and label[0].text.strip():
            return label[0].text.strip()

        for attribute in ("title", "placeholder", "aria-label", "class_title"):
            value = element.get_attribute(attribute)
            if value:
                return value.strip()

        return element_id