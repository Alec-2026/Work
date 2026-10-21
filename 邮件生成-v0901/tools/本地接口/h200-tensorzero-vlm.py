from openai import OpenAI
import requests
import base64

# tensorzero
# base_url = 'http://117.148.167.73:3000/openai/v1'
base_url = 'http://10.1.21.45:8000/openai/v1'
model = 'tensorzero::model_name::default-vlm-no-think'
key = 'sk-49e1db70ecdd40bd8b628d51b9b13f75'


image_url = 'https://diy.racetopprint.com/img/zlgupload/20250910/6b62942828954467b5cc7beb2c80914a.png!0x300'
user_content = '描述这张图'

response = requests.get(image_url)
from PIL import Image
from io import BytesIO

# 打开图像并检查是否存在透明通道（RGBA 或 LA）
img = Image.open(BytesIO(response.content))
if img.mode in ('RGBA', 'LA', 'PA'):
    # 创建白色背景
    background = Image.new('RGB', img.size, (255, 255, 255))
    # 将图像粘贴到白色背景上
    if img.mode == 'RGBA':
        background.paste(img, mask=img.split()[-1])  # 使用 alpha 通道作为掩码
    elif img.mode == 'LA':
        background.paste(img.convert('RGB'), mask=img.split()[-1])
    elif img.mode == 'PA':
        img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1])
    img = background
else:
    img = img.convert('RGB')  # 确保为 RGB 模式

# 将处理后的图像转为 base64
buffer = BytesIO()
img.save(buffer, format='PNG')
image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
messages = [
    {
        'role': 'user',
        'content': [
            {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{image_base64}'}},
            {'type': 'text', 'text': user_content}
        ]
    }
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