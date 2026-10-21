import traceback
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging

logger = logging.getLogger(__name__)


def cut_params(params):
    if 'propertiesWithHistory' in params.keys():
        params.pop('propertiesWithHistory')
    else:
        pass
    return params


def gen_email(params, max_workers=50):
    """
    批量生成email
    Args:
        params: [{}, {}, ...]
        max_workers:  [{}, {}, ...]

    Returns:

    """
    gen_email_interface = 'http://10.1.21.56:5022/gen_email'
    # gen_email_interface = 'http://localhost:5022/gen_email'
    headers = {"Content-Type": "application/json"}

    def process_single(x):
        try:
            response = requests.post(gen_email_interface, headers=headers, data=json.dumps(x)).json()

            if response.get('code', 0) == 1:
                res = {
                    'id': x['id'],
                    'email_send': 'Ready',
                    'email_subject': response['model_response'].get('email_subject', None),
                    'email_body': response['model_response'].get('email_body', None)
                }
                logger.info(f'邮件生成完成: {x["id"]}')
                return res
            else:
                logger.warning(f'邮件生成失败: 用户id: {x["id"]}; 失败原因: {response["info"]}')
                return {
                    'id': x['id'],
                    'email_send': 'Pending',
                    'email_subject': '',
                    'email_body': ''
                }

        except Exception as e:
            logger.error(traceback.format_exc(e))
            return {
                'id': x['id'],
                'email_send': 'Pending',
                'email_subject': '',
                'email_body': ''
            }

    res = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single, cut_params(x)) for x in params]
        for future in as_completed(futures):
            res.append(future.result())

    return res

if __name__ == '__main__':
    import json
    fp = '/Users/yangchengcheng/Documents/workspace/api_online/独立站相关/hubspot中转/data/contact_1.json'
    # 打开并读取json文件
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)  # 传入文件对象，返回dict/list
        print(data)
    res = gen_email([data])
    print(res)