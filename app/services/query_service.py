import json

from langchain_openai import OpenAIEmbeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class QueryService:
    def __init__(self,
        column_qdrant_repository: ColumnQdrantRepository,
        embedding_client: OpenAIEmbeddings,
        metric_qdrant_repository: MetricQdrantRepository ,
        value_es_repository: ValueEsRepository,
        meta_mysql_repository: MetaMysqlRepository,
        dw_mysql_repository: DwMysqlRepository,):



        self.column_qdrant_repository: ColumnQdrantRepository = column_qdrant_repository
        self.embedding_client: OpenAIEmbeddings = embedding_client
        self.metric_qdrant_repository: MetricQdrantRepository = metric_qdrant_repository
        self.value_es_repository: ValueEsRepository = value_es_repository
        self.meta_mysql_repository: MetaMysqlRepository = meta_mysql_repository
        self.dw_mysql_repository: DwMysqlRepository = dw_mysql_repository

    async def query(self,query:str):
        state = DataAgentState(query=query)

        context = DataAgentContext(
            column_qdrant_repository=self.column_qdrant_repository,
            embedding_client=self.embedding_client,
            metric_qdrant_repository=self.metric_qdrant_repository,
            value_es_repository=self.value_es_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_mysql_repository
        )
        try:
            async  for chunk in graph.astream(input=state, context=context, stream_mode='custom'):
                yield f"data:{json.dumps(chunk,ensure_ascii = False,default = str)}\n\n"
        except Exception as e:
            error = {"type": "error","message": str(e)}
            error = json.dumps(error,ensure_ascii = False,default = str)
            yield f"data:{error}\n\n"
