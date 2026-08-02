from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

from app.conf.app_config import app_config
from app.entities.metric_info import MetricInfo


class MetricQdrantRepository:

    collection_name = 'metric_info_collection'

    def __init__(self,client:AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=app_config.qdrant.embedding_size, distance=Distance.COSINE)
            )

    async def upsert(self, metric_embeddings:list[list[float]],metric_ids : list[str], metric_payloads:list[dict],batch_size:int=20):
        points:list[PointStruct] = [
            PointStruct(id = metric_id ,
                        vector=metric_embedding,
                        payload=metric_payload)
            for  metric_id ,metric_embedding,metric_payload in zip(metric_ids,metric_embeddings, metric_payloads)]

        #防止points过大，通过batch_size分批次添加向量
        for i in range(0,len(points),batch_size):
            batch_points = points[i:i+batch_size]
            await  self.client.upsert(
                collection_name=self.collection_name,
                points=batch_points
            )

    async def search(self, embedding:list[float],score_threshold:float = 0.6,limit:int=10) ->list[MetricInfo]:
        result = await  self.client.query_points(
            collection_name=self.collection_name,
            query = embedding,
            limit=limit,
            score_threshold = score_threshold
        )
        return [MetricInfo(**point.payload) for point in result.points]
