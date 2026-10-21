import os
from openai import OpenAI

client = OpenAI(
    api_key='tp-cqglg9i0ljx2afab9nco1oe41fjgl1czef8h50vjj3v9n9zh',
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)

completion = client.chat.completions.create(
    model="mimo-v2.5",
    messages=[
        {
            "role": "system",
            "content": "You are MiMo, an AI assistant developed by Xiaomi. Today is date: Tuesday, December 16, 2025. Your knowledge cutoff date is December 2024."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example-files.cnbj1.mi-fds.com/example-files/image/image_example.png"
                    }
                },
                {
                    "type": "text",
                    "text": "please describe the content of the image"
                }
            ]
        }
    ],
    max_completion_tokens=1024
)

print(completion.model_dump_json())