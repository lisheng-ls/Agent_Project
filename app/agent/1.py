import asyncio
from typing import TypedDict

from langgraph.graph import StateGraph
from langgraph.types import StreamWriter
from langgraph.constants import START, END
class State(TypedDict):
    topic: str
    joke: str

# Add writer as an argument in the function signature of the async node or tool
# LangGraph will automatically pass the stream writer to the function
async def generate_joke(state: State, writer: StreamWriter):
    writer({"custom_key": "Streaming custom data while generating a joke"})
    return {"joke": f"This is a joke about {state['topic']}"}

graph = (
    StateGraph(State)
    .add_node(generate_joke)
    .add_edge(START, "generate_joke")
    .compile()
)


# Set stream_mode="custom" to receive the custom data in the stream  #
async def test():
    async for chunk in graph.astream(
            {"topic": "ice cream"},
            stream_mode="custom",
            version="v2",
    ):
        if chunk["type"] == "custom":
            print(chunk["data"])


asyncio.run(test())