# Архитектура проекта

Документ описывает, как устроен тестовый фреймворк и куда добавлять новую
логику.

## Слои

```text
tests
  -> pages
    -> components
      -> Selenium WebDriver

checks
utils
fixtures
config
```

### `tests`

Тесты описывают пользовательский сценарий:

1. Получить исходные данные со страницы.
2. Выполнить действие через Page Object.
3. Проверить результат через общий `check`.

В тестах не должно быть CSS/XPath-локаторов и низкоуровневых Selenium-действий.

### `pages`

Page Object знает:

- URL страницы через `PATH`;
- HTML id фильтров через enum `*FilterId`;
- отображаемые названия фильтров через enum `*FilterTitle`;
- спецификации колонок таблицы через `AntTableColumn`;
- бизнес-методы страницы: `search_by_*`, `apply_*_filter`, `*_options`,
  `*_values`.

Базовые классы:

- `BasePage` открывает страницу, ищет элементы, возвращает фильтры по `FILTER_IDS`.
- `FilteredTablePage` добавляет работу с фильтрами, таблицей, dropdown и датами.

### `components`

Компоненты скрывают особенности Ant Design:

- `AntSelect` открывает dropdown, собирает опции, ищет и выбирает значение.
- `AntTable` читает значения колонок и определяет индекс колонки по заголовку.
- `DateInput` выбирает дату через календарь.
- `TextInput` заполняет текстовые поля и читает ошибки валидации.

Компоненты можно использовать в Page Object, но не напрямую в тестах.

### `checks`

`checks` содержат assert'ы, которые можно использовать на разных страницах.

- `checks/sorting.py` проверяет сортировку списков.
- `checks/filtering.py` проверяет поиск и применение фильтров.
- `checks/input_validation.py` проверяет ошибки валидации.
- `checks/utils.py` содержит небольшие helper'ы для подготовки тестовых данных.

Каждый check пишет данные в `CsvReport`, поэтому тест получает понятный отчет
без ручного дублирования.

### `utils`

`utils/value_matchers.py` содержит нормализацию и сравнение значений:

- очистка пробелов и служебных символов;
- сравнение ФИО;
- извлечение кода ДО;
- сравнение option/table значений, которые отображаются немного по-разному.

## Жизненный цикл теста

1. `pytest` поднимает `driver` и `wait` из `fixtures/browser.py`.
2. `authorized_session` из `fixtures/auth.py` один раз авторизует сессию.
3. Фикстура страницы из `fixtures/pages.py` создает Page Object и вызывает
   `page.open()`.
4. Тест выполняет действия через Page Object.
5. Проверка из `checks` добавляет запись в `test_report`.
6. Хук из `fixtures/reports.py` сохраняет строки в CSV после завершения сессии.

## Работа с таблицами

Раньше колонки можно было читать по фиксированному индексу. Сейчас это
специально не используется: индекс может измениться из-за порядка колонок,
скрытых колонок или многоуровневой шапки.

Колонка описывается так:

```python
class PrwPlanningListColumn:
    OBJECT_PRW_CODE_COLUMN = AntTableColumn(headers=("Код ПИР",))
    TITLE_COLUMN = AntTableColumn(headers=("Объект проектирования",))
```

Для сложной шапки используется полный путь:

```python
PROJECTION_DOC_STATUS = AntTableColumn(
    header_paths=(("Статус утверждения ПД", "Статус"),),
)
```

Если колонка появляется только после включения checkbox:

```python
PROJECTOR_CURATOR = AntTableColumn(
    headers=("Куратор проектир.", "Куратор проектирования"),
    checkbox_label="Кураторы",
)
```

При чтении через `table_column_values_by_spec` страница сама:

1. включит checkbox, если указан `checkbox_label`;
2. дождется появления колонки;
3. найдет актуальный индекс по заголовку;
4. вернет значения.

## Работа с фильтрами

Для текстового фильтра Page Object обычно использует `search_text_filter`:

```python
def search_by_title(self, value: str) -> list[str]:
    return self.search_text_filter(
        input_id=PrwPlanningListFilterId.TITLE_ID,
        value=value,
        result_getter=self.titles,
        ignore_case=True,
    )
```

Для dropdown-фильтра используется `apply_dropdown_filter`:

```python
def apply_subcompany_filter(self, value: str) -> list[str]:
    code = subcompany_code(value)

    return self.apply_dropdown_filter(
        input_id=PrwPlanningListFilterId.SUBCOMPANY_ID,
        value=value,
        search_value=code,
        result_getter=self.subcompany_codes,
        result_matches=lambda result: normalized_text(result) == code,
    )
```

`result_getter` читает колонку таблицы после применения фильтра.
`result_matches` описывает, как понять, что фильтр применился.

## Работа с датами

Даты не вводятся через `send_keys`. Для Ant DatePicker используется
`DateInput.select_date`:

1. открыть календарь;
2. перейти на нужный месяц;
3. кликнуть день по `td[title='YYYY-MM-DD']`;
4. дождаться, что input получил значение в формате `ДД.ММ.ГГГГ`.

Это важно, потому что прямой ввод в Ant DatePicker может оставить поле в
промежуточном состоянии.

## Фикстуры

Основные фикстуры:

| Фикстура | Назначение |
| --- | --- |
| `driver` | Создает Chrome WebDriver на сессию |
| `wait` | Общий `WebDriverWait` |
| `authorized_session` | Авторизует браузер перед тестами |
| `test_report` | Собирает строки CSV-отчета |
| `prw_*_page` | Открывает нужную страницу и возвращает Page Object |

Фикстуры страниц создаются через общий helper:

```python
def open_page(page_class: type[BasePage], driver, wait):
    page = page_class(driver, wait, BASE_URL)
    page.open()
    return page
```

## Отчетность

Каждая проверка добавляет строку:

```python
report.add(
    element="ДО",
    expected="После нажатия 'Найти' все строки соответствуют '036'",
    actual=["036", "036"],
    message="Проверка применения фильтра к таблице",
)
```

Файл сохраняется в `reports/test_report.csv` или в путь из `--csv-report`.

## Правила поддержки

- Новый Selenium-код сначала добавлять в `components` или `pages`, а не в тест.
- Повторяющийся assert выносить в `checks`.
- Повторяющуюся подготовку значения выносить в `checks/utils.py`.
- Повторяющуюся нормализацию выносить в `utils/value_matchers.py`.
- Колонки таблиц описывать через `AntTableColumn`, не через фиксированные
  индексы.
- Для скрытых колонок указывать `checkbox_label`.
- После изменений запускать `python3 -m compileall -q .` и
  `pytest --collect-only -q`.
