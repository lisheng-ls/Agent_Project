"""
校验sql
"""
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def validate_sql(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('校验sql')
    """
    通过explain<sql>进行校验sql
    
    """

    sql = state['sql']

    dw_mysql_repository = runtime.context['dw_mysql_repository']
    try:
        await dw_mysql_repository.validate_sql(sql)

        logger.info(f'sql校验结果：sql语法正确，错误内容：{state["error"]}')

        return {'explain': None}

    except Exception as e:
        logger.error(f'sql校验结果：sql语法错误，报错内容：{e}')
        return {'error': e}
