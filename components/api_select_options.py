"""
Получение значений Ant Design Select через API-каталоги.

Ant Design Select может рендерить длинные списки виртуально: в DOM одновременно
присутствует только часть option-элементов, поэтому чтение всех значений через
прокрутку может быть медленным и нестабильным.
"""
from typing import Callable

from pydantic import BaseModel, ConfigDict
from selenium.webdriver.remote.webdriver import WebDriver


LabelGetter = Callable[[dict], str]


class SelectCatalog(BaseModel):
    """Описание API-каталога для конкретного Ant Select."""
    model_config = ConfigDict(frozen=True)

    endpoint: str
    label_getter: LabelGetter


class ApiSelectOptions:
    """
    Получает значения Ant Select напрямую из API-каталогов.

    Длинные Ant Select списки рендерятся виртуально: в DOM одновременно есть
    только часть option-элементов, поэтому сбор всех значений через прокрутку
    может быть медленным и нестабильным. Для известных фильтров этот класс
    использует те же backend endpoint'ы, что и frontend, и возвращает полный
    список значений за один запрос.
    """
    CATALOGS_BY_INPUT_ID = {
        "projector_curator_id": SelectCatalog(
            endpoint="users/user-profile/?limit=10000",
            label_getter=lambda row: user_profile_label(row),
        ),
        "planning_curator_id": SelectCatalog(
            endpoint="users/user-profile/?limit=10000",
            label_getter=lambda row: user_profile_label(row),
        ),
        "subcompany_id": SelectCatalog(
            endpoint="subcompany/catalog/subcompanies/?limit=10000",
            label_getter=lambda row: (
                f"{row.get('code')} | {row.get('shortTitle')}"
            ),
        ),
        "subcompany_ids": SelectCatalog(
            endpoint="subcompany/catalog/subcompanies/?limit=10000",
            label_getter=lambda row: (
                f"{row.get('code')} | {row.get('shortTitle')}"
            ),
        ),
        "region_id": SelectCatalog(
            endpoint="subcompany/catalog/regions/?limit=10000",
            label_getter=lambda row: row.get("title") or ZERO_WIDTH_SPACE,
        ),
        "region_ids": SelectCatalog(
            endpoint="subcompany/catalog/regions/?limit=10000",
            label_getter=lambda row: row.get("title") or ZERO_WIDTH_SPACE,
        ),
        "stage_id": SelectCatalog(
            endpoint="subcompany/ip-subcompany/datamart/stages/?limit=10000",
            label_getter=lambda row: row.get("title") or ZERO_WIDTH_SPACE,
        ),
        "stage_ids": SelectCatalog(
            endpoint="subcompany/ip-subcompany/datamart/stages/?limit=10000",
            label_getter=lambda row: row.get("title") or ZERO_WIDTH_SPACE,
        ),
        "projection_doc_status_id": SelectCatalog(
            endpoint=(
                "holding/catalog/projection-doc-approval-status/?limit=10000"
            ),
            label_getter=lambda row: row.get("shortTitle") or ZERO_WIDTH_SPACE,
        ),
        "priority_id": SelectCatalog(
            endpoint=(
                "subcompany/catalog/"
                "priority-code-object-not-need-assembly/?limit=10000"
            ),
            label_getter=lambda row: str(row.get("code") or ZERO_WIDTH_SPACE),
        ),
        "group_id": SelectCatalog(
            endpoint=(
                "subcompany/catalog/"
                "group_object_not_need_assembly_catalog/?limit=10000"
            ),
            label_getter=lambda row: row.get("title") or ZERO_WIDTH_SPACE,
        ),
    }

    def __init__(self, driver: WebDriver):
        """Создает API-сборщик значений select'ов."""
        self.driver = driver

    def options(self, input_id: str) -> list[str] | None:
        """Возвращает значения select'а из API, если для него описан каталог."""
        catalog = self.CATALOGS_BY_INPUT_ID.get(input_id)

        if catalog is None:
            return None

        return [
            catalog.label_getter(row)
            for row in self.rows(catalog)
        ]

    def rows(self, catalog: SelectCatalog) -> list[dict]:
        """Возвращает строки API-каталога с кешированием в WebDriver."""
        cache = self.cache()

        if catalog.endpoint not in cache:
            cache[catalog.endpoint] = self.fetch_rows(catalog.endpoint)

        return cache[catalog.endpoint]

    def cache(self) -> dict[str, list[dict]]:
        """
        Возвращает кеш API-каталогов, привязанный к текущему WebDriver.

        Кеш хранится в атрибуте драйвера, чтобы повторные чтения одинакового
        каталога в рамках одной браузерной сессии не делали лишние HTTP-запросы.
        """
        cache = getattr(self.driver, "_api_select_options_cache", None)

        if cache is None:
            cache = {}
            setattr(self.driver, "_api_select_options_cache", cache)

        return cache

    def fetch_rows(self, endpoint: str) -> list[dict]:
        """
        Загружает строки каталога через fetch внутри браузера.

        Запрос выполняется из контекста страницы, чтобы использовать токен
        авторизации из `localStorage`.
        """
        response = self.driver.execute_async_script(
            """
            const endpoint = arguments[0];
            const done = arguments[1];
            const token = localStorage.getItem("access");
            const url = `http://127.0.0.1:8000/api/v1/${endpoint}`;

            fetch(url, {
                headers: {
                    "x-app-authorization": `Bearer ${token}`,
                },
            })
                .then(async (response) => {
                    const body = await response.json();

                    if (!response.ok) {
                        throw new Error(
                            `${response.status}: ${JSON.stringify(body)}`
                        );
                    }

                    done(body);
                })
                .catch((error) => done({ error: String(error) }));
            """,
            endpoint,
        )

        if isinstance(response, dict) and "error" in response:
            raise AssertionError(
                "Не удалось получить значения выпадающего списка через API.\n"
                f"Endpoint: {endpoint}\n"
                f"Ошибка: {response['error']}"
            )

        if isinstance(response, list):
            return response

        results = response.get("results", [])

        if response.get("isNextExists"):
            raise AssertionError(
                "API вернул не все значения выпадающего списка.\n"
                f"Endpoint: {endpoint}\n"
                f"Получено: {len(results)} из {response.get('count')}"
            )

        return results


ZERO_WIDTH_SPACE = "\u200b"


def user_profile_label(row: dict) -> str:
    """Формирует отображаемое ФИО пользователя из строки API."""
    full_name = " ".join(
        str(row.get(key) or "")
        for key in ("lastName", "firstName", "middleName")
    ).strip()

    return format_full_name(full_name)


def format_full_name(full_name: str) -> str:
    """Преобразует полное ФИО в формат с инициалами."""
    if not full_name:
        return ""

    parts = full_name.split()
    last_name = parts[0] if len(parts) > 0 else ""
    first_name = parts[1] if len(parts) > 1 else ""
    middle_name = parts[2] if len(parts) > 2 else ""

    if not middle_name:
        return f"{last_name} {user_initial(first_name)}.".strip()

    return (
        f"{last_name} "
        f"{user_initial(first_name)}."
        f"{user_initial(middle_name)}."
    ).strip()


def user_initial(name: str) -> str:
    """Возвращает первую букву имени в верхнем регистре."""
    return name[0].upper() if name else ""
