from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class DwMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    #查询表字段类型
    async def get_column_types(self,table_name):
        sql = f'show columns from {table_name}'
        results = await self.session.execute(text(sql))
        results = results.mappings().fetchall()
        return { result['Field'] : result['Type']  for result in results }


    #查询表中某个字段的值
    async def  get_column_values(self,column_name,table_name,limit = 10):
        sql = f'select {column_name} from {table_name} limit {limit} '
        results = await  self.session.execute(text(sql))
        results =  results.fetchall()
        return  [result[0] for result in results]

    async def get_mysql_info(self):
        sql = 'select version()'
        version = await self.session.execute(text(sql))
        version = version.scalar()

        dialect = self.session.get_bind().dialect.name
        return {'version':version,'dialect':dialect}

    async def validate_sql(self, sql):
            sql = f'explain {sql}'
            await self.session.execute(text(sql))

    async def run_sql(self, sql:str)->list[dict]:
        results = await self.session.execute(text(sql))
        results = results.mappings().fetchall()
        return [dict(result) for result in results]





