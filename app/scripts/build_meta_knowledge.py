import argparse
import asyncio
from pathlib import Path

from app.clients.mysql_client_manager import db_dw_client_manager, db_meta_client_manager
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(config_path:Path) -> None:
    db_dw_client_manager.create_mysql_client()
    db_meta_client_manager.create_mysql_client()

    async  with db_meta_client_manager.session_factory()  as meta_session,db_dw_client_manager.session_factory() as dw_session:
        meta_mysql_repository = MetaMysqlRepository(meta_session)
        dw_mysql_repository = DwMysqlRepository(dw_session)
        meta_knowledge_service = MetaKnowledgeService(
            meta_mysql_repository,
            dw_mysql_repository)
        meta_session.add_all(meta_knowledge_service)
        await meta_knowledge_service.build(config_path)

    await db_meta_client_manager.mysql_close()
    await db_dw_client_manager.mysql_close()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--config')
    args = parser.parse_args()
    config_path = args.config
    asyncio.run(build(config_path))