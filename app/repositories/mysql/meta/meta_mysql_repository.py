from sqlalchemy.ext.asyncio import AsyncSession


class MetaMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    def save_table_infos(self, table_info_list):
        self.session.add_all(table_info_list)

    def save_column_infos(self, column_info_list):
        self.session.add_all(column_info_list)

