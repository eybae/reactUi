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

def init_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"[INFO] Serial port {SERIAL_PORT} opened successfully.")
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port: {e}")
        return None

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

def control_camera(action, speed=32):
    commands = {
        'left': generate_command(0x00, 0x04, speed, 0x00),
        'right': generate_command(0x00, 0x02, speed, 0x00),
        'up': generate_command(0x00, 0x08, 0x00, speed),
        'down': generate_command(0x00, 0x10, 0x00, speed),
        'zoom_in': generate_command(0x00, 0x20),
        'zoom_out': generate_command(0x00, 0x40),
        'stop': generate_command(0x00, 0x00)
    }
    if action in commands:
        send_command(commands[action])

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


