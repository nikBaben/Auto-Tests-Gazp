"""Схемы для описания колонок Ant Design таблицы."""
from pydantic import BaseModel, ConfigDict


class AntTableColumn(BaseModel):
    """
    Описание колонки таблицы 
    без привязки к фиксированному индексу.
    """
    model_config = ConfigDict(frozen=True)

    headers: tuple[str, ...] = ()
    header_paths: tuple[tuple[str, ...], ...] = ()
    checkbox_label: str | None = None

