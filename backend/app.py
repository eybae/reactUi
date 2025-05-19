import sys
import json
import time
import base64
import traceback
import threading
import re
import os
from queue import Queue

from flask import Flask, request, jsonify, send_file, Response
from flask_socketio import SocketIO
from flask_cors import CORS
from paho.mqtt.client import Client as MQTTClient

from LampCont import dataParsing
from LampCont import downlink
from camera import ptz

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
    "Lamp1": "0080e11500000001",
    "Lamp2": "0080e11500000002",
    "Lamp3": "0080e11500000003",
    "Lamp4": "0080e11500000004",
    "Lamp5": "0080e11500000005",
    "Lamp6": "0080e11500000006",
    "Lamp7": "0080e11500000007",
    "Lamp8": "0080e11500000008",
    "Lamp9": "0080e11500000009",
    "Lamp10": "0080e1150000000a",
}

# 상태 저장
led_states = {}
expected_states = {}
last_sent_time = {}
retry_counts = {}  # 재시도 횟수 저장
MAX_RETRY = 3
STATE_FILE = "led_states.json"
status_check_queue = Queue()

# 상태 저장/복원 함수
def save_led_states():
    with open(STATE_FILE, "w") as f:
        json.dump(led_states, f)

def load_led_states():
    global led_states
    try:
        with open(STATE_FILE) as f:
            led_states = json.load(f)
        print("📂 이전 상태 복구 완료:", led_states)
    except:
        led_states = {}
        print("📁 상태 파일 없음. 새로 시작.")

# MQTT 콜백

def on_connect(client, userdata, flags, rc):
    print("📡 MQTT 연결 완료")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_str = msg.payload.decode()
        payload_json = json.loads(payload_str)

        # 공통 추출
        device_info = payload_json.get("deviceInfo", {})
        dev_eui = device_info.get("devEui")
        dev_key = next((k for k, v in DEV_MAP.items() if v == dev_eui), dev_eui)

        # ✅ txack 처리 (전송 확인만)
        if topic.endswith("/event/txack"):
            print(f"📨 txack 수신됨 → 명령 전송 확인: {dev_key}")
            socketio.emit("device_txack", {
                "device": dev_key
            })
            return  # 여기서 종료, ledStates 저장은 하지 않음

        # ✅ uplink 수신 처리 (상태 파싱 및 UI 반영)
        object_json = payload_json.get("objectJSON")
        if object_json:
            try:
                obj = json.loads(object_json)
                status = obj.get("status")
                brightness = obj.get("brightness")
                dev_data = {"status": status, "brightness": brightness}
            except Exception as parse_err:
                print("❌ objectJSON 파싱 오류:", parse_err)
                return
        else:
            print("⚠️ objectJSON 없음, 기본 파싱 사용")
            dev_data = dataParsing.deviceDataParsing(payload_json)

        print(f"🔎 파싱된 장비 상태: {dev_data}")

        expected = expected_states.get(dev_key)
        pending = (
            expected
            and (
                dev_data.get("status") != expected.get("status")
                or dev_data.get("brightness") != expected.get("brightness")
            )
        )

        if not pending:
            expected_states.pop(dev_key, None)
            retry_counts.pop(dev_key, None)
            last_sent_time.pop(dev_key, None)

        # 상태 저장 및 전송
        led_states[dev_key] = dev_data
        save_led_states()

        print(f"📤 UI로 전송: {dev_key} => {dev_data}, pending: {pending}")
        socketio.emit("device_status_update", {
            "device": dev_key,
            "status": dev_data["status"],
            "brightness": dev_data["brightness"],
            "pending": pending
        })

    except Exception as e:
        print(f"⚠️ on_message 처리 오류: {e}")

# 상태 확인용 큐에 전체 장비 등록

def enqueue_status_check():
    time.sleep(10)
    for dev_key in list(expected_states.keys()):
        status_check_queue.put(dev_key)
        print(f"📝 상태 확인 큐 등록: {dev_key}")

