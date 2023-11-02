from flask import Flask, send_file, jsonify, request
import cv2
import os
import threading
import zipfile
from io import BytesIO
from time import sleep, time

app = Flask(__name__)

# 이미지를 저장할 디렉토리
IMAGE_DIR = "captured_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# 촬영 제어를 위한 플래그
capturing = True

# 카메라 설정
camera = cv2.VideoCapture(0)  # 0은 일반적으로 시스템의 첫 번째 카메라를 가리킵니다.

def capture_images():
    global capturing
    while True:
        if capturing:
            start_time = time()
            for i in range(5):  # 5fps로 5장의 사진을 찍음
                ret, frame = camera.read()
                if ret:
                    image_path = os.path.join(IMAGE_DIR, f'image_{start_time}_{i}.jpg')
                    cv2.imwrite(image_path, frame)
                sleep(0.2)  # 5fps를 유지하기 위해 0.2초 간격으로 촬영
            sleep(max(3 - (time() - start_time), 0))  # 다음 3초 주기를 기다림
        else:
            sleep(1)  # 촬영이 중지된 경우, 루프를 느슨하게 실행

# 이미지 캡처 스레드 시작
threading.Thread(target=capture_images, daemon=True).start()

@app.route('/download-images', methods=['GET'])
def download_images():
    global capturing
    capturing = False  # 촬영 중지
    sleep(3)  # 현재 진행 중인 촬영 주기를 완료할 시간을 줌

    # 압축 파일을 메모리에 생성
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # IMAGE_DIR 내의 모든 파일을 압축 파일에 추가
        for root, dirs, files in os.walk(IMAGE_DIR):
            for file in files:
                zf.write(os.path.join(root, file), file)
    # 포인터를 시작 부분으로 이동
    memory_file.seek(0)
    
    capturing = True  # 촬영 재개
    # 압축 파일을 응답으로 전송
    return send_file(
    memory_file,
    mimetype='application/zip',
    as_attachment=True,
    download_name='images.zip'
)
    
@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'running'}), 200

@app.route('/stop', methods=['GET'])
def stop_capturing():
    global capturing
    capturing = False
    return jsonify({'status': 'stopped'}), 200

@app.route('/start', methods=['GET'])
def start_capturing():
    global capturing
    capturing = True
    return jsonify({'status': 'running'}), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5003)
    finally:
        camera.release()  # 카메라 자원을 해제합니다.
