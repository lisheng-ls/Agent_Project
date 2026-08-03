import asyncio

from langgraph.graph import StateGraph
from langgraph.constants import START, END
from app.agent.context import DataAgentContext
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_column_values import recall_column_values
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.validate_sql import validate_sql
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.extact_keywords import extract_keywords
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.merge_retrieved_info import merge_retrieved_info
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.run_sql import run_sql
from app.agent.state import DataAgentState
from app.clients.ec_client_manager import es_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.mysql_client_manager import db_meta_client_manager, db_dw_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw import dw_mysql_repository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

#创建graph
graph_build = StateGraph(state_schema=DataAgentState,context_schema=DataAgentContext)

#添加节点
graph_build.add_node('extract_keywords',extract_keywords)
graph_build.add_node('recall_column',recall_column)
graph_build.add_node('recall_metric',recall_metric)
graph_build.add_node('recall_column_values',recall_column_values)
graph_build.add_node('merge_retrieved_info',merge_retrieved_info)
graph_build.add_node('filter_metric',filter_metric)
graph_build.add_node('filter_table',filter_table)
graph_build.add_node('add_extra_context',add_extra_context)
graph_build.add_node('generate_sql',generate_sql)
graph_build.add_node('validate_sql',validate_sql)
graph_build.add_node('correct_sql',correct_sql)
graph_build.add_node('run_sql',run_sql)


#添加边
# ========== 并行扇出：extract_keywords 同时启动三个召回节点 ==========
graph_build.add_edge(START,'extract_keywords')
graph_build.add_edge('extract_keywords','recall_column')
graph_build.add_edge('extract_keywords','recall_metric')
graph_build.add_edge('extract_keywords','recall_column_values')

# ========== 汇聚：三个召回节点全部完成后进入merge ==========
graph_build.add_edge('recall_column','merge_retrieved_info')
graph_build.add_edge('recall_metric','merge_retrieved_info')
graph_build.add_edge('recall_column_values','merge_retrieved_info')

# merge之后并行执行 filter_metric / filter_table
graph_build.add_edge('merge_retrieved_info','filter_metric')
graph_build.add_edge('merge_retrieved_info','filter_table')

# 两个过滤节点都完成后进入 add_extra_context
graph_build.add_edge('filter_metric','add_extra_context')
graph_build.add_edge('filter_table','add_extra_context')

graph_build.add_edge('add_extra_context','generate_sql')
graph_build.add_edge('generate_sql','validate_sql')
graph_build.add_conditional_edges(
    source='validate_sql',
    path=lambda state :"run_sql" if not state['error'] else "correct_sql",
    path_map = {'run_sql':'run_sql','correct_sql':'correct_sql'}
    )
graph_build.add_edge('correct_sql','run_sql')
graph_build.add_edge('run_sql',END)

graph = graph_build.compile()
#print(graph.get_graph().draw_ascii())

if __name__ == '__main__':

        async def test():
            state = DataAgentState(
                query='统计华北地区的销售总额',
                keywords = [],
                retrieved_column_infos = [],
                retrieved_metric_infos = [],
                retrieved_column_values = [],
                metric_infos=[],
                table_infos = [],
                date_info = None,
                db_info = None,
                sql= '',
                sql_search_result='',
                error = None
            )

                    #qdrant客户端
            qdrant_client_manager.create_client()
            qdrant_client = qdrant_client_manager.client

            #embedding客户端
            embedding_client_manager.create_client()
            embedding_client = embedding_client_manager.client

            #es客户端
            es_client_manager.creat_es_client()
            es_client = es_client_manager.client


            #mysql客户端
            db_meta_client_manager.create_mysql_client()
            db_dw_client_manager.create_mysql_client()


            async with  db_meta_client_manager.session_factory() as meta_session ,db_dw_client_manager.session_factory() as dw_session:

                context= DataAgentContext(
                    column_qdrant_repository = ColumnQdrantRepository(qdrant_client),
                    embedding_client = embedding_client,
                    metric_qdrant_repository = MetricQdrantRepository(qdrant_client),
                    value_es_repository = ValueEsRepository(es_client),
                    meta_mysql_repository = MetaMysqlRepository(meta_session),
                    dw_mysql_repository = DwMysqlRepository(dw_session)
                )

                #config = {"context": context}
    
                async  for chunk in graph.astream(input=state,context=context,stream_mode='custom'):
                    print(chunk)

                #关闭qdrant客户端
                await qdrant_client_manager.close()

                #关闭es客户端
                await es_client_manager.close()


                #关闭mysql客户端
                await db_meta_client_manager.close()
                await db_dw_client_manager.close()


        asyncio.run(test())


