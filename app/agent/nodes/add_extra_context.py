"""
增加额外上下文
"""


from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def add_extra_context(state: DataAgentState,runtime:Runtime[DataAgentContext]):
    write = runtime.stream_writer('添加上下文')
    import asyncio
    await asyncio.sleep(1)