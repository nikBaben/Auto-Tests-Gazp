"""
Сборщик опций виртуализированного Ant Design Select.

Ant Design Select может рендерить в DOM только видимую часть опций.
Этот модуль прокручивает выпадающий список, собирает видимые элементы,
контролирует пропущенные индексы и возвращает полный список option-текстов
в исходном порядке.
"""
from time import sleep

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from components.dom.ant_select_dom import AntSelectDom
from components.schemas.ant_select_schema import AntSelectOption


class AntSelectOptionCollector:
    """
    Собирает все значения из dropdown Ant Select с виртуальной прокруткой.
    """
    SCROLL_PAUSE_SECONDS = 0.2
    MAX_SCROLL_STEPS = 500
    STABLE_BOTTOM_CHECKS = 3
    MAX_STALLED_SCROLL_STEPS = 8

    def __init__(
        self,
        driver: WebDriver,
        wait: WebDriverWait,
        input_id: str,
        dom: AntSelectDom,
    ):
        self.driver = driver
        self.wait = wait
        self.input_id = input_id
        self.dom = dom

    def all_options(self) -> list[str]:
        """Собирает все option-тексты из dropdown."""
        self.scroll_to_top()
        options_by_key: dict[str, str] = {}
        fallback_order: list[str] = []
        stable_bottom_checks = 0
        previous_bottom_signature: tuple | None = None
        stalled_scroll_steps = 0
        previous_progress_signature: tuple | None = None

        for _ in range(self.MAX_SCROLL_STEPS):
            self.add_visible_options(options_by_key, fallback_order)
            visible_signature = self.visible_options_signature()

            self.scroll_down()
            self.wait_visible_options_updated(visible_signature)
            self.add_visible_options(options_by_key, fallback_order)

            current_state = self.dom.scroll_state()
            progress_signature = (
                len(options_by_key),
                self.visible_options_signature(),
                current_state.scroll_top,
                current_state.scroll_height,
            )

            if progress_signature == previous_progress_signature:
                stalled_scroll_steps += 1
            else:
                stalled_scroll_steps = 0
                previous_progress_signature = progress_signature

            if current_state.is_bottom:
                current_signature = (
                    len(options_by_key),
                    current_state.scroll_top,
                    current_state.scroll_height,
                    self.missing_index_ranges(options_by_key),
                )

                if current_signature == previous_bottom_signature:
                    stable_bottom_checks += 1
                else:
                    stable_bottom_checks = 1
                    previous_bottom_signature = current_signature

                if (
                    stable_bottom_checks >= self.STABLE_BOTTOM_CHECKS
                    and not self.missing_index_ranges(options_by_key)
                ):
                    return self.sorted_options(options_by_key, fallback_order)
            else:
                stable_bottom_checks = 0
                previous_bottom_signature = None

            if stalled_scroll_steps >= self.MAX_STALLED_SCROLL_STEPS:
                raise AssertionError(
                    "Не удалось продвинуть прокрутку выпадающего списка.\n"
                    f"Поле: {self.input_id}\n"
                    f"Пропущенные индексы: {self.missing_index_ranges(options_by_key)}\n"
                    f"Собранные значения: {self.sorted_options(options_by_key, fallback_order)}"
                )

        raise AssertionError(
            "Не удалось прокрутить выпадающий список до конца.\n"
            f"Поле: {self.input_id}\n"
            f"Пропущенные индексы: {self.missing_index_ranges(options_by_key)}\n"
            f"Собранные значения: {self.sorted_options(options_by_key, fallback_order)}"
        )

    def wait_visible_options_updated(
        self,
        previous_signature: tuple[str, ...],
    ) -> None:
        """
        Ждет обновления набора видимых опций после прокрутки.

        Ожидание завершается, когда сигнатура видимых опций изменилась
        или dropdown уже находится внизу списка.
        """
        for _ in range(6):
            sleep(self.SCROLL_PAUSE_SECONDS)

            if self.visible_options_signature() != previous_signature:
                return

            if self.dom.scroll_state().is_bottom:
                return

    def visible_option_items(self) -> list[AntSelectOption]:
        """
        Возвращает видимые option-элементы активного dropdown.
        Перед чтением ждет, что dropdown открыт и видим.
        """
        self.wait.until(lambda _: self.dom.active_dropdown_is_visible())

        return self.dom.visible_option_items()

    def visible_options_signature(self) -> tuple[str, ...]:
        """
        Возвращает сигнатуру текущих видимых опций.

        Сигнатура строится по ключам option-элементов и используется,
        чтобы понять, изменился ли DOM после прокрутки.
        """
        return tuple(option.key for option in self.visible_option_items())

    def add_visible_options(
        self,
        options_by_key: dict[str, str],
        fallback_order: list[str],
    ) -> None:
        """Добавляет текущие видимые опции в накопитель."""
        for option in self.visible_option_items():
            key = option.key

            if key not in options_by_key:
                fallback_order.append(key)

            options_by_key[key] = option.text

    def sorted_options(
        self,
        options_by_key: dict[str, str],
        fallback_order: list[str],
    ) -> list[str]:
        """Возвращает собранные опции в правильном порядке."""
        def sort_key(key: str) -> tuple[int, int]:
            if key.startswith("index:"):
                return 0, int(key.removeprefix("index:"))

            return 1, fallback_order.index(key)

        return [
            options_by_key[key]
            for key in sorted(options_by_key, key=sort_key)
        ]

    def missing_index_ranges(self, options_by_key: dict[str, str]) -> list[str]:
        """
        Возвращает диапазоны пропущенных индексов среди собранных опций.

        Используется для диагностики виртуального списка, когда прокрутка дошла
        до конца, но часть индексированных option-элементов не была собрана.
        """
        indexes = sorted(
            int(key.removeprefix("index:"))
            for key in options_by_key
            if key.startswith("index:")
        )

        if not indexes:
            return []

        missing_ranges: list[str] = []
        expected_index = indexes[0]

        for current_index in indexes:
            if current_index > expected_index:
                missing_ranges.append(
                    self.index_range_text(expected_index, current_index - 1)
                )

            expected_index = current_index + 1

        if indexes[0] != 0:
            missing_ranges.insert(0, self.index_range_text(0, indexes[0] - 1))

        return missing_ranges

    def index_range_text(self, start: int, end: int) -> str:
        """Форматирует пропущенный индекс или диапазон индексов для сообщения ошибки."""
        if start == end:
            return str(start)

        return f"{start}-{end}"

    def scroll_to_top(self) -> None:
        """Прокручивает активный dropdown в начало списка."""
        self.dom.scroll_to_top()
        sleep(self.SCROLL_PAUSE_SECONDS)

    def scroll_down(self) -> None:
        """
        Прокручивает активный dropdown вниз одним шагом.

        Метод использует несколько способов прокрутки: `PAGE_DOWN`, wheel action
        и прямую DOM-прокрутку. Это повышает устойчивость для разных реализаций
        Ant Select и браузерных состояний.
        """
        scroll_info = self.dom.scroll_holder_info()

        if not scroll_info.holder:
            return

        scroll_step = int(scroll_info.scroll_step)

        try:
            self.driver.find_element(By.ID, self.input_id).send_keys(Keys.PAGE_DOWN)
        except WebDriverException:
            pass

        try:
            origin = ScrollOrigin.from_element(scroll_info.holder)
            ActionChains(self.driver).scroll_from_origin(
                origin,
                0,
                scroll_step,
            ).perform()
        except WebDriverException:
            pass

        self.dom.scroll_down(scroll_step)
