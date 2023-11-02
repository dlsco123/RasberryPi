from flask import Flask, send_file, jsonify, render_template
import requests
from io import BytesIO

app = Flask(__name__)

# 라즈베리 파이 서버의 주소
RASPBERRY_PI_ADDRESS = 'http://192.168.20.135:5003'

@app.route('/')
def index():
    # 웹 UI를 렌더링하여 반환
    return render_template('index.html')

@app.route('/download-images', methods=['GET'])
def download_images():
    response = requests.get(f"{RASPBERRY_PI_ADDRESS}/download-images", timeout=10)
    if response.ok:
        memory_file = BytesIO(response.content)
        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='images.zip'
        )
    
    else:
        app.logger.error(f"Failed to download images: {response.status_code} {response.text}")
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
    app.run(host='0.0.0.0', port=5004, debug=True)