from pathlib import Path

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository


class MetaKnowledgeService:
    def __init__(self,meta_mysql_repository:MetaMysqlRepository,dw_mysql_repository:DwMysqlRepository):
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository

    async def build(self,config_path:Path):
        #1.读取配置文件

        # 读取yaml文件内容
        content = OmegaConf.load(config_path)

        # 构造配置文件结构，按照MetaConfig结构构造
        schema = OmegaConf.structured(MetaConfig)

        # 合并结构+内容
        merge_config = OmegaConf.merge(schema, content)

        # 转换为MetaConfig的对象
        meta_config: MetaConfig = OmegaConf.to_object(merge_config)


        #2.根据配置文件读取表信息

        #判断是否有表信息
        if meta_config.metrics:
            table_list : TableInfo = []
            column_list :ColumnInfo  = []
            #2.1将表信息和字段信息存储到meta数据库中
            for table in meta_config.tables :

                #将表信息存储值table_info 表中

                table_info = TableInfo(
                    id = table.name,
                    name = table.name,
                    role = table.role,
                    description = table.description
                )
                table_list.append(table_info)

                #查询字段类型
                type_list =  await self.dw_mysql_repository.get_column_types(table.name)

                for columns in table.columns:

                    #查询字段的值
                    column_valuse = await self.dw_mysql_repository.get_column_values(columns.name,table.name)

                    # 将字段信息存储至column_info表中
                    columns_info = ColumnInfo(
                        id = f"{table.name}.{columns.name}",
                        name = columns.name,
                        type = type_list[columns.name],
                        role = columns.role,
                        examples = column_valuse,
                        description=columns.description,
                        alias=columns.alias,
                        table_id = table.name
                    )
                    column_list.append(columns_info)

            #将表信息写入table_info中，将字段信息写入column_info中
            async  with self.meta_mysql_repository.session.begin():
                self.meta_mysql_repository.save_table_info(table_list)
                self.meta_mysql_repository.save_table_info(column_list)


            #2.2对字段信息建立向量索引

            #2.3对指定的维度字段建立全文索引


        #3.根据配置文件读取指标信息

        #判断是否有指标信息
        if meta_config.metrics:
            pass
            #3.1将指标信息存储到meta数据库中

            #3.2对指标信息建立向量索引