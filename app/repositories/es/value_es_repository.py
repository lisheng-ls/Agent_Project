from dataclasses import asdict

from elasticsearch import AsyncElasticsearch

from app.entities.value_info import ValueInfo


class ValueEsRepository:

    index_name = 'index_value'

    index_mapping  =  {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "column_id": {"type": "keyword"}
        }
    }

    def __init__(self,es_client:AsyncElasticsearch):
        self.es_client:AsyncElasticsearch = es_client

    async def ensure_index(self):
        if not await self.es_client.indices.exists(index=self.index_name):
            await self.es_client.indices.create(
                index=self.index_name,
                mappings=self.index_mapping
            )

    async def index(self,column_value_infos:list[ValueInfo],batch_size= 20):
        #防止column_value_info值过大，通过batch_size批次添加
        
        for i in range(0,len(column_value_infos),batch_size):
            value_infos = column_value_infos[i:i+batch_size]
            batch_operation = []
            for column_value_info in column_value_infos:
                batch_operation.append(
                    {
                        "index": {
                            "_index": self.index_name
                        }
                    }
                )
                batch_operation.append(asdict(column_value_info))
            await self.es_client.bulk(operations=batch_operation)

    async def search(self, keyword:str,score_threshold:float = 0.3 ,limit :int = 100):

        query = {
            "match": {
                "value": keyword,
            }
        }

        all_results = await self.es_client.search(
            index=self.index_name,
            query = query,
            min_score = score_threshold,
            size = limit)

        all_results = all_results['hits']['hits']
        all_results = [ result['_source'] for result in all_results]

        #print( f"单词查询结果：{[ValueInfo(**result) for result in all_results]}")

        return [ValueInfo(**result) for result in all_results]
