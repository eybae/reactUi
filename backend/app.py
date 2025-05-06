import sys

print("🔍 Python sys.version:", sys.version)
print("🔍 sys.path:")
for p in sys.path:
    print("   ", p)

import json
print("✅ json module loaded from:", json.__file__)

import time
#import json
import base64
import traceback
import threading
import re

from flask import Flask, request, jsonify, send_file,Response
from flask_socketio import SocketIO
from flask_cors import CORS
from paho.mqtt.client import Client as MQTTClient

from LampCont import dataParsing
from LampCont import downlink
from camera import ptz

import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# MQTT 설정
mqtt = MQTTClient()
BROKER = "localhost"
TOPIC = 'application/46619040-fa61-4d88-a2bc-76032aeeb6f4/#'
APPID = "46619040-fa61-4d88-a2bc-76032aeeb6f4"

# 디바이스 정보
DEV_MAP = {
    #"Lamp1": "0080e115000ae9ae"
    "Lamp1": "0080e1150000be14",
    "Lamp2": "0080e1150000cda3",
    #"Lamp3": "0080e1150000c318",
    #"Lamp4": "0080e1150000ce98",
    #"Lamp5": "0080e1150000cf78",
}

# 상태 저장
led_states = {}
expected_states = {}
retry_counts = {}
last_sent_time = {}
RETRY_INTERVAL = 5
MAX_RETRY = 3

# 상태 모니터링 스레드

def monitor_expected_states():
    while True:
        now = time.time()
        for led_key, expected in list(expected_states.items()):
            retry = retry_counts.get(led_key, 0)
            last_sent = last_sent_time.get(led_key, 0)

            if retry >= MAX_RETRY:
                continue

            if now - last_sent >= RETRY_INTERVAL:
                print(f"🔁 주기적 재전송: {led_key} ({retry + 1}/{MAX_RETRY})")
                payload_bytes = dataParsing.encode_group_payload(
                    0, 1,
                    expected["status"],
                    expected["brightness"],
                    "00:00", "00:00"
                )
                dev_id = DEV_MAP.get(led_key)
                if dev_id:
                    downlink.sendData(dev_id, payload_bytes)
                    last_sent_time[led_key] = now
                    retry_counts[led_key] = retry + 1
        time.sleep(1)

# MQTT 콜백

def on_connect(client, userdata, flags, rc):
    print("📡 MQTT 연결 완료")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode()
        payload_json = json.loads(payload_str)
        deviceInfo = payload_json.get("deviceInfo")
        if not deviceInfo or "devEui" not in deviceInfo:
            print("⚠️ deviceInfo 누락됨:", payload_json)
            return
        devEUI = deviceInfo.get("devEui")

        dev_data = dataParsing.deviceDataParsing(payload_json)
        print(f"🔎 파싱된 장비 상태: {dev_data}")

        actual_status = dev_data

        # devEUI -> Lamp 이름 찾기
        dev_key = None
        for k, v in DEV_MAP.items():
            if v == devEUI:
                dev_key = k
                break

        if dev_key:
            led_key = dev_key  # ex) Lamp1
        else:
            led_key = devEUI

        # 🔄 기대 상태와 일치하는지 먼저 확인하고 pop 처리
        expected = expected_states.get(led_key)
        if expected and actual_status == expected:
            print(f"✅ 기대 상태 반영됨: {led_key}")
            expected_states.pop(led_key, None)
            retry_counts.pop(led_key, None)
            last_sent_time.pop(led_key, None)

        # ⚠️ 상태가 동일하더라도 emit()은 항상 수행
        prev = led_states.get(led_key)
        if prev == actual_status:
            print(f"⚠️ 상태 동일 (무시됨): {led_key} => {actual_status}")
            socketio.emit("device_status_update", {
                "device": led_key,
                "status": actual_status["status"],
                "brightness": actual_status["brightness"]
            })
            return

        # 💾 상태 저장
        led_states[led_key] = actual_status
        print(f"💾 저장됨: {led_key} -> 상태: {actual_status}")

        # 📤 상태 전송
        print(f"📤 UI로 전송: {led_key} => {actual_status}")
        socketio.emit("device_status_update", {
            "device": led_key,
            "status": actual_status["status"],
            "brightness": actual_status["brightness"]
        })

    except Exception as e:
        print(f"⚠️ on_message 처리 오류: {e}")



# 제어 API

