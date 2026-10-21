import requests
import json


def get_website_content(target_url):
    headers = {"Content-Type": "application/json"}
    url = 'http://47.251.75.225:5005/get_website_content'
    url = 'http://localhost:5005/get_website_content'
    data = {'url': target_url}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()
    return response_json


if __name__ == '__main__':
    # url = 'https://www.bookitprogram.com'
    url = 'https://www.sumalifehouse.com'
    response_json = get_website_content(url)
    print(json.dumps(response_json, indent=4, ensure_ascii=False))