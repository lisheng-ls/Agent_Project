from sqlalchemy.ext.asyncio import AsyncSession


class MetaMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session


    #将数据写入数据库中
    def save_table_info(self,list_info):
        self.session.add_all(list_info)

