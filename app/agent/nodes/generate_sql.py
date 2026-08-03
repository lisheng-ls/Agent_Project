"""
生成sql
"""
import yaml
from langchain_classic.chains.query_constructor import parser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.prompt.prompt_loader import prompt_loader
from app.core.log import logger


async def generate_sql(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('生成sql')

    #通过生成的table_infos,metric_infos,query, date_info,db_info,根据大模型生成sql
    table_infos = state['table_infos']
    metric_infos = state['metric_infos']
    query = state['query']
    date_info = state['date_info']
    db_info = state['db_info']

    #将table_infos,metric_infos, date_info,db_info转换为yaml格式，方便大模型使用
    yaml_table_infos = yaml.dump(data=table_infos,encoding='utf-8',allow_unicode=True,default_flow_style=False,sort_keys=True)
    yaml_metric_infos = yaml.dump(data=metric_infos,encoding='utf-8',allow_unicode=True,default_flow_style=False,sort_keys=True)
    yaml_date_info = yaml.dump(data=date_info,encoding='utf-8',allow_unicode=True,default_flow_style=False,sort_keys=True)
    yaml_db_info = yaml.dump(data=db_info,encoding='utf-8',allow_unicode=True,default_flow_style=False,sort_keys=True)


    #提示词
    prompt_template = prompt_loader(name ='generate_sql' )
    prompt = PromptTemplate(template=prompt_template,input_variables=['table_infos','metric_infos','query','date_info','db_info'])

    #输出解释器
    parser = StrOutputParser()

    #链路
    chain = prompt | llm | parser

    #调用
    result = await  chain.ainvoke(
        input={
            'table_infos':yaml_table_infos,
            'metric_infos':yaml_metric_infos,
            'query':query,
            'date_info':yaml_date_info,
            'db_info':yaml_db_info
        })

    logger.info(f'生成的sql为：{result}')

    return {'sql':result}

