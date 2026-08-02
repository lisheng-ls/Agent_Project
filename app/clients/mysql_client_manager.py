"""
mysql客户端
"""
import asyncio

from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker,create_async_engine


from app.conf.app_config import DbConfig, app_config


class MysqlClientManager:

    def __init__(self,mysql_config:DbConfig):
        self.engine : Optional[AsyncEngine]  = None
        self.session_factory =  None
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
        self.session_factory = async_sessionmaker(
            self.engine,
            #将数据刷新进数据库，但不提交事务，查询可以查询出数据
            autoflush=True,
            #
            expire_on_commit = False
        )
        return self.session_factory

    async def close(self):
        await self.engine.dispose()


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
       async  with db_dw_client_manager.session_factory()  as session :


            sql = "select customer_id from dim_customer limit 10"
            #sql = "show columns from dim_customer"
            result = await session.execute(text(sql))
            rows = result.fetchall()
            print(rows)
            # dist = {row['Field']:row['Type'] for row in rows}
            # print(dist)
            list = [row[0] for row in rows]
            print(list)
            await db_dw_client_manager.close()

    asyncio.run(test())




