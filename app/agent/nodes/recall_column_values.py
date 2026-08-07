"""
召回字段取值
"""
from elasticsearch import Elasticsearch, AsyncElasticsearch
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.value_info import ValueInfo
from app.prompt.prompt_loader import prompt_loader
from app.core.log import logger
from app.repositories.es.value_es_repository import ValueEsRepository


async def recall_column_values(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    step = '召回字段取值'

    write({"type": "progress","step": step,"status": "running"})


    try:

        #1.根据用户提问，通过大模型，丰富关键字

        #用户提问内容
        query = state['query']

        #提示词
        prompt_temple  = prompt_loader(name ='extend_keywords_for_value_recall')
        prompt = PromptTemplate(template=prompt_temple,input_variables=['query'])

        #输出解释器
        parser =  JsonOutputParser()

        #链路
        chain = prompt | llm | parser

        #生成关键字
        llm_keywords = await  chain.ainvoke(input={'query':query})
        logger.info(f'大模型生成的关键字：{llm_keywords}')


        #将抽取的关键字与大模型生成的关键字，并用set去重
        keywords = state['keywords']
        keywords = set(keywords+llm_keywords)

        logger.info(f'合并后的关键字：{keywords}')

        #2.根据关键字进行检索
        column_value_map : dict[str,ValueInfo] = {}
        for keyword in keywords:

            #查询
            value_es_repository : ValueEsRepository = runtime.context['value_es_repository']
            column_values =  await   value_es_repository.search(keyword)
            for column_value in column_values:
                if column_value.id not in column_value_map :
                    column_value_map[column_value.id] = column_value


        retrieved_column_values =   column_value_map.values()

        logger.info(f'检索结果：{retrieved_column_values}')


        write({"type": "progress","step": step,"status": "success"})

        return {'retrieved_column_values': retrieved_column_values}

    except Exception as e:
        write({"type": "progress","step": step,"status": "error"})
        logger.error(f'{step}执行失败：{e}')
        raise













