from openai import OpenAI

# sglang
base_url = 'http://112.20.69.137:40000/openai/v1'
model = 'tensorzero::model_name::default-llm-no-think'
key = 'sk-t0-DHuVw8Ss6mMb-ZjhJzB3syOp3e9mr8AdaaX0iud4jKuIiFHP4EvGLSceDqt8q'


messages = [
    {"role": "user", "content": "请联网搜索，今天是几号"}
]

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