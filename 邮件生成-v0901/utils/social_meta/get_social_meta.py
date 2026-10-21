#!/usr/bin/env python3
"""通过 TikHub 获取 Twitter、LinkedIn 公开元数据并生成 Markdown 报告。"""

import http.client

class SocialMeta:
    """
    获取用户在社交平台上的数据
    """
    def __init__(self, timeout=30):
        self.tikhub_base = "https://api.tikhub.io/api/v1"
        self.tikhub_api_key = "3M4JBJgb22qNg0q4LYiemQfvKwWjBKly/SnhtFyQV8aH13WxKEzZeyLPFQ=="
        self.tikhub_domain = 'api.tikhub.dev'
        self.timeout = timeout

    def get_linked_profile(self, url):
        """
        获取linkedin的个人信息
        """
        def get_interface_by_user_type(url):
            # 根据用户类型判断要访问的接口
            if '/in/' in url:
                return f"/api/v1/linkedin/web_v2/get_user_profile?url={url}"
            elif '/company/' in url:
                return f"/api/v1/linkedin/web_v2/get_company_profile?url={url}"
            else:
                return None

        conn = http.client.HTTPSConnection(self.tikhub_domain)
        payload = ''
        headers = {'Authorization': f'Bearer {self.tikhub_api_key}'}
        interface = get_interface_by_user_type(url)
        if interface:
            conn.request("GET", interface, payload, headers)
            res = conn.getresponse()
            data = res.read()
            res = data.decode("utf-8")
            return res
        else:
            return None




if __name__ == '__main__':
    sm = SocialMeta()
    name = 'https://www.linkedin.com/company/meridianeventsnyc'
    # name = 'https://www.linkedin.com/in/jayzofficial'
    res = sm.get_linked_profile(name)
    print(res)
