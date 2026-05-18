from enum import StrEnum


class PrwOtherExpertisesFilterTitle(StrEnum):
    """Названия фильтров на странице 'Прочие экспертизы'."""
    OBJECT_PRW_CODE = "Код ПИР"
    SUBCOMPANY = "Заказчик"
    CONCLUSION_TYPE = "Вид"
    STATUS = "Статус"
    CONCLUSION_DATE_FROM = "Дата утверждения от"
    CONCLUSION_DATE_TO = "Дата утверждения до"
    SEARCH = "Поиск"


class PrwOtherExpertisesFilterId(StrEnum):
    """HTML id полей фильтров на странице 'Прочие экспертизы'."""
    OBJECT_PRW_CODE_ID = "object_prw_code"
    SUBCOMPANY_ID = "subcompany_ids"
    CONCLUSION_TYPE_ID = "conclusion_type_id"
    STATUS_ID = "status"
    CONCLUSION_DATE_FROM_ID = "conclusion_date_from"
    CONCLUSION_DATE_TO_ID = "conclusion_date_to"
    SEARCH_ID = "search"