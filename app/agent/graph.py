from langgraph.constants import START
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
graph_build.add_edge(START,'extract_keywords')
graph_build.add_edge('extract_keywords','recall_column')
graph_build.add_edge('extract_keywords','recall_metric')
graph_build.add_edge('extract_keywords','recall_column_values')
graph_build.add_edge('recall_column','merge_retrieved_info')
graph_build.add_edge('recall_metric','merge_retrieved_info')
graph_build.add_edge('recall_column_values','merge_retrieved_info')
graph_build.add_edge('merge_retrieved_info','filter_metric')
graph_build.add_edge('merge_retrieved_info','filter_table')
graph_build.add_edge('filter_metric','add_extra_context')
graph_build.add_edge('filter_table','add_extra_context')
graph_build.add_edge('add_extra_context','generate_sql')
graph_build.add_edge('generate_sql','validate_sql')
graph_build.add_conditional_edges(
    source='validate_sql',
    path=lambda state :"run_sql" if state['error'] is None else "correct_sql",
    path_map = {'run_sql':'run_sql','correct_sql':'correct_sql'}
    )
graph_build.add_edge('correct_sql','run_sql')
graph_build.add_edge('run_sql',END)

graph = graph_build.compile()
#print(graph.get_graph().draw_ascii())

if __name__ == '__main__':
    
    resp = graph.astream()


