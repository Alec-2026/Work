from openai import OpenAI

# sglang
base_url = 'http://117.148.167.73:30000/v1'
model = 'qwen3-235b-a22b-instruct-2507'
key = 'sk-t0-sZriYk1rRSx2-ZcXIwS7KaXPw8lfMOKjB8IZxp3YGQNrDRs5oBwfU4MqGPcFR'


messages = [{"role": "user", "content": "你好，输出一段话, 包含中文、数字、英文，100个字左右"}]

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