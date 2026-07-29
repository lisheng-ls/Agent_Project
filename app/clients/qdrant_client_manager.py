"""
创建qdrant客户端
"""
import asyncio
from typing import Optional

from qdrant_client import  AsyncQdrantClient
from app.conf.app_config import QdrantConfig, app_config
from qdrant_client.models import PointStruct
from qdrant_client.models import Distance, VectorParams


class QdrantClientManager:
    def __init__(self,config:QdrantConfig ): #
        self.config = config
        self.client : Optional[AsyncQdrantClient] = None

    def qdrant_url(self):
        return  f'http://{self.config.host}:{self.config.port}'


    def create_client(self):
        self.client = AsyncQdrantClient(url=self.qdrant_url(),check_compatibility=False)
        return self.client

    @property
    def init_client(self) -> AsyncQdrantClient:
        """获取客户端，未创建则自动初始化"""
        if self.client is None:
            self.create_client()
        return self.init_client

    async def close(self):
        """关闭连接释放资源"""
        if self.client is not None:
            await self.client.close()


config = app_config.qdrant
qdrant_client_manager = QdrantClientManager(config)


if __name__ == '__main__':

    #创建客户端
    qdrant_client_manager.create_client()
    client = qdrant_client_manager.client

    async def test():
        #创建集合
        if not await client.collection_exists('my_collection'):
            await   client.create_collection(
                collection_name='my_collection',
                vectors_config= VectorParams(size=10, distance=Distance.COSINE),
            )
        #添加向量
        await client.upsert(
            collection_name="my_collection",
            wait=True,
            points=[
                PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
                PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
                PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
                PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
                PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
                PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
            ],
        )


        #查询数据

        search_result = await client.query_points(
            collection_name="my_collection",
            query=[0.2, 0.1, 0.9, 0.7],
            with_payload=False,
            limit=3
        )
        rest= search_result.points
        print(f'查询结果为{rest}')

    asyncio.run(test())

