import requests
import json
import time
import base64

headers = {"Content-Type": "application/json"}
start = time.time()

url = f'http://localhost:5009/hubspot'


# 单条请求
data = {}

response = requests.post(url, headers=headers, data=json.dumps(data))
response_json = response.json()

print(json.dumps(response_json, indent=4, ensure_ascii=False))
print('总花费时长: ', int(time.time()-start), 's')
