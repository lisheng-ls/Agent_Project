"""
过滤表信息
"""
import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, TableInfoState
from app.prompt.prompt_loader import prompt_loader
from app.core.log import logger

async def filter_table(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    step ='过滤表信息'
    write({"type": "progress","step": step,"status": "running"})
    """
    通过大模型，过滤表信息，生成相对应的格式(提示词中有)，并根据过滤后的结果，处理table_info，
    """

    try:
        #将table_infos 转换为yaml样式字符串
        table_infos =  state['table_infos']


        table_infos_yaml = yaml.dump(
            data=table_infos,
            allow_unicode = True,  #允许中文
            encoding = 'utf-8',#编码格式
            sort_keys = False,
            default_flow_style=False) #字段排列顺序，原table_infos什么排列就是什么排列
        logger.info(f'将table_info转换为yaml样式后的数据：{table_infos}')

        query  = state['query']

        #提示词
        prompt_template = prompt_loader(name = 'filter_table_info')
        prompt = PromptTemplate(template = prompt_template,input_variables=['query','table_infos'])


        #输出解释器
        parser = JsonOutputParser()

        #链路
        chain = prompt | llm | parser


        #调用
        results= await  chain.ainvoke(input={
            'query': query,
            'table_infos': table_infos_yaml
        }
        )

        logger.info(f'大模型过滤后的数据：{results}')


        #根据大模型生成的数据，处理原始table_info
        filter_table_infos: list[TableInfoState] = []
        for table_info in table_infos:
            if table_info['name'] in results:
                table_info['columns'] = [column_info for column_info in table_info['columns'] if column_info['name']  in   results[table_info['name']] ]
                filter_table_infos.append(table_info)

        #处理后的table_infos
        logger.info(f'处理后的table_info:{filter_table_infos}')
        write({"type": "progress","step": step,"status": "success"})

        return {'table_infos':filter_table_infos}

    except Exception as e:
        write({"type": "progress","step": step,"status": "error"})
        logger.error(f'{step}执行失败：{e}')
        raise


















