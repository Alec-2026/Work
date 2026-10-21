import json
import pandas as pd
from json_repair import repair_json


def parse_str_json(response: str, name: str):
    """
    :param response: 模型回复的json，字符串格式
    :param name: 需要获取的key，支持多级key，用'/'分隔
    :return:
    """
    try:
        response_json = json.loads(repair_json(response))
        names = name.split('/')
        if len(names) == 1: return response_json.get(name, None)
        if len(names) == 2: return response_json[names[0]][names[1]]
        if len(names) == 3: return response_json[names[0]][names[1]][names[2]]
        if len(names) == 4: return response_json[names[0]][names[1]][names[2]][names[3]]
        if len(names) == 5: return response_json[names[0]][names[1]][names[2]][names[3]][names[4]]
        return None
    except Exception as e:
        return None