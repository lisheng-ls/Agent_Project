"""
过滤指标信息
"""
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def filter_metric(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('过滤指标信息')
    import asyncio
    await asyncio.sleep(1)