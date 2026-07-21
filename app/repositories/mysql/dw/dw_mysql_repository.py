from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.clients.mysql_client_manager import db_dw_client_manager


class DwMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session



    async def get_column_types(self,table_name):
        sql = f'show columns from {table_name}'
        result = await self.session.execute(text(sql))
        rows = result.mappings().fetchall()



        return {row['Field']: row['Type'] for row in rows }


    async def get_example_values(self,table_name,column_name):
        sql = f'SELECT DISTINCT {column_name} FROM {table_name} LIMIT 10'
        result = await self.session.execute(text(sql))
        rows = result.fetchall()
        return [rows[0] for row in rows]