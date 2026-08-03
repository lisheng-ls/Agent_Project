"""
合并召回信息
"""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, ColumnInfoState, TableInfoState, MetricInfoState
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.core.log import logger


async def merge_retrieved_info(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('合并召回信息')

    meta_mysql_repository = runtime.context['meta_mysql_repository']

    #1.处理表信息
    retrieved_column_infos:list[ColumnInfo] = state['retrieved_column_infos']
    retrieved_metric_infos:list[MetricInfo] = state['retrieved_metric_infos']
    retrieved_column_values:list[ValueInfo] = state['retrieved_column_values']


    #1.1将指标信息的关联字段存入retrieved_column_infos中

    metric_relevant_column_to_column_info_mapping : dict[str, ColumnInfo] = {retrieved_column_info.id :retrieved_column_info for retrieved_column_info in retrieved_column_infos }

    for retrieved_metric_info in retrieved_metric_infos:

        for relevant_column in retrieved_metric_info.relevant_columns:
            #relevant_column是column_info表中的id字段，

            #判断关联字段id是否已经在检索到的表信息中，只有不在才添加
            if relevant_column not in metric_relevant_column_to_column_info_mapping:


                #根据id字段查询所有信息
                relevant_column_info = await meta_mysql_repository.get_column_info(relevant_column)


                if relevant_column_info is None:
                    logger.warning(f"字段 {relevant_column} 不存在，跳过")
                    continue

                metric_relevant_column_to_column_info_mapping[relevant_column] = relevant_column_info

    logger.info(f'metric_relevant_column_to_column_info_mapping的值为：{metric_relevant_column_to_column_info_mapping}')


    #1.2将字段取值加入到对应字段的examples中
    for  retrieved_column_value in retrieved_column_values:

        #获取字段di和字段的取值
        column_id = retrieved_column_value.column_id
        value = retrieved_column_value.value

        #根据column_id获取该字段对应的examples,并将value的值添加
        #判断column_id是否在retrieved_column_info_mapping中，不在，则要先查询出column_id队友的字段信息，添加到retrieved_column_info_mapping中

        if column_id not in metric_relevant_column_to_column_info_mapping:
            column_info = await meta_mysql_repository.get_column_info(column_id)

            logger.info(f'column_info为：{column_info}')

            if column_info is None:
                logger.warning(f"字段 {column_id} 不存在，跳过")
                continue

            metric_relevant_column_to_column_info_mapping[column_id] = column_info

            #如果字段取值不存在，则添加
            if value not in metric_relevant_column_to_column_info_mapping[column_id].examples:
                metric_relevant_column_to_column_info_mapping[column_id].examples.append(value)


    #1.3按照表对字段进行分组
    #定义一个字典 ：key :表id ，值：column_info
    table_to_column_map : dict[str, list[ColumnInfo]] = {}
    for column_info in  metric_relevant_column_to_column_info_mapping.values() :

        #获取表字段
        table_id = column_info.table_id

        if table_id is None:
            logger.warning("table_id为空，跳过")
            continue

        if table_id not in table_to_column_map:
            table_to_column_map[table_id] = []

        table_to_column_map[table_id].append(column_info)


    #防止主外键丢失，手动给每个表加上主外键

    #根据table_id，从column_info表中的获取所有主键和外键的字段信息

    for table_id in table_to_column_map.keys():

        foreign_primary_key_column_infos = await  meta_mysql_repository.get_key_info(table_id)

        #字段主键和外键字段信息添加到table_to_column_map.value中

        #判断主键和外键的字段id是否在之前的数据中，不存在，则添加

        column_id_infos = [ column_info.id for column_info in table_to_column_map[table_id]]
        for column_info in foreign_primary_key_column_infos:
            if column_info.id not in column_id_infos:
                table_to_column_map[table_id].append(column_info)


    #1.4整理出需要的table格式：TableInfoState

    table_infos: list[TableInfoState] = []

    for table_id,column_infos  in iter(table_to_column_map.items()):
        columns = [
           ColumnInfoState(
            name = column_info.name,
            type= column_info.type,
            role= column_info.role,
            examples= column_info.examples,
            description= column_info.description,
            alias = column_info.alias,)  for column_info in column_infos]


        #根据table_id 从table_info中查询表的相关信息
        table_info : TableInfo |None  =  await meta_mysql_repository.get_table_info(table_id)

        if table_info is None:
            logger.warning(f"表ID {table_id} 查询不到，跳过该表")
            continue


        table_info_state = TableInfoState(
            name = table_info.name,
            role = table_info.role,
            description= table_info.description,
            columns=columns,
        )
        table_infos.append(table_info_state)




    #2.处理指标信息
    metric_infos  = [
        MetricInfoState(
        name = retrieved_metric_info.name,
        description= retrieved_metric_info.description,
        relevant_columns=retrieved_metric_info.relevant_columns,
        alias= retrieved_metric_info.alias,
        )

        for retrieved_metric_info in retrieved_metric_infos
    ]


    logger.info(f'表信息：{table_infos}')
    logger.info(f'指标信息:{metric_infos}')


    return {
        'table_infos': table_infos,
        'metric_infos': metric_infos
    }