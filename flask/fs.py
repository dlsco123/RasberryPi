from flask import Flask, send_file, jsonify, render_template
import requests
from io import BytesIO

app = Flask(__name__)

# 라즈베리 파이 서버의 주소
RASPBERRY_PI_ADDRESS = 'http://raspberrypi:5000'

@app.route('/')
def index():
    # 웹 UI를 렌더링하여 반환
    return render_template('index.html')

@app.route('/download-images', methods=['GET'])
def download_images():
    # 라즈베리 파이 서버에 저장된 이미지들을 압축 파일로 다운로드
    response = requests.get(f"{RASPBERRY_PI_ADDRESS}/download-images")
    if response.ok:
        # 메모리에 압축 파일 생성
        memory_file = BytesIO(response.content)
        memory_file.seek(0)
        # 압축 파일을 응답으로 전송
        return send_file(memory_file, attachment_filename='images.zip', as_attachment=True)
    else:
        return jsonify({'message': 'Failed to download images from Raspberry Pi'}), response.status_code

@app.route('/status', methods=['GET'])
def status():
    # 라즈베리 파이 서버의 상태를 확인
    try:
        response = requests.get(f"{RASPBERRY_PI_ADDRESS}/status")
        if response.ok:
            return jsonify({'status': 'Raspberry Pi is running'}), 200
        else:
            return jsonify({'status': 'Raspberry Pi is not responding'}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'Raspberry Pi is not reachable', 'error': str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)