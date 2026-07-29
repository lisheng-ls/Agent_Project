from typing import Any

from app.entities.column_info import ColumnInfo
from app.models.column_info import ColumnInfoMySQL


class ColumnInfoMapper:
    @staticmethod
    def to_entity(column_info_mysql:ColumnInfoMySQL) -> ColumnInfo:
        # 归一化处理examples
        if column_info_mysql.examples is None:
            examples: list[Any] = []
        elif isinstance(column_info_mysql.examples, dict):
            examples = [column_info_mysql.examples]
        elif isinstance(column_info_mysql.examples, list):
            examples = column_info_mysql.examples
        else:
            examples = []
        # 归一化处理alias
        if isinstance(column_info_mysql.alias, list):
            alias = column_info_mysql.alias
        else:
            alias = []

        return  ColumnInfo(
            id = column_info_mysql.id,
            name = column_info_mysql.name,
            type = column_info_mysql.type,
            role = column_info_mysql.role,
            examples= examples,
            description= column_info_mysql.description,
            alias= alias,
            table_id=column_info_mysql.table_id,
        )

    #将业务实体类转换为orm实体类，用户存储数据
    @staticmethod
    def to_model(column_info : ColumnInfo)-> ColumnInfoMySQL :
        return ColumnInfoMySQL(
            id = column_info.id,
            name = column_info.name,
            type = column_info.type,
            role = column_info.role,
            examples= column_info.examples,
            description= column_info.description,
            alias= column_info.alias,
            table_id=column_info.table_id,
        )