from typing import TypedDict


class DataAgentState(TypedDict):
    error:str | None  #校验sql出现的错误信息