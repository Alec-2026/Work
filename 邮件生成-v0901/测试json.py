import json
from pathlib import Path

json_fp = Path(__file__).with_name('测试.json')

# 读取JSON文件
with open(json_fp, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 打印基本信息
# print(f"总共有 {len(data)} 条联系人数据")
# print("\n" + "="*50)

aa = data[1]

# print(aa)