@app.route('/group/control', methods=['POST'])
def group_control():
    data = request.json
    mode = data.get("mode", 0)
    cmd = data.get('cmd', 1)
    state = data.get('state', 'off')
    brightness = data.get('brightness', 1)
    on_time = data.get('onTime', '00:00')
    off_time = data.get('offTime', '00:00')

    try:
        payload_bytes = dataParsing.encode_group_payload(mode, cmd, state, brightness, on_time, off_time)
        for devName, devId in DEV_MAP.items():
            led_key = devName  # "Lamp1"
            expected_states[led_key] = {
                "status": state,
                "brightness": brightness
            }
            retry_counts[led_key] = 0
            last_sent_time[led_key] = time.time()
            downlink.sendData(devId, payload_bytes)
            time.sleep(0.5)

        print(f"📤 전송 바이트: {[hex(b) for b in payload_bytes]}")
        return jsonify({"status": "success"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
        

@app.route('/')
def index():
    return "Flask WebSocket Server is running"

@socketio.on('connect')
def handle_connect():
    print(f"✅ WebSocket 연결됨: {request.sid}")

@socketio.on('set_brightness')
def handle_set_brightness(data):
    print(f"💡 밝기 변경 요청 수신: {data}")
    socketio.emit('device_status_update', {
        'device': f"LED {data['device_id']}",
        'status': 'on',
        'brightness': data['brightness']
    })

@app.route('/stream.mjpg')
def stream_camera():
    return Response(ptz.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/ptz/control", methods=["POST"])
def ptz_control():
    data = request.json
    action = data.get("action", "stop")
    speed = data.get("speed", 63)
    ptz.control_camera(action, speed)
    return jsonify({"success": True, "action": action})

@app.route("/ptz/preset/store", methods=["POST"])
def ptz_store_preset():
    data = request.json
    preset_id = int(data.get("preset_id", 1))
    ptz.send_preset_store(preset_id)
    return jsonify({"success": True, "preset_id": preset_id})

@app.route("/ptz/preset/recall", methods=["POST"])
def ptz_recall_preset():
    data = request.json
    preset_id = int(data.get("preset_id", 1))
    ptz.send_preset_recall(preset_id)
    return jsonify({"success": True, "preset_id": preset_id})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ WebSocket 연결 종료됨: {request.sid}")

LOG_DIRS = {
    "esls": "/home/stn/Dev/esls-testbed/log",
    "ui": "/home/stn/Dev/uiTest/backend/logs"
}

# 재귀적으로 로그 파일 찾기
def find_all_logs(base_path, rel_base=""):
    log_files = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith(".csv") or f.endswith(".log"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_path)
                log_files.append({
                    "name": f,
                    "relative_path": os.path.join(rel_base, rel_path).replace("\\", "/")
                })
    return log_files

# 모든 .csv 파일 리스트 API
@app.route('/api/logs/list')
def list_log_files():
    all_files = []
    for source, folder in LOG_DIRS.items():
        try:
            log_files = find_all_logs(folder, rel_base=source)
            all_files.extend(log_files)
        except Exception as e:
            print(f"❌ Failed to read from {folder}: {e}")
    return jsonify(all_files)

# CSV 파일 내용 읽기 API
@app.route('/api/logs/file')
def get_log_file():
    relative_path = request.args.get("path")
    if not relative_path:
        return "Missing path", 400

    for source, folder in LOG_DIRS.items():
        if relative_path.startswith(source + "/"):
            rel_path = relative_path[len(source) + 1:]
            full_path = os.path.join(folder, rel_path)
            if not os.path.exists(full_path):
                return "File not found", 404
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read(), 200, {"Content-Type": "text/csv"}

    return "Invalid source", 400
    
# 파일 다운로드 API
@app.route('/api/logs/download')
def download_log_file():
    relative_path = request.args.get("path")
    if not relative_path:
        return "Missing path", 400

    try:
        source, filename = relative_path.split("/", 1)  # 여기만 바꿈
        folder = LOG_DIRS.get(source)
        if not folder:
            return "Invalid source", 400

        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            return "File not found", 404

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}", 500
   

if __name__ == '__main__':
    ptz.init_serial()
    #mqtt.on_connect = on_connect
    #mqtt.on_message = on_message
    #mqtt.connect(BROKER, 1883, 60)
    #mqtt.loop_start()

    #monitor_thread = threading.Thread(target=monitor_expected_states, daemon=True)
    #monitor_thread.start()

    socketio.run(app, host='0.0.0.0', port=5050, allow_unsafe_werkzeug=True)
