import argparse
import asyncio
from pathlib import Path

from app.clients.ec_client_manager import es_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.mysql_client_manager import db_meta_client_manager, db_dw_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager

from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService





async def build(config_path:Path) -> None:
    db_meta_client_manager.create_mysql_client()
    db_dw_client_manager.create_mysql_client()

    #qdrant客户端
    qdrant_client_manager.create_client()
    qdrant_client = qdrant_client_manager.client

    #embedding客户端
    embedding_client_manager.create_client()
    embedding_client = embedding_client_manager.client

    #es客户端
    es_client_manager.creat_es_client()
    es_client = es_client_manager.client

    async with db_meta_client_manager.session_factory() as meta_session, db_dw_client_manager.session_factory() as dw_session  :
        meta_mysql_repository = MetaMysqlRepository(meta_session)
        dw_mysql_repository = DwMysqlRepository(dw_session)
        column_qdrant_repository = ColumnQdrantRepository(qdrant_client)
        value_es_repository = ValueEsRepository(es_client)
        metric_qdrant_repository = MetricQdrantRepository(qdrant_client)


        meta_knowledge_service = MetaKnowledgeService(
            meta_mysql_repository=meta_mysql_repository,
            dw_mysql_repository=dw_mysql_repository,
            column_qdrant_repository=column_qdrant_repository,
            embedding_client=embedding_client,
            value_es_repository=value_es_repository,
            metric_qdrant_repository=metric_qdrant_repository)
        
        await meta_knowledge_service.build(config_path)


    await  db_meta_client_manager.close()
    await  db_dw_client_manager.close()
    await  qdrant_client_manager.close()
    await  es_client_manager.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--config')
    args = parser.parse_args()
    config_path = args.config
    asyncio.run(build(config_path))

    #控制台执行脚本命令：python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml