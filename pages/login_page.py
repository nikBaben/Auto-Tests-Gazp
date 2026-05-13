from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


class LoginPage(BasePage):
    """PageObject страницы авторизации."""
    
    USER_SELECT = (By.XPATH, "//select | //div[contains(@class, 'ant-select')]")
    USER_ID_INPUT = (By.ID, "userId")
    ANT_OPTIONS = (By.XPATH, "//div[contains(@class, 'ant-select-item-option')]")
    LOGIN_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(), 'Войти')] | //button[@type='submit']",
    )

    def login_as_user(self, user_index: int = 2) -> None:
        self.wait_for_login_state()

        if self.is_authenticated():
            return

        if not self.is_login_form_visible():
            raise AssertionError("Не найдена форма входа и пользователь не авторизован.")

        self.select_user(user_index)
        self.submit()

    def wait_for_login_state(self) -> None:
        try:
            self.wait.until(
                lambda _: self.is_login_form_visible() or self.is_authenticated()
            )
        except TimeoutException as error:
            raise AssertionError(
                "Не удалось дождаться формы входа или авторизованной сессии."
            ) from error

    def is_login_form_visible(self) -> bool:
        return any(
            button.is_displayed()
            for button in self.driver.find_elements(*self.LOGIN_BUTTON)
        )

    def is_authenticated(self) -> bool:
        return "/auth" not in self.driver.current_url and any(
            element.is_displayed()
            for element in self.driver.find_elements(
                By.CSS_SELECTOR,
                "._user_card_1gyvn_37, .ant-menu-item-selected",
            )
        )

    def select_user(self, user_index: int) -> None:
        self.find(self.USER_SELECT)

        native_selects = [
            select
            for select in self.driver.find_elements(By.TAG_NAME, "select")
            if select.is_displayed()
        ]
        if native_selects:
            options = Select(native_selects[0]).options
            self._check_option_index(options, user_index)
            Select(native_selects[0]).select_by_index(user_index)
            return

        user_input = self.clickable(self.USER_ID_INPUT)
        user_input.click()
        options = self.wait.until(EC.visibility_of_all_elements_located(self.ANT_OPTIONS))
        self._check_option_index(options, user_index)
        self.wait.until(EC.element_to_be_clickable(options[user_index])).click()

    def submit(self) -> None:
        current_url = self.driver.current_url
        self.js_click(self.clickable(self.LOGIN_BUTTON))
        self.wait.until(EC.url_changes(current_url))

    @staticmethod
    def _check_option_index(options: list, user_index: int) -> None:
        if user_index >= len(options):
            raise AssertionError(
                f"Пользователь с индексом {user_index} не найден. "
                f"Доступно вариантов: {len(options)}"
            )
