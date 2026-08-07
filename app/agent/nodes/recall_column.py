"""
召回字段信息
"""


from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import prompt_loader
from app.core.log import logger



async def recall_column(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer

    step = '召回字段信息'
    write({"type": "progress","step": step,"status": "running"})


    try:
        #state中的值
        keywords = state['keywords']
        query = state['query']

        #context中的值

        #qdrant
        column_qdrant_repository = runtime.context['column_qdrant_repository']

        #embedding
        embedding_client = runtime.context['embedding_client']



        #根据用户提问，通过大模型丰富关键词列表
        #提示词
        prompt_temple = prompt_loader('extend_keywords_for_column_recall')
        prompt = PromptTemplate(
            template=prompt_temple,
            input_variables=['query']
        )

        #输出解释器
        parser = JsonOutputParser()

        #链路
        chain = prompt | llm  |  parser

        result = await chain.ainvoke(input={'query':query},)

        #将状态中的keywords与大模型生成的keywords合并，用set进行去重
        keywords = set(keywords+result)

        logger.info(f'合并后的关键字：{keywords}')

        #从qdrant中检索字段信息
        column_infos_map:dict[str, ColumnInfo] = {}
        for keyword in keywords:
            #对keyword进行向量化
            embedding = await embedding_client.aembed_query(keyword)
            column_infos :list[ColumnInfo] = await column_qdrant_repository.search(embedding)
            for column_info in column_infos:
                if column_info.id not in column_infos_map:
                    column_infos_map[column_info.id] = column_info

        retrieved_column_infos = column_infos_map.values()

        logger.info(f'检索的字段信息：{retrieved_column_infos}')

        write({"type": "progress","step": step,"status": "success"})

        return {'retrieved_column_infos':retrieved_column_infos}

    except Exception as e:
        write({"type": "progress","step": step,"status": "error"})
        logger.error(f'{step}执行失败：{e}')
        raise
