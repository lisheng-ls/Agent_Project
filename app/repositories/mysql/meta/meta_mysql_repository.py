from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL

from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import TableInfoMapper


class MetaMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session


    #将表信息写入table_info表中
    def save_table_info(self,table_infos):

        table_info = [TableInfoMapper().to_model(table_info) for table_info in table_infos  ]

        self.session.add_all(table_info)


    #将字段信息写入column_info表中
    def save_column_info(self,column_infos):
        column_info = [ColumnInfoMapper().to_model(column_info) for column_info in column_infos  ]
        self.session.add_all(column_info)


    def save_metric_info(self,metric_infos):
        metric_info = [MetricInfoMapper().to_model(metric_info) for metric_info in metric_infos ]
        self.session.add_all(metric_info)

    async def get_column_info(self, relevant_column) -> ColumnInfo |None:
       #查询的数据类型为：ColumnInfoMapper
       column_info : ColumnInfoMySQL |None  = await self.session.get(ColumnInfoMySQL,relevant_column)
       if column_info:
           #转换为ColumnInfo类型
           return ColumnInfoMapper().to_entity(column_info)
       else:
           return None

    async def get_table_info(self, table_id) -> TableInfo |None :
        #根据table_id查询数据，得到的数据类型为TableInfoMySQL
        table_info : TableInfoMySQL |None = await self.session.get(TableInfoMySQL,table_id)
        if table_info:
            return TableInfoMapper().to_entity(table_info)
        else:
            return None

    async def get_key_info(self, table_id:str) -> list[ColumnInfo] :
        sql = "select * from key_info where table_id = :table_id  and role in ( 'primary_key','foreign_key') "
        result = await self.session.execute(text(sql),params={'table_id': table_id})
        result = result.mappings().fetchall()
        return [ColumnInfo(**dict(row)) for row in result]



