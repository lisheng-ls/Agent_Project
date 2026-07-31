"""
召回字段取值
"""
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def recall_column_values(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('召回字段取值')
    import asyncio
    await asyncio.sleep(1)