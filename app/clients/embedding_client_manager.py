import asyncio
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

from app.conf.app_config import EmbeddingConfig, load_app_config

"""

embedding 客户端
"""
class EmbeddingClientManager:
    def __init__(self,embedding_config : EmbeddingConfig):
        self.client: HuggingFaceEndpointEmbeddings | None = None
        self.embedding_config = embedding_config

    def _get_url(self):
        host = self.embedding_config.host
        port = self.embedding_config.port
        print(f'http://{host}:{port}')
        return f'http://{host}:{port}'


    def create_embedding_client(self):
        self.client = HuggingFaceEndpointEmbeddings(
            model = self.embedding_config.model,
        )
        return self.client


embedding_config = load_app_config().embedding
embedding_client_manager = EmbeddingClientManager(embedding_config)

if __name__ == '__main__':
    #创建客户端
    embedding_client_manager.create_embedding_client()
    client = embedding_client_manager.client
    """
    同步操作
    """

    #单条数据转换为向量
    text = "What is deep learning?"
    query_result = client.embed_query(text)
    print(f'单条数据转换为向量结果：{query_result}')

    #多条数据转换为向量
    texts=["What is deep learning?","What is  learning?"]
    document_result = client.embed_documents(texts)
    print(f'多条数据转换为向量结果：{document_result}')

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