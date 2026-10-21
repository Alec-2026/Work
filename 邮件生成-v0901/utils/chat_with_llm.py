import os
import configparser
from openai import OpenAI
import traceback

from utils.image_process import encode_image_from_url
from utils.get_llm_conf import get_llm_configuration
from utils.load_config import get_config
from utils.image_process import image_compression


class LocalPrompt(object):
    def __init__(self, prompt_fp):
        with open(prompt_fp, 'r', encoding='utf-8') as file:
            self.content = file.read()

    def compile(self, **kwargs: dict):
        for k, v in kwargs.items():
            self.content = self.content.replace(f'{{{{{k}}}}}', str(v))
        return self.content


class LLM(object):
    def __init__(self, model_name):
        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf.ini')
        config.read(config_file_path)

        # 模型信息初始化
        conf = get_config()
        self.model_name = conf[model_name]['model_path']
        self.openai_api_base = conf[model_name]['model_url']
        self.openai_api_key = conf[model_name]['model_api_key']
        self.input_cost_per_k_token = float(conf[model_name]['input_cost_per_k_token'])
        self.output_cost_per_k_token = float(conf[model_name]['output_cost_per_k_token'])

        # 模型计费信息
        self.all_input_tokens = 0
        self.all_output_tokens = 0
        self.all_cost = 0

        # 初始化prompt的位置，本地读取还是从langfuse读取
        self.prompt_source = 'local'

    def reset_messages(self, messages):
        if 'data:image/png;base64' in str(messages):
            for record in messages:
                for content in record['content']:
                    if content['type'] == 'image_url':
                        content['image_url']['url'] = 'encode(image_url[image_index])'
        else:
            pass

        return messages

    def cal_cost(self, response):
        try:
            input_token = response.usage.prompt_tokens
            output_token = response.usage.completion_tokens
            cost = input_token / 1000 * self.input_cost_per_k_token + output_token / 1000 * self.output_cost_per_k_token
            self.all_input_tokens += input_token
            self.all_output_tokens += output_token
            self.all_cost += cost
        except Exception as e:
            traceback.print_exc()

    def call_model(self, messages: list, business_name='营销话术生成', image_url=[]):
        """
        :param messages: [{"role": "user", "content": prompt}]
        :return:
        """
        client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            top_p=0.8,
            max_tokens=2000,
            timeout=3600,
            extra_body={"enable_thinking": False},
        )

        self.cal_cost(response)  # 计算花费
        client.close()
        return response


    def get_prompt(self, prompt_fp):
        content = ''
        if self.prompt_source == 'local':
            content = LocalPrompt(prompt_fp)
        else:
            pass
        return content


    def get_message(self, row, prompt, chat_type='text', image_type='url'):
        """
        组装prompt
        :param row: {url: ['']}
        :param prompt:
        :param type: text / image
        :return:
        """

        def get_message_image():
            # 多模态模型
            image_list = row['url']
            encode_image_list = []
            for x in image_list:
                encode_image = image_compression(x, image_type)
                if encode_image is not None:
                    encode_image_list.append(encode_image)
            if len(encode_image_list) == 0:
                raise Exception('图片获取失败')

            messages = [{
                    'role': 'user',
                    'content': [
                        {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{x}'}} for x in
                        encode_image_list
                    ]
            }]
            messages[0]['content'].append({'type': 'text', 'text': prompt})

            return messages

        def get_message_text():
            # 纯文本模型
            messages = [
                {'role': 'system', 'content': 'you are a helpful assistant'},
                {'role': 'user', 'content': prompt}
            ]
            return messages


        if chat_type == 'text':
            messages = get_message_text()
        elif chat_type == 'image':
            messages = get_message_image()
        else:
            raise Exception('模型类型错误')
        return messages


if __name__ == '__main__':
    """文本测试"""
    # model_name = 'llm-text'
    # llm = LLM(model_name)
    #
    # prompt = '你好'
    # messages = [{"role": "user", "content": prompt}]
    # output = llm.call_model(messages).choices[0].message.content
    # print(output)

    """文本测试-使用类方法获取messages"""
    model_name = 'llm-text'
    llm = LLM(model_name)
    messages = llm.get_message(row={'url': ['']}, prompt='你好', type='text')
    output = llm.call_model(messages).choices[0].message.content
    print(output)

    """prompt的测试"""
    # model_name = 'llm-text'
    # llm = LLM(model_name)
    # prompt_fp = '/Users/yangchengcheng/Documents/workspace/customer_aware_interface_template/通用工程模版/prompt/prompt.txt'
    # prompt = llm.get_prompt(prompt_fp).compile(**{'name': '张三'})
    # messages = [{"role": "user", "content": prompt}]
    # output = llm.call_model(messages).choices[0].message.content
    # print(output)

    """图片测试"""
    # model_name = 'llm-vl'
    # llm = LLM(model_name)
    # image_url = 'http://10.168.20.103/images/ithumb//2025/2025-04-05/东讯/17/2520801516195139284/2301a1cd07524becb3c803a49e41a9e7.jpg'
    # image_encode = encode_image_from_url(image_url)
    # messages = [{
    #     'role': 'user',
    #     'content': [
    #         {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{image_encode}'}},
    #         {'type': 'text', 'text': '请介绍下这幅图'}
    #     ]
    # }]
    # output = llm.call_model(messages, business_name='图片测试2', image_url=[image_url]).choices[0].message.content
    # print(output)

    """图片测试, 使用类方法获取messages"""
    # model_name = 'llm-vl'
    # llm = LLM(model_name)
    # image_url = ['http://10.168.20.103/images/ithumb//2025/2025-04-05/东讯/17/2520801516195139284/2301a1cd07524becb3c803a49e41a9e7.jpg']
    # params = {'url': image_url}
    # prompt = '请介绍下这幅图'
    # messages = llm.get_message(params, prompt, type='image')
    # output = llm.call_model(messages, business_name='图片测试2', image_url=[image_url]).choices[0].message.content
    # print(output)