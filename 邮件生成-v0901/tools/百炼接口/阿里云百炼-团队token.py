from openai import OpenAI

# sglang
base_url = 'https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1'
model = 'qwen3.7-max'
key = 'sk-sp-D.LDLMX.0dY1.MEQCIA0iKYgDLFrUMQN7dnL3voPryMII1ZHnyiikCqrIQrXlAiAzRLDsnAvTITfey4RcaHs4OBAJl4OsdBsZKb8Quhc8Nw=='


messages = [{"role": "user", "content": "wakeup"}]

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
print(response.usage)
print(response.choices[0].message.content)