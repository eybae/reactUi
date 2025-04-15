import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages/") 

from flask import Flask, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from paho.mqtt.client import Client as MQTTClient
from LampCont import dataParsing
from camera import ptz
import os
from datetime import datetime
import json
import threading
from flask import jsonify



app = Flask(__name__)
CORS(app)
#socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# MQTT 클라이언트
mqtt = MQTTClient()

APPID = "1"
TOPIC = 'application/1/#'
DEV01 = "dev01"
BROKER = "192.168.10.10"

led_states = {}
devEUI = ""

# MQTT 콜백
def on_connect(client, userdata, flags, rc):
    print("📡 MQTT 브로커 연결됨")
    client.subscribe(TOPIC)  # 예: led/1/status

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_str = msg.payload.decode()
        payload_json = json.loads(payload_str)

        devEUI = payload_json.get("deviceName")
        if not devEUI:
            print("⚠️ deviceName 없음")
            return

        dev_data = dataParsing.deviceDataParsing(payload_json)

        # 상태 저장
        led_states[devEUI] = {
            "status": "on" if dev_data.get("state") == 1 else "off",
            "brightness": dev_data.get("dem", 0)
        }

        print(f"💾 저장됨: {devEUI} -> 상태: {led_states[devEUI]}")

        # 안전한 emit
        import re
        led_id = re.findall(r'\d+', devEUI)
        led_id = led_id[0] if led_id else "0"
        
        print(f"🚀 WebSocket emit → LED {led_id}")

        socketio.emit("device_status_update", {
            "device": f"LED {led_id}",
            "status": led_states[devEUI]["status"],
            "brightness": led_states[devEUI]["brightness"]
        })

    except Exception as e:
        print(f"⚠️ on_message 처리 중 오류: {e}")
        
def delayed_emit():
    import time
    time.sleep(2)
    print("🚀 테스트 emit")

    socketio.emit("device_status_update", {
        "device": "LED 2",
        "status": "on",
        "brightness": 75
    })

threading.Thread(target=delayed_emit).start()

# MQTT 초기화
mqtt.on_connect = on_connect
mqtt.on_message = on_message
mqtt.connect(BROKER, 1883, 60)
mqtt.loop_start()

@app.route('/')
def index():
    return "Flask WebSocket Server is running"

@socketio.on('connect')
def handle_connect():
    print(f"✅ WebSocket 연결됨: {request.sid}")

@socketio.on('set_brightness')
def handle_set_brightness(data):
    print(f"💡 밝기 변경 요청 수신: {data}")

    # 예시 응답: 상태 다시 클라이언트에게 broadcast
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

if __name__ == '__main__':
    ptz.init_serial()
    socketio.run(app, host='0.0.0.0', port=5050)