# 하나씩 상태 확인 전송
def sequential_status_check():
    while True:
        if not status_check_queue.empty():
            led_key = status_check_queue.get()
            expected = expected_states.get(led_key)
            if not expected:
                continue
            actual = led_states.get(led_key)

            if actual != expected:
                count = retry_counts.get(led_key, 0)
                if count < MAX_RETRY:
                    print(f"🔁 상태 확인 재요청 ({count+1}/{MAX_RETRY}): {led_key} → {expected}")
                    payload_bytes = dataParsing.encode_group_payload(
                        0, 1,
                        expected["status"],
                        expected["brightness"],
                        "00:00", "00:00"
                    )
                    dev_id = DEV_MAP.get(led_key)
                    if dev_id:
                        downlink.sendData(dev_id, payload_bytes)
                    retry_counts[led_key] = count + 1
                    status_check_queue.put(led_key)  # 다시 큐에 넣음
                else:
                    print(f"❌ 최대 재시도 초과: {led_key}")
            else:
                print(f"✅ 상태 일치 확인됨: {led_key}, 큐 제거")
                retry_counts.pop(led_key, None)
            time.sleep(5)

# REST API
@app.route("/api/devices/status")
def get_all_led_states():
    return jsonify(led_states)


# 제어 API
@app.route('/group/control', methods=['POST'])
def group_control():
    data = request.json
    mode = data.get("mode", 0)
    cmd = data.get('cmd', 1)
    state = data.get('state', 'off')
    brightness = data.get('brightness', 0)
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
            status_check_queue.put(led_key)
            last_sent_time[led_key] = time.time()
            downlink.sendData(devId, payload_bytes)
            #time.sleep(0.5)

        print(f"📤 전송 바이트: {[hex(b) for b in payload_bytes]}")
        return jsonify({"status": "success"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
        
@app.route('/single/control', methods=['POST'])
def single_control():
    try:
        data = request.json
        dev_eui = data.get("devEui")
        state = data.get("state", "off")
        brightness = int(data.get("brightness", 0))
        on_time = data.get("onTime", "00:00")
        off_time = data.get("offTime", "00:00")

        # devEUI -> Lamp 키 매핑
        lamp_key = None
        for k, v in DEV_MAP.items():
            if v == dev_eui:
                lamp_key = k
                break
        if lamp_key is None:
            return jsonify({"status": "error", "message": f"Unknown devEUI: {dev_eui}"}), 400

        # 기대 상태 등록
        expected_states[lamp_key] = {
            "status": state,
            "brightness": brightness,
        }
        retry_counts[lamp_key] = 0
        status_check_queue.put(lamp_key)
        last_sent_time[lamp_key] = time.time()

        # 전송 payload 생성 및 전송
        payload_bytes = dataParsing.encode_group_payload(0, 1, state, brightness, on_time, off_time)
        downlink.sendData(dev_eui, payload_bytes)

        print(f"📤 개별제어 전송: {lamp_key}({dev_eui}) => {payload_bytes}")
        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ 개별제어 오류:", e)
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

@app.route("/ptz/osd", methods=["POST"])
def ptz_call_osd():
    ptz.call_osd_menu()
    return jsonify({"success": True, "message": "OSD 호출됨"})

@app.route("/ptz/osd/confirm/iris", methods=["POST"])
def ptz_osd_confirm_iris():
    ptz.osd_confirm_iris_open()
    return jsonify({"success": True})

@app.route("/ptz/osd/cancel", methods=["POST"])
def ptz_osd_cancel():
    ptz.osd_cancel()
    return jsonify({"success": True})

@app.route("/ptz/osd/cancel/zoom", methods=["POST"])
def ptz_osd_cancel_zoom():
    ptz.osd_cancel_zoom_out()
    return jsonify({"success": True})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ WebSocket 연결 종료됨: {request.sid}")

LOG_DIRS = {
    "esls": "/home/stn/Dev/esls-testbed/log",
    "ui": "/home/stn/Dev/uiTest/backend/logs"
}

# 재귀적으로 로그 파일 찾기
def find_all_logs(folder, rel_base):
    files = []
    for root, _, filenames in os.walk(folder):
        for fname in filenames:
            # 🔽 필터링 제거
            rel_path = os.path.relpath(os.path.join(root, fname), folder)
            files.append({
                "name": fname,
                "relative_path": os.path.join(rel_base, rel_path).replace("\\", "/")
            })
    return files

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
    load_led_states()
    ptz.init_serial()
    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    mqtt.connect(BROKER, 1883, 60)
    mqtt.loop_start()

    threading.Thread(target=enqueue_status_check, daemon=True).start()
    threading.Thread(target=sequential_status_check, daemon=True).start()

    socketio.run(app, host='0.0.0.0', port=5050, allow_unsafe_werkzeug=True)
