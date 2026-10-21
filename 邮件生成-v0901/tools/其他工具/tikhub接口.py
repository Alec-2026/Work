import http.client
import json
"""
tips:
tikhub的linkedin区分个人接口和公司接口
- 个人接口: get_user_profile
- 公司接口: get_company_profile

"""
conn = http.client.HTTPSConnection("api.tikhub.dev")
payload = ''
headers = {
   'Authorization': 'Bearer t6seLp4g3HetukK4HoiRmTPnExaff7tHw0XArE+/E8CWs0+OJkyYSQ7FaA=='
}
# url = 'https://www.linkedin.com/company/hut8corp'
url = 'https://www.linkedin.com/in/yaritza-arriaga-16102825a/'
conn.request("GET", f"/api/v1/linkedin/web_v2/get_user_profile?url={url}", payload, headers)
res = conn.getresponse()
data = res.read()
res = data.decode("utf-8")
print(json.dumps(json.loads(res), indent=4, ensure_ascii=False))
