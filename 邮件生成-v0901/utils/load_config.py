import configparser
import traceback

import yaml
import os
from pathlib import Path


def get_yaml() -> dict:
    """安全读取 YAML 文件并返回字典"""
    file_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)  # 使用 safe_load 避免代码注入风险[2,4,11](@ref)
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML 文件未找到: {file_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 解析错误: {e}")


def get_config():
    try:
        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'conf.ini')
        config.read(config_file_path)
        return config
    except Exception as e:
        traceback.print_exc()
        raise Exception('')


if __name__ == '__main__':
    config = get_yaml()
    print(config['一级行业'])