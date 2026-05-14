# Как писать и расширять тесты

Документ показывает типовые сценарии добавления тестов.

## Общий шаблон теста

```python
def test_some_filter(page_fixture, test_report):
    selected_value = ...

    values = page_fixture.apply_some_filter(selected_value)

    assert_filter_values_match(
        element=SomeFilterTitle.SOME_FILTER,
        selected_value=selected_value,
        values=values,
        report=test_report,
        normalizer=normalized_text,
    )
```

Тест должен быть коротким. Если в тесте появляются XPath, CSS-селекторы,
`driver.find_element`, `WebDriverWait` или сложная логика ожидания, это почти
всегда нужно перенести в Page Object или компонент.

## Добавить новую страницу

1. Создать Page Object в `pages/...`.
2. Унаследоваться от `FilteredTablePage`, если на странице есть фильтры и таблица.
3. Описать `PATH`.
4. Описать enum с id фильтров.
5. Описать enum с названиями фильтров.
6. Описать колонки через `AntTableColumn`.
7. Добавить методы страницы.
8. Экспортировать класс в `pages/__init__.py`, если тесты импортируют его из
   `pages`.
9. Добавить фикстуру страницы в `fixtures/pages.py`, если страница часто
   используется в тестах.

Минимальный пример:

```python
from enum import StrEnum

from components.schemas.ant_table_schema import AntTableColumn
from pages.filtered_table_page import FilteredTablePage


class SomePageFilterTitle(StrEnum):
    OBJECT_CODE = "Код ПИР"


class SomePageFilterId(StrEnum):
    OBJECT_CODE_ID = "object_code"


class SomePageColumn:
    OBJECT_CODE = AntTableColumn(headers=("Код ПИР",))


class SomePage(FilteredTablePage):
    PATH = "/some/path"
    FILTER_IDS = SomePageFilterId

    def object_codes(self) -> list[str]:
        return self.table_column_values_by_spec(SomePageColumn.OBJECT_CODE)

    def wait_object_codes(self) -> list[str]:
        return self.wait.until(lambda _: self.object_codes())

    def search_by_object_code(self, value: str) -> list[str]:
        return self.search_text_filter(
            input_id=SomePageFilterId.OBJECT_CODE_ID,
            value=value,
            result_getter=self.object_codes,
        )
```

## Добавить текстовый фильтр

В Page Object:

```python
def titles(self) -> list[str]:
    return self.table_column_values_by_spec(SomePageColumn.TITLE)

def wait_titles(self) -> list[str]:
    return self.wait.until(lambda _: self.titles())

def search_by_title(self, value: str) -> list[str]:
    return self.search_text_filter(
        input_id=SomePageFilterId.TITLE_ID,
        value=value,
        result_getter=self.titles,
        ignore_case=True,
    )
```

В тесте:

```python
def test_some_page_title_searches_by_partial_value(page, test_report):
    entered_value = partial_filter_search_value(
        options=page.wait_titles(),
        part_length=4,
        case_transform=str.lower,
    )

    values = page.search_by_title(entered_value)

    assert_values_contain_substring(
        element=SomePageFilterTitle.TITLE,
        entered_value=entered_value,
        values=values,
        report=test_report,
        ignore_case=True,
    )
```

## Добавить dropdown-фильтр

В Page Object:

```python
def subcompany_codes(self) -> list[str]:
    return self.table_column_values_by_spec(SomePageColumn.SUBCOMPANY)

def subcompany_options(self) -> list[str]:
    return self.dropdown_options(SomePageFilterId.SUBCOMPANY_ID)

def apply_subcompany_filter(self, value: str) -> list[str]:
    code = subcompany_code(value)

    return self.apply_dropdown_filter(
        input_id=SomePageFilterId.SUBCOMPANY_ID,
        value=value,
        search_value=code,
        result_getter=self.subcompany_codes,
        result_matches=lambda result: normalized_text(result) == code,
    )
```

В тесте:

