"""
抽取关键字
"""
import jieba.analyse
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def extract_keywords(state: DataAgentState,runtime: Runtime[DataAgentContext] ):
    writer = runtime.stream_writer
    writer({"type": "progress","step": "抽取关键字","status": "running"})

    try:
        query  = state['query']

        # 对查询进行分词，只提取指定词性的词
        allow_pos = (
            "n",  # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",  # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",  # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng",  # 英文
            "i",  # 成语
            "l",  # 常用固定短语
        )

        #基于 TF-IDF 算法的关键词抽取
        """
        sentence 为待提取的文本
        topK 为返回几个 TF/IDF 权重最大的关键词，默认值为 20
        withWeight 为是否一并返回关键词权重值，默认值为 False
        allowPOS 仅包括指定词性的词，默认值为空，即不筛选   
        """

        keywords = jieba.analyse.extract_tags(sentence=query, allowPOS=allow_pos)

        #将原本输入的查询加入keywords中

        keywords = list(set(keywords+[query]))  #防止query与的得到的分词列表中的某个一样
        logger.info(f'抽取的关键字列表：{keywords}')

        writer({"type": "progress","step": "抽取关键字","status": "success"})
        return {'keywords': keywords}
    except Exception as e:
        logger.error(f'抽取关键字失败：{e}')

        writer({"type": "progress","step": "抽取关键字","status": "error"})
        writer({"type": "error","message": str(e)})
        raise 