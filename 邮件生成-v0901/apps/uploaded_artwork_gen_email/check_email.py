import traceback
from json_repair import repair_json
import json
import time
from utils.chat_with_llm import LLM
from openai import BadRequestError
import logging
import os
from utils.load_config import get_yaml

logger = logging.getLogger()


class AutoTag(object):
    def __init__(self):
        self.prompt_name = '独立站-邮件审核.md'
        self.prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompt')
        self.prompt_fp = os.path.join(self.prompt_dir, self.prompt_name)
        self.business_name = self.prompt_name.split('.')[0]

        self.model_name = 'llm-text'
        self.llm = LLM(self.model_name)

        self.labels = get_yaml()


    def check_model_response(self, response_json):
        if isinstance(response_json, dict):
            pass
        else:
            return False

        keys = ['质检项目']
        for x in keys:
            if x not in response_json.keys():
                return False

        return True


    def format_to_json(self, llm_response):
        response_origin = llm_response.choices[0].message.content

        # 直接获取json
        response_json = json.loads(repair_json(response_origin))

        if isinstance(response_json, dict):
            pass
        else:
            logger.error(f'json解析失败, 模型原始输出: {response_origin}')
            raise ValueError(f'json解析失败, 模型原始输出: {response_origin}')

        return response_json


    def llm_request(self, messages, max_retries=5, delay=1):
        """请求模型，失败时重试，最多重试 max_retries 次"""
        response_json = None
        for attempt in range(max_retries):
            try:
                response = self.llm.call_model(messages, self.business_name)
                response_json = self.format_to_json(response)
                if self.check_model_response(response_json):
                    logger.info('llm 请求成功')
                    return response_json
                else:
                    logger.warning(f"校验失败，尝试 {attempt + 1}/{max_retries} 次")
                    time.sleep(delay)
            except BadRequestError as e:
                logger.error(traceback.format_exc())
                if (e.body['message'] == 'Output data may contain inappropriate content.'
                        or e.body['message'] == 'Input data may contain inappropriate content.'):
                    raise Exception('模型请求失败, 请求包含非法内容')
                else:
                    logger.warning(f"请求失败，尝试 {attempt + 1}/{max_retries} 次, 失败原因: {repr(e)}")
                    if attempt + 1 == max_retries:
                        raise Exception(f'模型请求失败, 失败原因: {repr(e)}')
                    time.sleep(delay)
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.warning(f"请求失败，尝试 {attempt + 1}/{max_retries} 次, 失败原因: {repr(e)}")
                if attempt+1 == max_retries:
                    raise Exception(f'模型请求失败, 失败原因: {repr(e)}')
                time.sleep(delay)

        return response_json

    def fill_prompt(self, row):
        params = row
        prompt = self.llm.get_prompt(self.prompt_fp)
        # 参数填充: 示例, params['用户行业'] = params['业务'].split('-')[0]

        prompt = prompt.compile(**params)
        return prompt

    def fix_response(self, response):
        # 修改字段名称
        return response

    def auto_tag(self, row):
        start_time = time.time()
        try:
            prompt = self.fill_prompt(row)
            # print(prompt)
            messages = self.llm.get_message(
                row, prompt, chat_type='text', image_type='url'
            )  # 如果type是image，则row中必须有url这个参数,image_type: url/path, chat_type:image/text
            llm_response = self.llm_request(messages)
            llm_response_fix = self.fix_response(llm_response)

            result = {
                'code': 1, 'model_response': llm_response_fix, 'info': 'success',
                'remote_addr': row.get('remote_addr', None), 'request_model': self.llm.model_name,
                'input_token': self.llm.all_input_tokens, 'output_token': self.llm.all_output_tokens,
                'cost': self.llm.all_cost, 'use_time': time.time()-start_time, 'business': self.business_name
            }
            logger.info(f'推理完成: \nresponse:\n{llm_response_fix}')
        except Exception as e:
            logger.error(traceback.format_exc())
            result = {
                'code': 0, 'model_response': None, 'info': repr(e),
                'remote_addr': row.get('remote_addr', None), 'request_model': self.llm.model_name,
                'input_token': self.llm.all_input_tokens, 'output_token': self.llm.all_output_tokens,
                'cost': self.llm.all_cost, 'use_time': time.time() - start_time, 'business': self.business_name
            }

        return result



if __name__ == '__main__':
    """
    文本调用示例：
    self.prompt_name = 'prompt-text.txt'
    self.model_name = 'llm-text'
    self.llm.get_message(row, prompt, chat_type='text', image_type='url')
    """
    params = {
        "email_subject": "",
        "email_body": "Hello,\n\xa0\nI wanted to follow up once more about your plans for luxury gift box bags.\n\xa0\nChoosing the right material, size, quantity, or artwork setup is usually easier when the intended use is clear, even if the specifications are not final.\n\xa0\nCould you share the intended use or an approximate quantity? That information will help me recommend options suited to your project.\n\xa0\nIf the project is no longer active, no action is needed. We'll be here whenever support would be useful.\n\xa0\nBest regards,\nMegan H\nCustomer Success Manager",
        'first_name': 'Isa',
        'last_name': 'Fernandez',
        'product_name': 'Custom Foil Stamped Gift Bags',
        'sender_name': 'Megan H'
    }
    start = time.time()
    print('request: ', params)
    print()
    response = AutoTag().auto_tag(params)
    print('response: ', response)
    print()
    print('model response: ', json.dumps(response['model_response'], ensure_ascii=False, indent=4))
    print(f'消耗时间: {time.time()-start}')


    """
    excel指定行数示例
    """
    # import pandas as pd
    # fp = '/Users/yangchengcheng/Documents/workspace/customer_aware_interface_template/通用工程模版/apps/tag_name/data/示例数据.xlsx'
    # row = pd.read_excel(fp).iloc[0].to_dict()
    # params = {
    #     'name': row['name']
    # }
    # start = time.time()
    # print('request: ', params)
    # print()
    # response = AutoTag().auto_tag(params)
    # print('response: ', response)
    # print()
    # print('model response: ', json.dumps(response['model_response'], ensure_ascii=False, indent=4))
    # print(f'消耗时间: {time.time()-start}')

    """
    图像调用示例，参数：
    1. self.prompt_name = 'prompt-vl.txt'
    2. self.model_name = 'llm-vl'
    3. self.llm.get_message(row, prompt, chat_type='url', image_type='path')
    ** 注意 ** : params中必须有url参数
    """
    # import pandas as pd
    # # row = pd.read_excel('data/全切跑稿件-image-address.xlsx').iloc[0].to_dict()
    # # params = {
    # #     'url': [row['图片地址']],
    # # }
    # params = {
    #     'url': ['/Users/yangchengcheng/Documents/workspace/api_online/临时项目/不干胶全切稿件打标/data/全切跑稿件/image001.png']
    # }
    # start = time.time()
    # print('request: ', params)
    # print()
    # response = AutoTag().auto_tag(params)
    # print('response: ', response)
    # print()
    # print('model response: ', json.dumps(response['model_response'], ensure_ascii=False, indent=4))
    # print(f'消耗时间: {time.time()-start}')
