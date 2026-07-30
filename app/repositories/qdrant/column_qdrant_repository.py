from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance, VectorParams

from app.conf.app_config import app_config


class ColumnQdrantRepository:

    collection_name : str = 'column_info_collection'

    def __init__(self,client:AsyncQdrantClient):
        self.client = client


    #创建集合
    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await  self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=app_config.qdrant.embedding_size, distance=Distance.COSINE)
            )


    #
    async def upsert(self, column_embeddings:list[list[float]], ids:list[str] , payloads:list[dict],batch_size:int=20) -> None:

        #zip返回迭代器
        points:list[PointStruct]=[PointStruct(id=id,vector=column_embedding,payload=payload)for id,column_embedding,payload in zip(ids,column_embeddings,payloads)]

        #
        # points:list[PointStruct] = []
        # for i in range(0,min(len(embeddings),len(ids),len(payloads))):
        #     id = ids[i]
        #     embedding =embeddings[i]
        #     payload = payloads[i]
        #     pointStruct = PointStruct(id=id, vector=embedding,payload=payload)
        #     points.append(pointStruct)


        #防止points数据过大，通过batch_size控制写入的大小
        for i in range(0,len(points),batch_size):
            batch_points = points[i:i+batch_size]
            await self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=batch_points
            )
