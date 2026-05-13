from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class ElementActions:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def scroll_into_view(self, element: WebElement) -> None:
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )

    def click(self, element: WebElement) -> None:
        try:
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)
