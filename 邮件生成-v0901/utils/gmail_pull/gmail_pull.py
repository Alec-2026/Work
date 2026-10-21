"""
获取独立站邮箱中客户发送的邮件
返回按 Gmail 账号分组的邮件及解码后的正文和 HTML
"""

import requests


def get_email_appendix(email, limit):
    URL = "http://47.251.75.225:5001/gmail/pull"
    # URL = "http://localhost:5001/gmail/pull"

    response = requests.post(
        URL,
        json={
            "email": email,
            "limit": limit
        },
        timeout=3600,
    )
    response.raise_for_status()
    result = response.json()

    return result

if __name__ == '__main__':
    email = "MHall@anaheimducks.com"
    limit = 1
    res = get_email_appendix(email, limit)
    print(res)
