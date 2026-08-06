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
    step = '增加额外上下文'
    writer({"type": "progress","step": step,"status": "running"})
    """
    需要额外添加data_info，和db_info上下文
    """
    try:
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
        writer({"type": "progress","step": step,"status": "success"})

        return {'db_info':db_info,
                'date_info':date_info}
    except Exception as e:
        logger.error(f'{step}执行失败：{e}')
        writer({"type": "progress","step": step,"status": "error"})
        raise