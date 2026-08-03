"""
过滤指标信息
"""
import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.prompt.prompt_loader import prompt_loader
from app.core.log import logger

async def filter_metric(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('过滤指标信息')


    #1.通过大模型过滤指标信息
    metric_infos = state['metric_infos']
    query = state['query']

    #将指标信息转化为yaml格式数据方便大模型解析

    metric_infos_yaml = yaml.dump(
        data=metric_infos,
        encoding='utf-8',
        allow_unicode=True,
        default_flow_style=False,
        sort_keys = True
    )


    #提示词
    prompt_template = prompt_loader(name = 'filter_metric_info')
    prompt = PromptTemplate(template=prompt_template,input_variables=['query','metric_infos'])

    #输出解释器
    parser = JsonOutputParser()

    #链路
    chain = prompt | llm | parser

    #调用
    result  =  await  chain.ainvoke(input={'query': query, 'metric_infos': metric_infos_yaml})

    logger.info(f'大模型过滤后的指标信息：{result}')

    #2.根据大模型生成的结果，处理metric_infos
    filter_metric_infos = [metric_info for metric_info in metric_infos if metric_info['name'] in result]


    #处理后的指标信息
    logger.info(f'处理后的指标信息:{filter_metric_infos}')

    return {'metric_infos': filter_metric_infos}







    





