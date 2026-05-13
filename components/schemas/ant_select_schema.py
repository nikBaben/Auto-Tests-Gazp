"""Схемы для описания работы с Ant Design Select."""
from pydantic import BaseModel, ConfigDict
from selenium.webdriver.remote.webelement import WebElement


class ScrollHolderInfo(BaseModel):
    """
    Информация о scroll-контейнере Ant Design компонента.

    Используется для хранения:
    - элемента контейнера со скроллом;
    - шага прокрутки.

    Применяется при работе с виртуализированными списками,
    где элементы подгружаются во время прокрутки.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    holder: WebElement | None
    scroll_step: float


class ScrollState(BaseModel):
    """Текущее состояние scroll-контейнера."""
    scroll_top: float
    scroll_height: float
    client_height: float
    is_bottom: bool


class AntSelectOption(BaseModel):
    """Описание option элемента Ant Design Select."""
    key: str
    index: int | None
    text: str
