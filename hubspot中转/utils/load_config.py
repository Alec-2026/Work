import configparser
import traceback
from pathlib import Path


def get_config():
    try:
        config = configparser.ConfigParser()
        config_file_path = Path(__file__).parent.parent / 'conf.ini'
        config.read(config_file_path)
        return config
    except Exception as e:
        traceback.print_exc()
        raise Exception('')


if __name__ == '__main__':
    config = get_config()
    print(config['hubspot']['access_token'])