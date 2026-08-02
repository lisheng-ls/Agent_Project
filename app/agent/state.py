from dataclasses import dataclass
from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


@dataclass
class ColumnInfoState:
    name:str | None
    type:str | None
    role:str | None
    examples:list | None
    description:str| None
    alias:list[str]


#表信息含有的字段
@dataclass
class TableInfoState:
    name: str | None
    role: str | None
    description: str | None
    columns:list[ColumnInfoState]

#定义合并后的指标信息
@dataclass
class MetricInfoState:
    name: str | None
    description: str | None
    relevant_columns:list[str]
    alias:list[str]


class DataAgentState(TypedDict):
    query:str  #用户输入的查询
    error:str | None  #校验sql出现的错误信息
    keywords : list[str]  #抽取的关键字
    retrieved_column_infos : list[ColumnInfo] #检索的字段信息
    retrieved_metric_infos : list[MetricInfo]
    retrieved_column_values : list[ValueInfo]
    table_infos: TableInfoState
    metric_infos: MetricInfoState




