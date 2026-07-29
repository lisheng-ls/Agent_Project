import uuid
from dataclasses import asdict
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.clients.embedding_client_manager import EmbeddingClientManager
from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


class MetaKnowledgeService:
    def __init__(self,
                meta_mysql_repository:MetaMysqlRepository,
                dw_mysql_repository:DwMysqlRepository,
                column_qdrant_repository:ColumnQdrantRepository,
                embedding_client:HuggingFaceEndpointEmbeddings):

        self.meta_mysql_repository:MetaMysqlRepository = meta_mysql_repository
        self.dw_mysql_repository:DwMysqlRepository = dw_mysql_repository
        self.column_qdrant_repository:ColumnQdrantRepository = column_qdrant_repository
        self.embedding_client:HuggingFaceEndpointEmbeddings = embedding_client

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
            table_infos : list[TableInfo] = []
            column_infos : list[ColumnInfo]  = []
            #2.1将表信息和字段信息存储到meta数据库中
            for table in meta_config.tables or [] :

                #将表信息存储值table_info 表中
                table_info = TableInfo(
                    id = table.name,
                    name = table.name,
                    role = table.role,
                    description = table.description
                )
                table_infos.append(table_info)

                #查询字段类型
                type_list =  await self.dw_mysql_repository.get_column_types(table.name)

                for columns in table.columns:

                    #查询字段的值
                    column_value = await self.dw_mysql_repository.get_column_values(columns.name,table.name)

                    # 将字段信息存储至column_info表中
                    columns_info = ColumnInfo(
                        id = f"{table.name}.{columns.name}",
                        name = columns.name,
                        type = type_list[columns.name],
                        role = columns.role,
                        examples = column_value,
                        description=columns.description,
                        alias=columns.alias,
                        table_id = table.name
                    )
                    column_infos.append(columns_info)

            #将表信息写入table_info中，将字段信息写入column_info中
            async  with self.meta_mysql_repository.session.begin():
                    self.meta_mysql_repository.save_table_info(table_infos)
                    self.meta_mysql_repository.save_column_info(column_infos)


            #2.2对字段信息建立向量索引

            #2.2.1创建集合
            await  self.column_qdrant_repository.ensure_collection()

            #2.2.2添加向量
            points : list[dict] = []
            for column_info in column_infos:
                points.append(
                    {
                        'id':uuid.uuid4(),
                        'embedding_text':column_info.name,
                        'payload':asdict(column_info)
                    }
                )

                points.append(
                    {
                        'id':uuid.uuid4(),
                        'embedding_text':column_info.description,
                        'payload':asdict(column_info)
                    }
                )

                for alia in column_info.alias:
                    points.append(
                        {
                            'id':uuid.uuid4(),
                            'embedding_text':alia,
                            'payload':asdict(column_info)
                        }
                    )
            #2.2.3批量向量化
            embedding_texts = [point['embedding_text']for point in points]

            #防止数据过多，选择通过embedding_batch_size分批次向量化
            embedding_batch_size = 20
            embeddings:list[list[float]] = []
            for i in range(0, len(embedding_texts), embedding_batch_size):
                batch_embedding_text = embedding_texts[i:i+embedding_batch_size]
                batch_embedding = await self.embedding_client.aembed_documents(batch_embedding_text)
                embeddings.extend(batch_embedding)
            ids = [ point['id'] for point in points ]
            payloads = [ point['payload'] for point in points ]
            #将数据存入向量数据库qdrant中
            await self.column_qdrant_repository.upsert(embeddings, ids, payloads)

        #2.3对指定的维度字段建立全文索引
         

        #3.根据配置文件读取指标信息

        #判断是否有指标信息
        if meta_config.metrics:
            pass
            #3.1将指标信息存储到meta数据库中

            #3.2对指标信息建立向量索引