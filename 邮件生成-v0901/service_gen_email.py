from flask import Flask, request, jsonify
from utils.logging_config import configure_logging
from app_tag import tag_app
from utils.upload_prompt import upload_prompt

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# 日志配置
configure_logging()

# prompt上传
business_name = '独立站邮件生成'
upload_prompt(business_name)


@app.route('/gen_email', methods=['POST'])
def audio_main():
    params = request.get_json()
    params['remote_addr'] = request.remote_addr
    app.logger.info(f'参数接收成功: {params}')
    response = tag_app(params)
    result = {
        'code': response['code'],
        'model_response': response['model_response'],
        'info': response['info']
    }

    app.logger.info(f'params:{params}\nresponse:{result}')

    return jsonify(result)



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5022
    )
