from pathlib import Path

from omegaconf import OmegaConf
from app.conf.meta_config import MetaConfig
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta import meta_mysql_repository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository


class MetaKnowledgeService:
    def __init__(self,
                 meta_mysql_repository : MetaMysqlRepository,
                 dw_mysql_repository : DwMysqlRepository):
        self.meta_mysql_repository : MetaMysqlRepository = meta_mysql_repository
        self.dw_mysql_repository : DwMysqlRepository = dw_mysql_repository

    async def build(self,config_path:Path):
        #1.读取配置文件
        #读取yaml文件内容
        content = OmegaConf.load(config_path)

        #构造配置文件结构，按照AppConfig结构构造
        schema = OmegaConf.structured(MetaConfig)

        # 合并结构+内容
        merge_config = OmegaConf.merge(schema,content)

        # 转换为AppConfig的对象
        meta_config: MetaConfig = OmegaConf.to_object(merge_config)


        #2.根据配置文件同步指定的表信息
        if meta_config.tables:
            #配置文件中有表信息
            #同步表信息

            #表信息
            table_info_list : list[TableInfoMySQL] =[]
            column_info_list : list[ColumnInfoMySQL] =[]
            #遍历表信息，将表信息插入meta数据库中的table_info表
            for table in meta_config.tables:

                #插入数据，查考SQLAlchemy中的ORM方法
                table_info = TableInfoMySQL(
                    id=table.name,
                    name = table.name,
                    role = table.role,
                    description = table.description
                )
                table_info_list.append(table_info)

                #查询字段类型
                column_types = await self.dw_mysql_repository.get_column_types(table.name)

                #变量字段信息，将字段信息插入meta数据库中的column_info表
                for column in table.columns:
                    #查询字段取值示例
                    column_values = await  self.dw_mysql_repository.get_example_values(table.name, column.name)


                    column_info = ColumnInfoMySQL(
                        id = f'{table.name}{column.name}',
                        name=column.name,
                        type=column_types[column.name],
                        role=column.role,
                        examples=column_values,
                        description=column.description,
                        alias=column.alias,
                        table_id=table.name,
                    )
                    column_info_list.append(column_info)

            async  with self.meta_mysql_repository.session.begin() :
                self.meta_mysql_repository.save_table_infos(table_info_list)
                self.meta_mysql_repository.save_column_infos(column_info_list)



        #3.根据配置文件同步指定的指标信息
        if meta_config.metrics:
            #配置文件中有指标信息
            #同步指标信息
            pass
