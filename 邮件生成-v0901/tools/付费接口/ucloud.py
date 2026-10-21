
import requests

prompt = '你是谁'

response = requests.post(
    "https://api.modelverse.cn/v1/responses",
    headers={
        "Authorization": "Bearer 8OR5wqEhMiRGafYgA6Dd7f16-03b7-468e-901F-4b342589",
        "Content-Type": "application/json",
    },
    json={
        "model": "kimi-k2.6",
        "input": prompt,
    },
)

print(response.json())