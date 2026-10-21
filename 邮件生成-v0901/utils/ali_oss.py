import oss2
from utils.load_config import get_config

"""
将图片上传到oss，并获取oss的公开链接
"""


class AliOss(object):
    def __init__(self):
        conf = get_config()
        self.accessKeyId = conf['oss']['accessKeyId']
        self.accessKeySecret = conf['oss']['accessKeySecret']
        self.endpoint = conf['oss']['endpoint']
        self.bucket_name = conf['oss']['bucket_name']
        self.region = conf['oss']['region']

        self.auth = oss2.Auth(self.accessKeyId, self.accessKeySecret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name, region=self.region)

        self.object_name = ''

    def upload_to_oss(self, file_path):
        object_name = file_path.split('/')[-1]
        self.object_name = object_name
        self.bucket.put_object_from_file(object_name, file_path)
        return object_name

    def get_url_from_oss(self, object_name):
        signed_url = self.bucket.sign_url('GET', object_name, expires=86400)  # 设置一天的有效期
        return signed_url

    def close(self):
        if self.object_name != '':
            self.bucket.delete_object(self.object_name)
        else:
            print('无需删除')


    def translate_to_oss_url(self, file_path):
        object_name = self.upload_to_oss(file_path)
        signed_url = self.get_url_from_oss(object_name)
        return signed_url


if __name__ == '__main__':
    fp = '/Users/yangchengcheng/Documents/workspace/api_online/用户运营相关/语音分析/data/77334199.mp3'
    ali = AliOss()
    url = ali.translate_to_oss(fp)
    # ali.delete_file('77334199.mp3')
    print(url)