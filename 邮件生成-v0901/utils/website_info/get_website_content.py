import traceback
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB


def get_website_info(url):
    url = 'https://' + url if 'http' not in url else url
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.title.string
        paragraphs = soup.find_all('p')
        par_list = []
        for para in paragraphs:
            par_list.append(para.get_text())
        return {
            'title': title,
            'paragraphs': '\n'.join(par_list),
            'info': 'success'
        }
    else:
        return {
            'title': '',
            'paragraphs': '',
            'info': f"请求失败，状态码: {response.status_code}"
        }


@app.route('/get_website_content', methods=['POST'])
def get_website_content():
    try:
        params = request.get_json()
        print(params)
        url = params.get('url', None)
        response = get_website_info(url)
        info = response.pop('info', None)
        result = {'code': 1, 'model_response': response, 'info': info}
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'code': 0, 'model_response': '无官网信息', 'info': f'failed: {str(repr(e))}'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
