import requests

url = "http://127.0.0.1:8000/api/query"

resp = requests.request(url=url, method="post",json={'query':'统计华北地区的销售总额'}).json()

print(resp)