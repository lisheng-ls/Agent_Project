#es
from app.clients.ec_client_manager import es_client_manager


#es客户端
client = es_client_manager.creat_es_client()




#添加索引
"""
index 索引名称,
body='' 索引内容
"""
index_name = 'index_001'

index_body = {
    #分片、副本、分词、刷新规则
    'setting':{

    },
    'mapping':{
        
    }

}



add_result = client.indices.create(index= '',body=''  )


#添加数据
"""
index  索引名称,
document   数据内容
"""
client.index(index='',document='')


#查询数据
"""
index 索引名称,
query  查询条件
"""
client.search(index='',query='')