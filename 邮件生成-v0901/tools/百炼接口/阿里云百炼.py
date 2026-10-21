from openai import OpenAI

# sglang
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
model = 'kimi-k2.6'
key = 'sk-49e1db70ecdd40bd8b628d51b9b13f75'


messages = [{"role": "user", "content": "请联网搜索，今天是几号"}]

client = OpenAI(
    base_url=base_url,
    api_key=key
)

response = client.chat.completions.create(
    model=model,
    temperature=0.7,
    top_p=0.8,
    messages=messages,
    timeout=100,
)

print('response:')
print(response.choices[0].message.content)