import requests
import time

headers = {"Content-Type": "application/json"}
start = time.time()

url = f'http://10.1.21.56:5022/gen_email'
#url = f'http://localhost:5022/gen_email'
import json

# 单条请求
from 测试json import aa

data = aa
print(data['properties']['last_behavioral_email_type'])
print(data['properties']['n1v1_email_round'])
print(data['properties']['firstname'])
print(data['properties']['last_viewed_product_name'])
print(data['properties']['industry_level_2'])
print(data['properties']['dedicated_account_manager_label_for_ai_email'])
print(data['properties']['first_order_offer_message'])

response = requests.post(url, headers=headers, data=json.dumps(data))
response_json = response.json()

print(json.dumps(response_json, indent=4, ensure_ascii=False))
print('总花费时长: ', int(time.time()-start), 's')
