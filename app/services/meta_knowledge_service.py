import uuid
from dataclasses import asdict
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf


from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.core.log import logger

class MetaKnowledgeService:
    def __init__(self,
                meta_mysql_repository:MetaMysqlRepository,
                dw_mysql_repository:DwMysqlRepository,
                column_qdrant_repository:ColumnQdrantRepository,
                embedding_client:HuggingFaceEndpointEmbeddings,
                 value_es_repository:ValueEsRepository,
                 metric_qdrant_repository:MetricQdrantRepository):

        self.meta_mysql_repository:MetaMysqlRepository = meta_mysql_repository
        self.dw_mysql_repository:DwMysqlRepository = dw_mysql_repository
        self.column_qdrant_repository:ColumnQdrantRepository = column_qdrant_repository
        self.embedding_client:HuggingFaceEndpointEmbeddings = embedding_client
        self.value_es_repository:ValueEsRepository = value_es_repository
        self.metric_qdrant_repository:MetricQdrantRepository = metric_qdrant_repository

    # 2.根据配置文件读取表信息
    # 2.1将表信息和字段信息存储到meta数据库中
    async def _save_table_info_to_meta(self,meta_config:MetaConfig) -> list[ColumnInfo]:
        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []
        # 2.1将表信息和字段信息存储到meta数据库中
        for table in meta_config.tables or []:

            # 将表信息存储值table_info 表中
            table_info = TableInfo(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description
            )
            table_infos.append(table_info)

            # 查询字段类型
            type_list = await self.dw_mysql_repository.get_column_types(table.name)

            for columns in table.columns:
                # 查询字段的值
                column_value = await self.dw_mysql_repository.get_column_values(columns.name, table.name)

                # 将字段信息存储至column_info表中
                columns_info = ColumnInfo(
                    id=f"{table.name}.{columns.name}",
                    name=columns.name,
                    type=type_list[columns.name],
                    role=columns.role,
                    examples=column_value,
                    description=columns.description,
                    alias=columns.alias,
                    table_id=table.name
                )
                column_infos.append(columns_info)

        # 将表信息写入table_info中，将字段信息写入column_info中
        async  with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.save_table_info(table_infos)
            self.meta_mysql_repository.save_column_info(column_infos)

        return column_infos

    # 2.2对字段信息建立向量索引
    async def _save_column_info_to_qdrant(self,column_infos:list[ColumnInfo]):
        # 2.2对字段信息建立向量索引

        # 2.2.1创建集合
        await  self.column_qdrant_repository.ensure_collection()

        # 2.2.2添加向量
        points: list[dict] = []
        for column_info in column_infos:
            points.append(
                {
                    'id': uuid.uuid4(),
                    'embedding_text': column_info.name,
                    'payload': asdict(column_info)
                }
            )

            points.append(
                {
                    'id': uuid.uuid4(),
                    'embedding_text': column_info.description,
                    'payload': asdict(column_info)
                }
            )

            for alia in column_info.alias:
                points.append(
                    {
                        'id': uuid.uuid4(),
                        'embedding_text': alia,
                        'payload': asdict(column_info)
                    }
                )
        # 2.2.3批量向量化
        embedding_texts = [point['embedding_text'] for point in points]

        # 防止数据过多，选择通过embedding_batch_size分批次向量化
        column_embeddings: list[list[float]] = []
        embedding_batch_size = 5
        for i in range(0, len(embedding_texts), embedding_batch_size):
            batch_embedding_text = embedding_texts[i:i + embedding_batch_size]
            batch_embedding = await self.embedding_client.aembed_documents(batch_embedding_text)
            column_embeddings.extend(batch_embedding)
            
        logger.info('embedding向量haul成功')

        ids = [point['id'] for point in points]
        payloads = [point['payload'] for point in points]
        # 将数据存入向量数据库qdrant中
        await self.column_qdrant_repository.upsert(column_embeddings, ids, payloads)

    # 2.3对指定的维度字段建立全文索引
    async def _save_value_info_to_es(self,meta_config:MetaConfig) :

        # 创建index
        await self.value_es_repository.ensure_index()

        # 添加数据
        column_value_infos: list[ValueInfo] = []
        for table_info in meta_config.tables or []:

            for column_info in table_info.columns:
                # 读取当前字段的所有值
                current_column_values = await self.dw_mysql_repository.get_column_values(table_name=table_info.name,
                                                                                         column_name=column_info.name,
                                                                                         limit=10000000000)

                # 根据字段的信息，生成index需要的信息
                column_value_info = [
                    ValueInfo(
                        id=f"{table_info.name}.{column_info.name}.{current_column_value}",
                        value=current_column_value,
                        column_id=f'{table_info.name}.{column_info.name}'
                    )
                    for current_column_value in current_column_values
                ]

                column_value_infos.extend(column_value_info)

        await  self.value_es_repository.index(column_value_infos)

    # 3.根据配置文件读取指标信息
    # 3.1将指标信息存储到meta数据库中
    async  def _save_metric_info_to_meta(self,meta_config:MetaConfig) -> list[MetricInfo]:
        metric_infos: list[MetricInfo] = []
        for metric in meta_config.metrics or []:
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            )
            metric_infos.append(metric_info)
        async  with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.save_metric_info(metric_infos)

        return metric_infos

    # 3.2.2添加向量
    async  def _save_metric_info_to_qdrant(self,metric_infos:list[MetricInfo]) -> None:
        # 3.2对指标信息建立向量索引
        # 3.2.1创建集合
        await self.metric_qdrant_repository.ensure_collection()

        # 3.2.2添加向量
        metric_points: list[dict] = []
        for metric_info in metric_infos:
            # 将name字段的值添加到向量数据库
            metric_points.append(
                {
                    'id': uuid.uuid4(),
                    'embedding_text': metric_info.name,
                    'payload': asdict(metric_info),
                }
            )

            # 将description字段的值添加到向量数据库
            metric_points.append(
                {
                    'id': uuid.uuid4(),
                    'embedding_text': metric_info.description,
                    'payload': asdict(metric_info),
                }
            )

            # 将description字段的值添加到向量数据库
            for alia in metric_info.alias:
                metric_points.append(
                    {
                        'id': uuid.uuid4(),
                        'embedding_text': alia,
                        'payload': asdict(metric_info),
                    }
                )
        # 3.2.3批量向量化
        metric_embeddings: list[list[float]] = []
        embedding_text = [metric_point['embedding_text'] for metric_point in metric_points]
        batch_size = 20
        # 防止数据embedding_text 过大，通过batch_size 分批次向量化

        for i in range(0, len(embedding_text), batch_size):
            batch_embedding_text = embedding_text[i:i + batch_size]
            batch_embedding = await self.embedding_client.aembed_documents(batch_embedding_text)
            metric_embeddings.extend(batch_embedding)

        metric_ids = [metric_point['ids'] for metric_point in metric_points]
        metric_payloads = [metric_point['payload'] for metric_point in metric_points]
        # 将数据存入向量数据库qdrant中
        await self.metric_qdrant_repository.upsert(metric_embeddings, metric_ids, metric_payloads)



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

        logger.info('配置文件读取成功：')
        # 2.根据配置文件读取表信息

        # 判断是否有表信息
        if meta_config.metrics:
            # 2.1将表信息和字段信息存储到meta数据库中
            column_infos =  await self._save_table_info_to_meta(meta_config)
            logger.info('保存表信息和字段信息到meta数据库中成功')

            # 2.2对字段信息建立向量索引
            await self._save_column_info_to_qdrant(column_infos)
            logger.info('字段建立向量索引成功')

            # 2.3对指定的维度字段建立全文索引
            await self._save_value_info_to_es(meta_config)
            logger.info('制定维度字段建立全文索引成功')

        #3.根据配置文件读取指标信息
        #判断是否有指标信息

        if meta_config.metrics:
            # 3.1将指标信息存储到meta数据库中
            metric_infos = await self._save_metric_info_to_meta(meta_config)
            logger.info('保存指标信息到meta数据库中成功')

            #构建点
            #3.2.2添加向量
            await self._save_metric_info_to_qdrant(metric_infos)
            logger.info('字段建立向量索引成功')