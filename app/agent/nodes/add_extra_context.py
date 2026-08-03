"""
增加额外上下文
"""
from datetime import date

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DbInfoState
from app.core.log import logger


async def add_extra_context(state: DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer('添加额外上下文')
    """
    需要额外添加data_info，和db_info上下文
    """

    #添加data_info
    today = date.today()
    date_str = today.strftime("%Y-%m-%d")
    weekday = today.strftime("%A")
    quarter = f'Q{(today.month-1) // 3 +1}'
    date_info = DateInfoState(date=date_str,weekday=weekday,quarter=quarter)

    #添加db_info,从db数据库中查
    dw_mysql_repository = runtime.context['dw_mysql_repository']
    db_info = await dw_mysql_repository.get_mysql_info()
    #转换为DbInfoState格式
    db_info = DbInfoState(**date_info)

    logger.info(f'添加的上下文：date_info:{date_info},db_info:{db_info}')

    return {'db_info':db_info,
            'date_info':date_info}
