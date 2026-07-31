"""
抽取关键字
"""
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def extract_keywords(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('抽取关键字')
    import asyncio
    await asyncio.sleep(1)