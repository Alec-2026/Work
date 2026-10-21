import os
import configparser
import traceback


def get_config():
    try:
        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), 'conf.ini')
        config.read(config_file_path)
        return config
    except Exception as e:
        traceback.print_exc()
        return {}


def read_sql(file_name):
    """
    读取当前目录下的 sql 文件
    :param file_name: sql 文件名
    :return: sql 模版内容
    """
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_content = file.read().strip()
    return sql_content


def fill_sql_content(sql_content, sql_params: dict):
    """
    将参数合并到 sql 模版中，占位符格式为 {{param}}
    :param sql_content: sql 模版内容
    :param sql_params: 参数字典
    :return: 填充后的 sql
    """
    for k, v in sql_params.items():
        k_format = f'{{{{{k}}}}}'
        sql_content = sql_content.replace(k_format, str(v))

    return sql_content
