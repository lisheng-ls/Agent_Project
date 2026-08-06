"""
召回指标信息
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.agent.llm import llm
from app.entities.metric_info import MetricInfo
from app.prompt.prompt_loader import prompt_loader
from app.core.log import logger

async def recall_metric(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    step = '召回指标信息'
    write({"type": "progress","step": step,"status": "running"})


    try:

        keywords = state['keywords']
        query = state['query']


        #1.根据用户提问，通过大模型生产关键词

        #提示词
        prompt_template = prompt_loader('extend_keywords_for_metric_recall')

        prompt = PromptTemplate(template = prompt_template,input_variables = ['query'])

        #输出解释器
        parser  = JsonOutputParser()

        #链路
        chain = prompt | llm | parser

        result  = await  chain.ainvoke(input={'query':query})

        #将生成的关键词，与提取的关键字合并并去重
        keywords = set(keywords+result)

        logger.info(f'合并后的关键词：{keywords}')

        #2.根据关键字检索
        #2.1将关键字向量化
        embedding_client =  runtime.context['embedding_client']

        metric_infos_map:dict[str,MetricInfo ] = {}
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)

            #2.1根据向量进行检索
            metric_qdrant_repository = runtime.context['metric_qdrant_repository']
            metric_infos = await metric_qdrant_repository.search(embedding)

            for metric_info in metric_infos:
                if metric_info.id not in metric_infos_map:
                    metric_infos_map[metric_info.id] = metric_info

        retrieved_metric_infos = list(metric_infos_map.values())

        logger.info(f'指标信息检索结果为:{retrieved_metric_infos}')

        write({"type": "progress","step": step,"status": "success"})


        return {'retrieved_metric_infos': retrieved_metric_infos}


    except Exception as e:
        write({"type": "progress","step": step,"status": "error"})
        logger.error(f'{step}执行失败：{e}')
        raise















