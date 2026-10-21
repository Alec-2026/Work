from utils.operate_database import OpDataBase
import logging
import time
import os

logger = logging.getLogger()


def upload_single_prompt(business_name, prompt_fp='prompt/prompt.txt'):
    """
    将prompt上传到ck
    """
    with open(prompt_fp, 'r', encoding='utf-8') as file:
        current_prompt = file.read()

    odb = OpDataBase()
    last_prompt = odb.get_last_prompt(business_name)
    if last_prompt != current_prompt:
        version = time.time()
        odb.upload_prompt(business_name, current_prompt, version)
        logger.info(f'{business_name}的prompt更新成功')
    else:
        logger.info(f'{business_name}的prompt已经是最新版, 无需更新')


def upload_prompt(business_name='模版测试'):
    fp = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'apps'
    )
    for x in os.listdir(fp):
        abs_path = os.path.join(fp, x)
        if os.path.isdir(abs_path) and x not in ['__pycache__']:
            prompt_dir = os.path.join(abs_path, 'prompt')
            for y in os.listdir(prompt_dir):
                if 'txt' in y:
                    upload_single_prompt(
                        business_name=business_name + '-' + y.replace('.txt', ''),
                        prompt_fp=os.path.join(prompt_dir, y)
                    )

if __name__ == '__main__':
    pass