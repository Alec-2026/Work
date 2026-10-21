import requests
import json
import logging
logger = logging.getLogger()


def get_llm_configuration(resource_name):
    """
    请求模型配置接口获取配置信息

    Args:
        resource_type (str): 资源类型，如'llm'
        resource_name (str): 资源名称，如'llm-text'

    Returns:
        dict: 接口返回的配置信息
    """
    # 接口URL
    url = "http://10.1.21.20:5021/get_llm_conf"
    # url = "http://localhost:5021/get_llm_conf"

    # 构造请求参数
    payload = {
        "resource_name": resource_name
    }

    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 发送POST请求
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        # 检查响应状态
        response.raise_for_status()
        logger.info(f'{resource_name}模型配置信息获取成功')
        # 返回JSON格式的响应数据
        return response.json()

    except requests.exceptions.RequestException as e:
        # 处理请求异常
        logger.info(f'{resource_name}模型配置信息获取失败, {e}')
        return None
    except json.JSONDecodeError as e:
        # 处理JSON解析错误
        logger.info(f'{resource_name}模型配置信息获取失败, {e}')
        return None


# 使用示例
if __name__ == "__main__":
    # 调用函数获取配置
    result = get_llm_configuration("llm-text")
    if result:
        print("获取到的配置信息:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("获取配置失败")
