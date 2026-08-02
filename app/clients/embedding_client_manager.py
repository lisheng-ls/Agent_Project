import asyncio
from typing import Optional

import httpx
from langchain_openai import OpenAIEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config



"""
embedding 客户端
"""
class EmbeddingClientManager:
    def __init__(self,embedding_config : EmbeddingConfig):
        self.client: Optional[OpenAIEmbeddings] | None = None
        self.embedding_config = embedding_config

    def _get_url(self):
        host = self.embedding_config.host
        port = self.embedding_config.port
        return f'http://{host}:{port}'


    def create_client(self):

        self.client = OpenAIEmbeddings(
            model=self.embedding_config.model,
            api_key='unused',
            base_url=self._get_url(),
            check_embedding_ctx_length=False,
            # 异步专用 AsyncClient（可选，控制超时）
            http_async_client = httpx.AsyncClient(timeout=120.0)
        )


embedding_config = app_config.embedding
embedding_client_manager = EmbeddingClientManager(embedding_config)

if __name__ == '__main__':
    #创建客户端
    embedding_client_manager.create_client()
    client = embedding_client_manager.client
    """
    同步操作
    """

    # #单条数据转换为向量
    # text = "What is deep learning?"
    # query_result = client.embed_query(text)
    # print(f'单条数据转换为向量结果：{query_result}')
    #
    # #多条数据转换为向量
    # texts=["What is deep learning?","What is  learning?"]
    # document_result = client.embed_documents(texts)
    # print(f'多条数据转换为向量结果：{document_result}')

    """
    异步操作
    """
    async def test():
        atext = "What is deep learning?"
        aquery_result = await client.aembed_query(atext)
        print(f'单条数据转换为向量结果：{aquery_result}')
        # 多条数据转换为向量
        atexts = ["What is deep learning?", "What is  learning?"]
        adocument_result = await client.aembed_documents(atexts)
        print(f'多条数据转换为向量结果：{adocument_result}')

    asyncio.run(test())