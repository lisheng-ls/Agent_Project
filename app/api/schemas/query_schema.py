from pydantic import BaseModel


class QuerySchema(BaseModel):
    query: str = '统计华北地区的销售总额'


