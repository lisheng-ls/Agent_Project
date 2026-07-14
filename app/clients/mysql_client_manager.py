"""
mysql客户端
"""
import asyncio

from typing import Optional

from huggingface_hub import export_entries_as_dduf
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from app.conf.app_config import DbConfig, load_app_config


class MysqlClientManager:

    def __init__(self,mysql_config:DbConfig):
        self.engine : Optional[AsyncEngine]  = None
        self.mysql_config = mysql_config

    def _get_url(self):
        user = self.mysql_config.user
        password = self.mysql_config.password
        host = self.mysql_config.host
        port = self.mysql_config.port
        dbname = self.mysql_config.database
        return f"mysql+asyncmy://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4"

    def create_mysql_client(self):
        self.engine = create_async_engine(
            #数据库连接地址
            self._get_url(),
            #连接池数量
            pool_size=10,
            #连接前默然尝试连接看通不通
            pool_pre_ping = True
        )
        return self.engine

    async def mysql_close(self):
        await self.engine.dispose()

app_config = load_app_config()

#db_meta数据库客户端
db_meta_client_manager = MysqlClientManager(app_config.db_meta)

#db_dw数据库客户端
db_dw_client_manager = MysqlClientManager(app_config.db_dw)

if __name__ == '__main__':

    #初始化客户端
    db_dw_client_manager.create_mysql_client()

    engine = db_dw_client_manager.engine
    print('客户端初始化成功')
    async def test():
       async  with AsyncSession(
            engine,
           #将数据刷新进数据库，但不提交事务，查询可以查询出数据
            autoflush=True,
           #
           export_on_commit = False
            ) as session :
            sql = "select * from fact_order limit 10"
            result = await session.execute(text(sql))

            rows = result.fetchall()
            print(rows)
            await db_dw_client_manager.mysql_close()
    asyncio.run(test())




