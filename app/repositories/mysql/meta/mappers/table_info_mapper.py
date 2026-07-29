from app.entities.table_info import TableInfo
from app.models.table_info import TableInfoMySQL


class TableInfoMapper:
    #将orm实体类转换为业务实体类，用于输出数据

    @staticmethod
    def to_entity(table_info_mysql:TableInfoMySQL) -> TableInfo:
        return  TableInfo(
            id = table_info_mysql.id,
            name = table_info_mysql.name,
            role = table_info_mysql.role,
            description = table_info_mysql.description
        )

    #将业务实体类转换为orm实体类，用户存储数据
    @staticmethod
    def to_model(table_info : TableInfo)-> TableInfoMySQL :
        return TableInfoMySQL(
            
        )
