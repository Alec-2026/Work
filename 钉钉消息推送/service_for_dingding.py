from flask import Flask, request, jsonify
from app import send_message

app = Flask(__name__)

@app.route('/hubspot', methods=['POST'])
def send():
    send_message()
    return jsonify({'message': 'ok'})

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5009
    )