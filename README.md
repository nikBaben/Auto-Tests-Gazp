# Auto-Tests-Gazp

Selenium + pytest автотесты для локального стенда ИУС «ГАЗПРОЕКТ 2.0».

Проект проверяет страницы разделов ИП ДО: сортировку значений в фильтрах,
поиск по частичному совпадению, валидацию полей, применение фильтров к таблицам
и работу с таблицами Ant Design.

## Быстрый старт

```bash
pip install -r requirements.txt
pytest
```

По умолчанию тесты открывают `http://localhost:3000`, авторизуются через
пользователя с индексом `2` и запускают все тесты из `tests`.

## Настройки окружения

Настройки читаются из переменных окружения в `config/settings.py`.

```bash
BASE_URL=http://localhost:3000
SELENIUM_TIMEOUT=20
DEFAULT_USER_INDEX=2
HEADLESS=1
```

| Переменная | Значение по умолчанию | Назначение |
| --- | --- | --- |
| `BASE_URL` | `http://localhost:3000` | Адрес frontend-стенда |
| `SELENIUM_TIMEOUT` | `20` | Таймаут ожиданий Selenium в секундах |
| `DEFAULT_USER_INDEX` | `2` | Индекс пользователя на странице входа |
| `HEADLESS` | пусто | Если `1`, `true` или `yes`, Chrome запускается без UI |

## Полезные команды

```bash
pytest
pytest tests/ip_subcompany/prw/planning_list
pytest tests/ip_subcompany/prw/test_prw_design_assignment_filter_apply.py -q
pytest --collect-only -q
python3 -m compileall -q .
```

CSV-отчет формируется после запуска pytest:

```text
reports/test_report.csv
```

Путь можно переопределить:

```bash
pytest --csv-report reports/my_report.csv
```

## Структура проекта

```text
config/                 настройки окружения
fixtures/               pytest-фикстуры: browser, auth, pages, reports
components/             обертки над UI-компонентами Ant Design
pages/                  Page Object модели
checks/                 переиспользуемые проверки и test helper'ы
utils/                  нормализация и сравнение значений
tests/                  pytest-тесты по разделам приложения
docs/                   подробная документация проекта
```

## Документация

- [Архитектура проекта](docs/ARCHITECTURE.md)
- [Как писать и расширять тесты](docs/WRITING_TESTS.md)

## Основной принцип

Тест должен описывать сценарий, а не Selenium-детали.

Хороший тест обычно выглядит так:

```python
def test_prw_planning_list_applies_subcompany_filter(
    prw_planning_list_page,
    test_report,
):
    code = first_non_empty(prw_planning_list_page.subcompany_codes())
    selected_option = matching_subcompany_option(
        options=prw_planning_list_page.subcompany_options(),
        code=code,
    )

    values = prw_planning_list_page.apply_subcompany_filter(selected_option)

    assert_filter_values_match(
        element=PrwPlanningListFilterTitle.SUBCOMPANY,
        selected_value=code,
        values=values,
        report=test_report,
        normalizer=normalized_text,
    )
```

Где должна жить логика:

| Что | Где |
| --- | --- |
| Selenium-локаторы и действия со страницей | `pages/` |
| Работа с Ant Select, Ant Table, DatePicker | `components/` |
| Проверки сортировки, фильтрации, валидации | `checks/` |
| Нормализация текста, ФИО, кодов ДО | `utils/` |
| Сценарии проверок | `tests/` |

## Текущие особенности

- Колонки таблиц ищутся по заголовкам через `AntTableColumn`, а не по
  фиксированным индексам.
- Если колонка скрыта и включается checkbox'ом, Page Object включает ее перед
  чтением значений.
- Даты выбираются через календарь Ant DatePicker, а не прямым вводом строки.
- Выпадающие списки сначала пробуют получить значения из API-данных страницы,
  а если это невозможно, читают видимые DOM-опции.
- CSV-отчет заполняется из общих `checks`, поэтому в тестах не нужно вручную
  писать строки отчета.
