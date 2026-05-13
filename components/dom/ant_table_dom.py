"""DOM-адаптер для работы с Ant Design Table."""
from typing import cast

from selenium.webdriver.remote.webdriver import WebDriver

from components.schemas.ant_table_schema import AntTableColumn


class AntTableDom:
    """
    DOM-адаптер для Ant Design Table.

    JavaScript-операции,
    необходимые для стабильной работы с таблицами Ant Design,
    включая сложные многоуровневые заголовки
    """
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def column_index_by_header(self, header_texts: tuple[str, ...]) -> int | None:
        """Возвращает индекс колонки по текстам заголовков."""
        return self.column_index(
            AntTableColumn(headers=header_texts),
        )

    def column_index(self, column: AntTableColumn) -> int | None:
        """Возвращает индекс колонки по спецификации."""
        return cast(
            int | None,
            self.driver.execute_script(
                """
                const table = document.querySelector(".ant-table");
                if (!table) {
                    return null;
                }

                const expectedTexts = arguments[0].map(normalize);
                const expectedPaths = arguments[1].map(
                    (path) => path.map(normalize)
                );
                const headerRows = Array.from(
                    table.querySelectorAll(".ant-table-thead tr")
                );
                const grid = [];

                headerRows.forEach((row, rowIndex) => {
                    grid[rowIndex] = grid[rowIndex] || [];
                    let columnIndex = 0;

                    Array.from(row.children).forEach((cell) => {
                        while (grid[rowIndex][columnIndex]) {
                            columnIndex += 1;
                        }

                        const header = {
                            text: normalize(cell.innerText),
                        };
                        const rowSpan = Number(
                            cell.getAttribute("rowspan") || cell.rowSpan || 1
                        );
                        const colSpan = Number(
                            cell.getAttribute("colspan") || cell.colSpan || 1
                        );

                        for (
                            let rowOffset = 0;
                            rowOffset < rowSpan;
                            rowOffset += 1
                        ) {
                            const targetRow = rowIndex + rowOffset;
                            grid[targetRow] = grid[targetRow] || [];

                            for (
                                let colOffset = 0;
                                colOffset < colSpan;
                                colOffset += 1
                            ) {
                                grid[targetRow][columnIndex + colOffset] = header;
                            }
                        }

                        columnIndex += colSpan;
                    });
                });

                const leafHeaders = grid[grid.length - 1] || [];

                for (let index = 0; index < leafHeaders.length; index += 1) {
                    const path = compactPath(
                        grid.map((row) => row[index]?.text)
                    );

                    if (matchesPath(path, expectedPaths)) {
                        return index;
                    }
                }

                for (let index = 0; index < leafHeaders.length; index += 1) {
                    const path = compactPath(
                        grid.map((row) => row[index]?.text)
                    );
                    const leafText = path[path.length - 1];

                    if (leafText && expectedTexts.includes(leafText)) {
                        return index;
                    }
                }

                return null;

                function normalize(value) {
                    return String(value || "")
                        .replace(/\\u200b/g, "")
                        .replace(/\\s+/g, " ")
                        .trim();
                }

                function compactPath(path) {
                    return path
                        .filter(Boolean)
                        .filter(
                            (header, index, headers) => (
                                index === 0 || header !== headers[index - 1]
                            )
                        );
                }

                function matchesPath(path, expectedPaths) {
                    return expectedPaths.some((expectedPath) => (
                        path.length === expectedPath.length
                        && expectedPath.every(
                            (header, index) => header === path[index]
                        )
                    ));
                }
                """,
                list(column.headers),
                [list(header_path) for header_path in column.header_paths],
            ),
        )

    def column_values(
        self,
        column_index: int,
        keep_empty: bool = False,
    ) -> list[str]:
        """Возвращает значения колонки таблицы по индексу."""
        return cast(
            list[str],
            self.driver.execute_script(
                """
                const table = document.querySelector(".ant-table");
                if (!table) {
                    return [];
                }

                const keepEmpty = arguments[1];
                const valuesAt = (selector) => Array.from(
                    table.querySelectorAll(selector)
                ).map((row) => {
                    const style = window.getComputedStyle(row);
                    if (
                        style.display === "none"
                        || style.visibility === "hidden"
                    ) {
                        return "";
                    }

                    const cell = row.querySelectorAll(".ant-table-cell")[
                        arguments[0]
                    ];
                    return cell ? cell.innerText.trim() : "";
                });
                const textAt = (selector) => {
                    const values = valuesAt(selector);
                    return keepEmpty ? values : values.filter(Boolean);
                };

                const extraValues = textAt(".ant-table-row-extra");
                return extraValues.length
                    ? extraValues
                    : textAt(".ant-table-row:not(.ant-table-row-extra)");
                """,
                column_index,
                keep_empty,
            ),
        )
