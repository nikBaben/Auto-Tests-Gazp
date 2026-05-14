"""
Устойчивые действия с Selenium WebElement.

Модуль содержит небольшие обертки над частыми действиями Selenium,
которые в UI на Ant Design могут быть нестабильными: прокрутка элемента
в видимую область и клик с fallback на JavaScript.
"""
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class ElementActions:
    """Helper для устойчивых действий с DOM-элементами."""
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def scroll_into_view(self, element: WebElement) -> None:
        """Прокручивает страницу так, чтобы элемент оказался в центре viewport."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )

    def click(self, element: WebElement) -> None:
        """
        Кликает по элементу с fallback на JavaScript click.

        Сначала выполняется обычный Selenium click. Если браузер не смог кликнуть
        по элементу из-за перекрытия, нестабильного состояния или другой
        `WebDriverException`, выполняется `arguments[0].click()` через JavaScript.
        """
        try:
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)
