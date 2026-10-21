import requests
import os
import librosa

"""
音频处理:
将音频下载到本地，使用结束后删除文件
"""


class AudioProcess(object):
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        self.video_name = ''

    def download_audio(self, url):
        video_name = url.split('/')[-1]
        self.video_name = video_name
        fp = os.path.join(self.cache_dir, video_name)

        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # 检查请求是否成功
            with open(fp, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):  # 分块写入文件
                    file.write(chunk)
        
        # 获取音频时长
        duration = librosa.get_duration(path=fp)
        return fp, duration
        

    def close(self):
        """
        删除指定文件
        :param video_name: 要删除的文件名（含路径）
        :return: True if file deleted successfully, False otherwise
        """
        if '/' in self.video_name:
            fp = self.video_name
        else:
            fp = os.path.join(self.cache_dir, self.video_name)

        try:
            # 检查文件是否存在
            if os.path.isfile(fp):
                os.remove(fp)
                print(f"文件 {self.video_name} 已成功删除。")
                return True
            else:
                print(f"错误：文件 {self.video_name} 不存在。")
                return False
        except PermissionError:
            print(f"错误：没有权限删除文件 {self.video_name}。")
            return False
        except Exception as e:
            print(f"删除文件 {self.video_name} 时发生错误：{e}")
            return False



if __name__ == '__main__':
    url = 'https://www.36588.com.cn/bmpupload/wxworkChatRecord/2025-08-04/dongxun/meeting_voice_call/15937314.MP3'
    fp, duration = AudioProcess().download_audio(url)
    print(fp, duration)
