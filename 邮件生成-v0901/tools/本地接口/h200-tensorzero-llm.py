from openai import OpenAI

# sglang
base_url = 'http://117.148.167.73:3000/openai/v1'
model = 'tensorzero::model_name::default-llm-no-think'
key = 'sk-t0-sZriYk1rRSx2-ZcXIwS7KaXPw8lfMOKjB8IZxp3YGQNrDRs5oBwfU4MqGPcFR'



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
    extra_body={
        "rabbitmq_priority": 10  # 你的自定义参数
    }
)

print('response:')
print(response.choices[0].message.content)