```python
def test_some_page_applies_subcompany_filter(page, test_report):
    code = first_non_empty(page.subcompany_codes())
    selected_option = matching_subcompany_option(
        options=page.subcompany_options(),
        code=code,
    )

    values = page.apply_subcompany_filter(selected_option)

    assert_filter_values_match(
        element=SomePageFilterTitle.SUBCOMPANY,
        selected_value=code,
        values=values,
        report=test_report,
        normalizer=normalized_text,
    )
```

## Добавить фильтр по дате

В Page Object:

```python
def approval_dates(self, keep_empty: bool = False) -> list[str]:
    return self.table_column_values_by_spec(
        SomePageColumn.APPROVAL_DATE,
        keep_empty=keep_empty,
    )

def fill_approval_date_from(self, value: str) -> None:
    self.date_input(SomePageFilterId.APPROVAL_DATE_FROM_ID).fill(value)

def fill_approval_date_to(self, value: str) -> None:
    self.date_input(SomePageFilterId.APPROVAL_DATE_TO_ID).fill(value)
```

В тесте:

```python
def test_some_page_applies_approval_date_range_filter(page, test_report):
    date_from, date_to = date_range_from_values(page.approval_dates())

    values = page.apply_approval_date_range_filter(
        date_from=date_from,
        date_to=date_to,
    )

    assert_date_values_in_range(
        element="Дата утверждения с / Дата утверждения по",
        date_from=date_from,
        date_to=date_to,
        values=values,
        report=test_report,
    )
```

## Добавить проверку сортировки dropdown

```python
def test_some_page_subcompany_sorted(page, test_report):
    options = page.subcompany_options()
    errors = []

    for check in (
        assert_special_values_at_end,
        assert_sorted_by_leading_number,
    ):
        try:
            check(
                element=SomePageFilterTitle.SUBCOMPANY,
                values=options,
                report=test_report,
            )
        except AssertionError as error:
            errors.append(str(error))

    assert not errors, "\n\n".join(errors)
```

Такой формат позволяет увидеть сразу несколько ошибок сортировки за один запуск.

## Добавить проверку валидации

В Page Object:

```python
def fill_object_code(self, value: str) -> None:
    self.text_input(SomePageFilterId.OBJECT_CODE_ID).fill(value)

def object_code_value(self) -> str:
    return self.text_input(SomePageFilterId.OBJECT_CODE_ID).value()

def object_code_error(self) -> str:
    return self.text_input(SomePageFilterId.OBJECT_CODE_ID).error_text()
```

В тесте:

```python
def test_some_page_object_code_shows_error_for_text(page, test_report):
    entered_value = "Код ПИР"

    page.fill_object_code(entered_value)
    field_value = page.object_code_value()
    actual_error = page.object_code_error()

    assert_shows_validation_error(
        element=SomePageFilterTitle.OBJECT_CODE,
        entered_value=entered_value,
        field_value=field_value,
        expected_error="Укажите целое неотрицательное число",
        actual_error=actual_error,
        report=test_report,
    )
```

## Как выбирать тестовые данные

Лучше брать данные с текущей страницы, а не хардкодить значения:

```python
existing_code = first_non_empty(page.wait_object_codes())
entered_value = existing_code[-3:]
```

Для dropdown:

```python
table_value = first_non_empty(page.projector_curators())
selected_option = matching_person_option(
    options=page.projector_curator_options(),
    table_value=table_value,
)
```

Если на текущем стенде нет подходящих данных, тест может честно сделать
`pytest.skip`, как в проверках регионов или статусов, где пустая таблица не дает
проверить фильтр.

## Где держать константы

Если константа используется только в одном файле, можно оставить ее в тесте.
Если константа общая для группы тестов страницы, лучше вынести ее в локальный
`config.py` рядом с тестами страницы.

Пример:

```text
tests/ip_subcompany/prw/planning_list/config.py
```

## Проверка после изменений

Минимальный набор:

```bash
python3 -m compileall -q .
pytest --collect-only -q
```

Для реальной проверки конкретного сценария:

```bash
pytest tests/ip_subcompany/prw/planning_list/test_prw_planning_list_filter_apply.py -q
```

Если тест работает с UI, перед запуском должен быть доступен frontend по
`BASE_URL`.
