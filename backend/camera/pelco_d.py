# backend/camera/pelco_d.py
import serial
import time

SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600  # 기본값. 카메라 메뉴에서 9600, 4800일 수도 있음
CAMERA_ID = 0   # DIP 스위치에서 설정한 주소

def send_pelco_d(cmd_bytes):
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
        ser.write(cmd_bytes)
        print("[PELCO-D SEND]", cmd_bytes.hex())
        time.sleep(0.2)

def pelco_command(cmd1, cmd2, data1, data2):
    cmd = bytearray([
        0xFF,
        CAMERA_ID,
        cmd1,
        cmd2,
        data1,
        data2
    ])
    checksum = sum(cmd[1:]) % 256
    cmd.append(checksum)
    return cmd

# 방향 제어
def move_left(speed=0x20):   send_pelco_d(pelco_command(0x00, 0x04, speed, 0x00))
def move_right(speed=0x20):  send_pelco_d(pelco_command(0x00, 0x02, speed, 0x00))
def move_up(speed=0x20):     send_pelco_d(pelco_command(0x00, 0x08, 0x00, speed))
def move_down(speed=0x20):   send_pelco_d(pelco_command(0x00, 0x10, 0x00, speed))
def stop():                  send_pelco_d(pelco_command(0x00, 0x00, 0x00, 0x00))

# 줌 제어
def zoom_in():               send_pelco_d(pelco_command(0x00, 0x20, 0x00, 0x00))
def zoom_out():              send_pelco_d(pelco_command(0x00, 0x40, 0x00, 0x00))
