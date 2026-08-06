from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.ec_client_manager import es_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.mysql_client_manager import db_dw_client_manager, db_meta_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager


@asynccontextmanager

async def lifespan(app: FastAPI):
    #初始化客户端
    # qdrant客户端
    qdrant_client_manager.create_client()
    qdrant_client = qdrant_client_manager.client

    # embedding客户端
    embedding_client_manager.create_client()
    embedding_client = embedding_client_manager.client

    # es客户端
    es_client_manager.creat_es_client()
    es_client = es_client_manager.client

    # mysql客户端
    db_meta_client_manager.create_mysql_client()
    db_dw_client_manager.create_mysql_client()


    yield


    #关闭客户端

    # 关闭qdrant客户端
    await qdrant_client_manager.close()

    # 关闭es客户端
    await es_client_manager.close()

    # 关闭mysql客户端
    await db_meta_client_manager.close()
    await db_dw_client_manager.close()
