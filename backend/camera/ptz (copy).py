import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages/") 

import serial
import time
import json
import os
import cv2

# PTZ 카메라 설정 (Pelco-D 방식)
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
CAMERA_ID = 0
PRESET_FILE = "ptz_presets.json"

ser = None  # 전역 시리얼 포트 객체

def init_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"[✅] Serial 연결 완료: {SERIAL_PORT}")
    except Exception as e:
        print(f"[❌] Serial 연결 실패: {e}")
        ser = None

def send_pelco_d(cmd_bytes):
    global ser
    if ser and ser.is_open:
        ser.write(cmd_bytes)
        ser.flush()
        print("[PELCO-D SEND]", cmd_bytes.hex())
        time.sleep(0.1)
    else:
        print("❌ Pelco-D 전송 실패: Serial 포트가 닫혀있음")

def pelco_command(cmd1, cmd2, data1, data2):
    checksum = (CAMERA_ID + cmd1 + cmd2 + data1 + data2) % 256
    cmd = bytearray([
        0xFF,
        CAMERA_ID,
        cmd1,
        cmd2,
        data1,
        data2,
        checksum
    ])
    return cmd

def control_camera(action, speed=0x3F):
    action_map = {
        'left':  lambda: send_pelco_d(pelco_command(0x00, 0x04, speed, 0x00)),
        'right': lambda: send_pelco_d(pelco_command(0x00, 0x02, speed, 0x00)),
        'up':    lambda: send_pelco_d(pelco_command(0x00, 0x08, 0x00, speed)),
        'down':  lambda: send_pelco_d(pelco_command(0x00, 0x10, 0x00, speed)),
        'stop':  lambda: send_pelco_d(pelco_command(0x00, 0x00, 0x00, 0x00)),
        'zoom_in':  lambda: send_pelco_d(pelco_command(0x00, 0x20, 0x00, 0x00)),
        'zoom_out': lambda: send_pelco_d(pelco_command(0x00, 0x40, 0x00, 0x00)),
    }

    if action in action_map:
        print(f"🎮 {action.upper()} 명령 전송됨 (Pelco-D)")
        action_map[action]()
    else:
        print(f"⚠️ 알 수 없는 PTZ 명령: {action}")

def get_camerasrc_mjpeg():
    return (
        "udpsrc port=8554 caps=application/x-rtp,media=video,encoding-name=H264,payload=96 ! "
        "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
    )

def gen_frames():
    cap = cv2.VideoCapture(get_camerasrc_mjpeg(), cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print('[ERROR] Camera not opened')
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
        )

def send_visca_store_preset(preset_id):
    print("[INFO] VISCA 프리셋 저장 명령은 비활성화됨 (Pelco-D 카메라)")

def send_visca_recall_preset(preset_id):
    print("[INFO] VISCA 프리셋 호출 명령은 비활성화됨 (Pelco-D 카메라)")
