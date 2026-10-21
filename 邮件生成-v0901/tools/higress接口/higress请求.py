from openai import OpenAI

# sglang
base_url = 'http://10.1.21.49:8082/v1'
model = 'tensorzero::model_name::default-llm-no-think'
key = 'sk-49e1db70ecdd40bd8b628d51b9b13f75'


messages = [{"role": "user", "content": "请联网搜索，今天是几号"}]

client = OpenAI(
    base_url=base_url,
    api_key=key
)

response = client.chat.completions.create(
    model=model,
    temperature=0.6,
    top_p=0.8,
    max_tokens=2048,
    messages=messages,
    timeout=100,
    extra_body={"chat_template_kwargs": {"thinking": False}},
)

print('response:')
print(response.choices[0].message.content)