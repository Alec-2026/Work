import requests
import json
import time
from utils.load_config import get_config


class Audio2Text(object):
    def __init__(self):
        conf = get_config()
        self.api_key = conf['audio2text']['api_key']
        self.service_url = conf['audio2text']['service_url']
        self.model_name = conf['audio2text']['model_name']
        self.vocabulary_id = conf['audio2text']['vocabulary_id']

    def submit_task(self, file_urls) -> str:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        data = {
            "model": self.model_name,
            "input": {"file_urls": file_urls},
            "parameters": {
                "channel_id": [0, 1],
                "language_hints": ["zh", "en"],
                "vocabulary_id": self.vocabulary_id,
                "disfluency_removal_enabled": "false",
                "diarization_enabled": "true",
                "speaker_count": 2
            },
        }
        # 录音文件转写服务url
        response = requests.post(
            self.service_url,
            headers=headers,
            data=json.dumps(data)
        )

        # 打印响应内容
        if response.status_code == 200:
            return response.json()["output"]["task_id"]
        else:
            print("task failed!")
            print(response.json())
            return None


    def wait_for_complete(self, task_id):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }

        pending = True
        while pending:
            # 查询任务状态服务url
            service_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            response = requests.post(
                service_url, headers=headers
            )
            if response.status_code == 200:
                status = response.json()['output']['task_status']
                if status == 'SUCCEEDED':
                    print("task succeeded!")
                    pending = False
                    return response.json()
                elif status == 'RUNNING' or status == 'PENDING':
                    pass
                else:
                    print("task failed!")
                    pending = False
            else:
                print("query failed!")
                pending = False
            print(response.json())
            time.sleep(0.1)

    def get_json_by_url(self, json_url):
        try:
            # 发送 GET 请求获取 JSON 数据
            response = requests.get(json_url)
            # 检查响应状态码是否为 200
            if response.status_code == 200:
                # 将响应内容解析为 JSON 并返回
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"请求发生错误: {e}")
            return None

    def format_text(self, result: dict) -> str:
        role_dict = {'0': 'A', '1': 'B', '2': 'C', '3': 'D'}
        chat_records = []
        transcripts = result['transcripts']
        for para in transcripts:
            for sen in para['sentences']:
                sentences = {
                    'begin_time': sen['begin_time'],
                    'sentence': role_dict[str(sen['speaker_id'])] + ': ' + sen['text'],
                }
                chat_records.append(sentences)

        chat_records = sorted(chat_records, key=lambda x: x["begin_time"])
        chat_records_list = [x['sentence'] for x in chat_records]
        return '\n'.join(chat_records_list)


    def auto2text(self, file_urls):
        task_id = self.submit_task(file_urls)
        print("task_id: ", task_id)
        result = self.wait_for_complete(task_id)
        print("transcription result: ", result)
        res_json_url = result['output']['results'][0]['transcription_url']

        result = self.get_json_by_url(res_json_url)
        chat_records = self.format_text(result)
        duration = result['properties']['original_duration_in_milliseconds'] / 1000
        return chat_records, duration


if __name__ == '__main__':
    at = Audio2Text()
    url = [
        'https://www.36588.com.cn/bmpupload/wxworkChatRecord/2025-08-04/yihao/meeting_voice_call/76742663.MP3'
    ]
    res = at.auto2text(url)
    print(res)
    #
    # json_url = 'https://www.36588.com.cn/bmpupload/wxworkChatRecord/2025-08-04/yihao/meeting_voice_call/76618489.MP3'
    # res = at.get_json_by_url(json_url)
    # res = at.format_text(res)
    # print('>>>\n', res)
