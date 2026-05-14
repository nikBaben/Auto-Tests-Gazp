"""
Обертка для работы с Ant Design Select.

Модуль скрывает Selenium-детали работы с `ant-select`: открытие dropdown,
получение полного списка опций, поиск по опциям и выбор значения.
Для виртуализированных списков используется `AntSelectOptionCollector`.
"""
from typing import cast

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from components.api_select_options import ApiSelectOptions
from components.dom.ant_select_dom import AntSelectDom
from components.ant_select_option_collector import AntSelectOptionCollector
from components.element_actions import ElementActions


class AntSelect:
    """
    Компонент для работы с одним Ant Design Select.

    Экземпляр привязан к конкретному select по HTML id input-элемента.
    Класс умеет открывать и закрывать dropdown, читать опции, искать значения
    и выбирать нужную option.
    """
    def __init__(self, driver: WebDriver, wait: WebDriverWait, input_id: str):
        self.driver = driver
        self.wait = wait
        self.input_id = input_id
        self.dom = AntSelectDom(driver, input_id)
        self.actions = ElementActions(driver)
        self.option_collector = AntSelectOptionCollector(
            driver=driver,
            wait=wait,
            input_id=input_id,
            dom=self.dom,
        )

    def options(self) -> list[str]:
        """
        Возвращает полный список опций select.

        Сначала пытается получить опции из данных страницы через `ApiSelectOptions`.
        Если это невозможно, открывает dropdown и собирает все DOM-опции через
        `AntSelectOptionCollector`.
        """
        api_options = ApiSelectOptions(self.driver).options(self.input_id)

        if api_options is not None:
            return api_options

        try:
            self.open()
            return self.option_collector.all_options()
        finally:
            self.close()

    def search_options(self, value: str) -> list[str]:
        """
        Возвращает опции, найденные через встроенный поиск select.

        Метод открывает dropdown, вводит значение в input и ждет, пока все видимые
        опции будут соответствовать введенному тексту.
        """
        try:
            self.open()
            input_element = self.wait.until(
                EC.element_to_be_clickable((By.ID, self.input_id))
            )
            self.actions.click(input_element)
            input_element.send_keys(value)
            self.wait.until(
                lambda _: (input_element.get_attribute("value") or "") == value
            )
            return self.wait.until(lambda _: self.visible_options_matching(value))
        finally:
            self.close()

    def select_option(self, value: str, search_value: str | None = None) -> None:
        """
        Выбирает option в dropdown.

        Метод открывает select, вводит поисковое значение, ждет появления нужной
        option и кликает по ней.
        """
        search_value = search_value or value

        try:
            self.open()
            input_element = self.wait.until(
                EC.element_to_be_clickable((By.ID, self.input_id))
            )
            self.actions.click(input_element)
            input_element.send_keys(search_value)
            self.wait.until(
                lambda _: (input_element.get_attribute("value") or "") == search_value
            )
            option = cast(
                WebElement,
                self.wait.until(lambda _: self.visible_option_element(value)),
            )
            self.actions.click(option)
        finally:
            self.close()

    def visible_options_matching(self, value: str) -> list[str]:
        """
        Возвращает видимые опции, если все они содержат поисковый текст.
        Используется как условие ожидания после ввода в поиск select.
        """
        options = self.visible_options()
        needle = value.casefold()

        if options and all(needle in option.casefold() for option in options):
            return options

        return []

    def visible_options(self) -> list[str]:
        """Возвращает тексты текущих видимых опций активного dropdown."""
        return [
            option.text
            for option in self.option_collector.visible_option_items()
        ]

    def visible_option_element(self, value: str) -> WebElement | None:
        """Возвращает DOM-элемент видимой option по ее тексту."""
        return self.dom.visible_option_element(value)

    def active_dropdown_is_visible(self) -> bool:
        """Проверяет, что dropdown текущего select открыт и видим."""
        return self.dom.active_dropdown_is_visible()

    def open(self) -> None:
        """
        Открывает dropdown текущего Ant Select.

        Метод находит wrapper select по input id, кликает по `.ant-select-selector`
        и ждет появления активного dropdown.
        """
        input_element = self.wait.until(
            EC.presence_of_element_located((By.ID, self.input_id))
        )
        select = input_element.find_element(
            By.XPATH,
            "./ancestor::div[contains(@class, 'ant-select')]",
        )
        selector = select.find_element(By.CSS_SELECTOR, ".ant-select-selector")

        self.wait.until(lambda _: selector.is_displayed())
        self.actions.click(selector)
        self.wait.until(lambda _: self.active_dropdown_is_visible())

    def close(self) -> None:
        """Закрывает активный dropdown нажатием Escape."""
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
