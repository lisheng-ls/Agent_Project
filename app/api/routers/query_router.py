from fastapi import APIRouter, Depends, Query
from langchain_openai import OpenAIEmbeddings
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.qdrant_client_manager import QdrantClientManager, qdrant_client_manager
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.query_service import QueryService

query_router = APIRouter()





@query_router.post("/api/query")
async def query_handle(query:QuerySchema,query_service:QueryService = Depends(get_query_service)):
    return StreamingResponse(content=query_service.query(query.query))