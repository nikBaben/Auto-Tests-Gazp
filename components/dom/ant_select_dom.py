"""DOM-адаптер для работы с Ant Design Select."""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from components.schemas import (
    AntSelectOption,
    ScrollHolderInfo,
    ScrollState,
)


"""
JavaScript-функция поиска активного dropdown 
для конкретного Ant Select.
"""
ACTIVE_DROPDOWN_SCRIPT = """
function activeDropdown(inputId) {
    const listId = `${inputId}_list`;
    const dropdowns = Array.from(
        document.querySelectorAll(".ant-select-dropdown")
    ).filter((item) => item.querySelector(`[id="${listId}"]`));

    return dropdowns.find((item) => {
        const style = window.getComputedStyle(item);
        return style.display !== "none"
            && style.visibility !== "hidden"
            && !item.classList.contains("ant-select-dropdown-hidden")
            && item.querySelector(`[id="${listId}"]`);
    });
}
"""


class AntSelectDom:
    """
    DOM-адаптер для Ant Design Select.

    JavaScript-операции, которые сложно или нестабильно
    выполнять обычными Selenium-локаторами.
    """
    def __init__(self, driver: WebDriver, input_id: str):
        self.driver = driver
        self.input_id = input_id

    def active_dropdown_is_visible(self) -> bool:
        """Проверяет, виден ли активный dropdown текущего Ant Select."""
        return self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            return Boolean(activeDropdown(arguments[0]));
            """,
            self.input_id,
        )

    def visible_option_items(self) -> list[AntSelectOption]:
        """Возвращает видимые option элементы активного dropdown."""
        items = self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            const listId = `${{arguments[0]}}_list`;
            const dropdown = activeDropdown(arguments[0]);

            if (!dropdown) {{
                return [];
            }}

            return Array.from(
                dropdown.querySelectorAll(`[id="${{listId}}"] div[role="option"]`)
            ).map((option, fallbackIndex) => {{
                const indexMatch = option.id.match(/_(\\d+)$/);

                return {{
                    key: indexMatch
                        ? `index:${{indexMatch[1]}}`
                        : `fallback:${{fallbackIndex}}:${{option.innerText.trim()}}`,
                    index: indexMatch ? Number(indexMatch[1]) : null,
                    text: option.innerText.trim(),
                }};
            }});
            """,
            self.input_id,
        )

        return [AntSelectOption.model_validate(item) for item in items]

    def visible_option_element(self, value: str) -> WebElement | None:
        """
        Ищет видимый option элемент по тексту.

        Сначала ищет точное совпадение после нормализации пробелов.
        Если точного совпадения нет, ищет частичное совпадение.
        """
        return self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            const listId = `${{arguments[0]}}_list`;
            const expected = normalize(arguments[1]);
            const dropdown = activeDropdown(arguments[0]);

            if (!dropdown) {{
                return null;
            }}

            const options = Array.from(
                dropdown.querySelectorAll(`[id="${{listId}}"] div[role="option"]`)
            );

            return options.find((option) => normalize(option.innerText) === expected)
                || options.find((option) => normalize(option.innerText).includes(expected))
                || null;

            function normalize(value) {{
                return value.replace(/\\s+/g, " ").trim();
            }}
            """,
            self.input_id,
            value,
        )

    def scroll_to_top(self) -> None:
        """
        Прокручивает dropdown текущего Ant Select в начало списка.

        Используется перед сбором всех options или перед поиском значения,
        чтобы начать обход виртуализированного списка с первого элемента.
        """
        self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            const dropdown = activeDropdown(arguments[0]);
            const holder = dropdown?.querySelector(".rc-virtual-list-holder");

            if (holder) {{
                holder.scrollTop = 0;
                holder.dispatchEvent(new Event("scroll", {{ bubbles: true }}));
            }}
            """,
            self.input_id,
        )

    def scroll_holder_info(self) -> ScrollHolderInfo:
        """Возвращает информацию о scroll-контейнере dropdown."""
        info = self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            const dropdown = activeDropdown(arguments[0]);
            const holder = dropdown?.querySelector(".rc-virtual-list-holder");

            if (!holder) {{
                return {{
                    holder: null,
                    scroll_step: 0,
                }};
            }}

            const option = holder.querySelector('div[role="option"]');
            const optionHeight = option?.getBoundingClientRect().height || 32;
            const visibleHeight = holder.clientHeight || optionHeight * 8;
            const scrollStep = Math.max(optionHeight * 8, visibleHeight * 0.9);

            return {{
                holder,
                scroll_step: scrollStep,
            }};
            """,
            self.input_id,
        )

        return ScrollHolderInfo.model_validate(info)

    def scroll_down(self, scroll_step: float) -> None:
        """Прокручивает dropdown вниз на указанный шаг."""
        self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            const dropdown = activeDropdown(arguments[0]);
            const holder = dropdown?.querySelector(".rc-virtual-list-holder");

            if (!holder) {{
                return;
            }}

            const maxScrollTop = holder.scrollHeight - holder.clientHeight;
            const previousScrollTop = holder.scrollTop;
            holder.scrollTop = Math.min(
                maxScrollTop,
                previousScrollTop + arguments[1]
            );
            holder.dispatchEvent(new Event("scroll", {{ bubbles: true }}));
            """,
            self.input_id,
            scroll_step,
        )

    def scroll_state(self) -> ScrollState:
        """Возвращает текущее состояние scroll-контейнера dropdown."""
        state = self.driver.execute_script(
            f"""
            {ACTIVE_DROPDOWN_SCRIPT}

            const dropdown = activeDropdown(arguments[0]);
            const holder = dropdown?.querySelector(".rc-virtual-list-holder");

            if (!holder) {{
                return {{
                    scroll_top: 0,
                    scroll_height: 0,
                    client_height: 0,
                    is_bottom: true,
                }};
            }}

            const maxScrollTop = holder.scrollHeight - holder.clientHeight;

            return {{
                scroll_top: holder.scrollTop,
                scroll_height: holder.scrollHeight,
                client_height: holder.clientHeight,
                is_bottom: holder.scrollTop >= maxScrollTop,
            }};
            """,
            self.input_id,
        )

        return ScrollState.model_validate(state)
