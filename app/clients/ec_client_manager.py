import asyncio

from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import EsConfig, app_config


class EsClientManager:
    def __init__(self,es_config:EsConfig):
        self.es = es_config
        self.client :Optional[AsyncElasticsearch] = None


    def es_url(self):
        return f'http://{self.es.host}:{self.es.port}'

    def creat_es_client(self):
        #@print(self.es_url())
        self.client = AsyncElasticsearch(
            hosts = [self.es_url()],
            verify_certs = False,
            ssl_show_warn = False,
            request_timeout = 30,  # 延长请求超时，避免慢初始化被切断
            connections_per_node = 5  # 限制连接池，防止连接堆积被ES清理
        )
        return self.client

    async def es_close(self):
        await self.client.close()


es_config = app_config.es
es_client_manager = EsClientManager(es_config)

if __name__ == '__main__':
    #初始化es客户端
    client = es_client_manager.creat_es_client()

    """
    创建索引、插入数据、查询数据
    """
    index_name = "student4"

    # 索引配置
    index_body = {
        "settings": {
            "number_of_shards": 1,    # 主分片
            "number_of_replicas": 0   # 副本，单机设0
        },
        "mappings": {
            "properties": {
                "stu_id": {"type": "keyword"},
                "name": {"type": "text"},
                "age": {"type": "integer"},
                "score": {"type": "float"},
                "create_time": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"}
            }
        }
    }
    async def test():
        #添加索引
        await client.indices.create(index=index_name,body=index_body)
        print('索引添加成功')
        #添加数据
        doc = {
            "stu_id": "S001",
            "name": "张三",
            "age": 18,
            "score": 92.5,
            "create_time": "2026-07-11 10:20:00"
        }
        resp = await client.index(index=index_name,document=doc)
        print("单条插入结果：", resp)

        #查询数据
        all_res =await client.search(index=index_name, query={"match_all": {}})
        print(all_res)

        #删除索引
        await client.indices.delete(index = ['student2','student','student1','student3','student4'])
        print('索引删除成功')

        #关闭客户端
        await es_client_manager.es_close()

    asyncio.run(test())
