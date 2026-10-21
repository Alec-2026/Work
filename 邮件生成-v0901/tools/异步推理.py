import asyncio
from openai import AsyncOpenAI

# 1. 配置异步 OpenAI 客户端，指向 SGLang 本地服务
client = AsyncOpenAI(
    api_key="dummy_key",  # SGLang 兼容服务无需真实 OpenAI API Key，填任意非空值即可
    base_url="http://117.148.167.73:3000/openai/v1"  # 指向 SGLang 的 OpenAI 兼容接口（必须带 /v1 后缀）
)

# 2. 准备批量请求（列表格式，每个元素对应一个独立推理请求）
batch_messages = [
    # 第 1 个请求
    [{"role": "user", "content": "总结大模型 batch 推理的核心优势"}],
    # 第 2 个请求
    [{"role": "user", "content": "如何平衡大模型推理的吞吐量和延迟"}],
    # 第 3 个请求
    [{"role": "user", "content": "SGLang 实现 batch 推理的核心优化技术是什么"}]
]


# 3. 定义异步推理函数
async def async_inference(messages, index):
    """异步调用单个推理请求"""
    response = await client.chat.completions.create(
        model="tensorzero::model_name::qwen3-235b-a22b-instruct-2507",  # 模型名需与 SGLang 启动时的模型一致
        messages=messages,  # 单个请求的消息列表
        max_tokens=200,  # 每个请求的最大生成长度
        temperature=0.7
    )
    return index, response


# 4. Batch 推理主函数（并发执行所有请求）
async def batch_inference():
    """并发执行所有推理请求"""
    # 创建所有异步任务
    tasks = [async_inference(messages, idx) for idx, messages in enumerate(batch_messages)]

    # 并发执行所有任务
    results = await asyncio.gather(*tasks)

    # 按原始顺序排序结果
    results.sort(key=lambda x: x[0])

    return results


# 5. 执行 Batch 推理并解析结果
if __name__ == "__main__":
    # 运行异步批量推理
    results = asyncio.run(batch_inference())

    # 解析批量返回结果
    print("===== Batch 推理结果 =====")
    for idx, response in results:
        print(f"\n--- 请求 {idx + 1} 结果 ---")
        print(response.choices[0].message.content)
