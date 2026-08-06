"""
校验sql
"""
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def validate_sql(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer

    step = '校验sql'

    write({"type": "progress","step": step,"status": "running"})

    """
    通过explain<sql>进行校验sql
    
    """
    try:
        sql = state['sql']
        dw_mysql_repository = runtime.context['dw_mysql_repository']

        try:
            await dw_mysql_repository.validate_sql(sql)
            logger.info(f'sql校验结果：sql语法正确')
            write({"type": "progress","step": step,"status": "success"})
            return {'error': None}

        except Exception as e:
            logger.error(f'sql校验结果：sql语法错误，报错内容：{e}')
            write({"type": "progress","step": step,"status": "success"})
            return {'error': e}

    except Exception as e:
        write({"type": "progress","step": step,"status": "error"})
        logger.error(f'{step}执行失败：{e}')
        raise