from dataclasses import dataclass
from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


@dataclass
class ColumnInfoState(TypedDict):
    name:str | None
    type:str | None
    role:str | None
    examples:list | None
    description:str| None
    alias:list[str]


#表信息含有的字段
@dataclass
class TableInfoState(TypedDict):
    name: str | None
    role: str | None
    description: str | None
    columns:list[ColumnInfoState]

#定义合并后的指标信息
@dataclass
class MetricInfoState(TypedDict):
    name: str | None
    description: str | None
    relevant_columns:list[str]
    alias:list[str]


@dataclass
class DateInfoState(TypedDict):
    date:str
    weekday:str
    quarter:str

@dataclass
class DbInfoState(TypedDict):
    version:str
    dialect:str




class DataAgentState(TypedDict):
    query:str  #用户输入的查询
    error:str | None  #校验sql出现的错误信息
    keywords : list[str]  #抽取的关键字

    retrieved_column_infos : list[ColumnInfo]   #检索的字段信息
    retrieved_metric_infos : list[MetricInfo]   #检索的指标信息
    retrieved_column_values : list[ValueInfo]   #检索的字段取值

    #表信息和指标信息
    table_infos: list[TableInfoState]
    metric_infos: list[MetricInfoState]


    #上下文信息
    date_info: DateInfoState | None
    db_info: DbInfoState | None

    # 生成的sql
    sql:str

    #执行sql得到的结果
    sql_search_result:str | None