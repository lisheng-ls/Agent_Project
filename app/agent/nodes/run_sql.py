"""
执行sql
"""
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def run_sql(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    step = '执行sql'

    write({"type": "progress","step": step,"status": "success"})

    try:
        #根据生成的sql执行sql语句
        sql = state['sql']
        dw_mysql_repository  = runtime.context['dw_mysql_repository']

        result = await dw_mysql_repository.run_sql(sql)

        logger.info(f'sql执行结果为：{result}')


        write({"type": "progress","step": step,"status": "success"})

        write({"type": "result","data": result})

    except Exception as e:
        write({"type": "progress","step": step,"status": "error"})
        logger.error(f'{step}执行失败：{e}')
        raise