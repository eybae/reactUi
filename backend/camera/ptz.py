import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages/") 

import serial
import time
import json
import os
import cv2


# PTZ 카메라 설정
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
ADDRESS = 0
PRESET_FILE = "ptz_presets.json"

try:
    ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
    print(f"[✅] Serial 연결 완료: {ser.port}")
except Exception as e:
    ser = None
    print(f"[❌] Serial 연결 실패: {e}")    

def send_command(command):
    print(f"[SEND] {command.hex()}")
    try:
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
            ser.write(command)
            time.sleep(0.3)
    except Exception as e:
        print(f"[ERROR] Failed to send command: {e}")

def generate_command(cmd1, cmd2, data1=0x00, data2=0x00):
    command = bytearray([0xFF, ADDRESS, cmd1, cmd2, data1, data2])
    checksum = sum(command[1:]) % 256
    command.append(checksum)
    return command

def control_camera(action, speed=3):
    if not ser or not ser.is_open:
        print("❌ 시리얼 포트 연결 안됨")
        return

    speed = max(1, min(speed, 7))

    # VISCA PTZ 명령 (Pan-Tilt Drive)
    # 구조: 81 01 06 01 VV WW XX YY FF
    # VV = pan speed (01~18), WW = tilt speed (01~14)
    # XX = pan direction, YY = tilt direction

    direction_map = {
        'left':  (speed, speed, 0x01, 0x03),  # Pan Left
        'right': (speed, speed, 0x02, 0x03),  # Pan Right
        'up':    (speed, speed, 0x03, 0x01),  # Tilt Up
        'down':  (speed, speed, 0x03, 0x02),  # Tilt Down
        'stop':  (0x03, 0x03, 0x03, 0x03),    # Stop both
    }

    if action in direction_map:
        pan_speed, tilt_speed, pan_dir, tilt_dir = direction_map[action]
        cmd = b"\x81\x01\x06\x01" + bytes([pan_speed, tilt_speed, pan_dir, tilt_dir]) + b"\xFF"
        serial.write(cmd)
        print(f"🎮 {action.upper()} 명령 전송됨 (속도: {speed})")
    elif action == "zoom_in":
        serial.write(b"\x81\x01\x04\x07\x20\xFF")
    elif action == "zoom_out":
        serial.write(b"\x81\x01\x04\x07\x30\xFF")
    else:
        print(f"⚠️ 알 수 없는 PTZ 명령: {action}")

def get_camerasrc_mjpeg():
    return (
        "udpsrc port=8554 caps=application/x-rtp,media=video,encoding-name=H264,payload=96 ! "
        "rtph264depay ! avdec_h264 ! "
        "videoconvert ! appsink" 
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
    command = bytearray([0x81, 0x01, 0x04, 0x3F, 0x01, 0x00, preset_id, 0xFF])
    send_command(command)

def send_visca_recall_preset(preset_id):
    command = bytearray([0x81, 0x01, 0x04, 0x3F, 0x02, 0x00, preset_id, 0xFF])
    send_command(command)


