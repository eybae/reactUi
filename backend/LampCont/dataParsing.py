import json
import base64
from datetime import datetime
import os

# 16진수 -> 10진수 변환용 dict
hex_to_dec = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15
}

def converted_value(hex_string):
    decimal = 0
    for i in range(len(hex_string)):
        decimal += hex_to_dec[hex_string[i]] * (16 ** (len(hex_string) - i - 1))
    return decimal

def encode(data_hex):
    return base64.b64encode(bytes.fromhex(data_hex)).decode()

# 디바이스에서 받은 base64 메시지를 dict로 파싱
def dataDecode(base64_message):    
    data = base64.b64decode(base64_message).hex()
    return {
        "mode": converted_value(data[0:2]),
        "cmd": converted_value(data[2:4]),
        "state": converted_value(data[4:6]),
        "dem": converted_value(data[6:8])
    }

# 로그 저장 함수 (오류 방지)
def log_device_data(device_name, dev_data):
    now = datetime.now()
    log_dir = os.path.join("logs", device_name, now.strftime("%Y"), now.strftime("%m"))
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{now.strftime('%d')}.log")
    log_line = (
        f"{now.strftime('%H:%M:%S')}, "
        f"mode: {dev_data.get('mode', '?')}, "
        f"cmd: {dev_data.get('cmd', '?')}, "
        f"state: {dev_data.get('state', '?')}, "
        f"dem: {dev_data.get('dem', '?')}\n"
    )
    with open(log_path, "a") as f:
        f.write(log_line)

# 최종적으로 json_payload를 파싱해 DB저장용 딕셔너리 반환
def deviceDataParsing(json_payload):
    devName = json_payload.get('deviceName', 'unknown')
    dev_data = {}

    if 'data' in json_payload:
        try:
            dev_data = dataDecode(json_payload['data'])
        except Exception as e:
            print(f"⚠️ dataDecode 오류: {e}")

    try:
        log_device_data(devName, dev_data)
    except Exception as e:
        print(f"⚠️ 로그 저장 오류: {e}")

    return dev_data

# 그룹 제어용 payload 생성 (mode, cmd, on/off, 밝기, 시간 포함)
def encode_group_payload(mode, cmd, state, dem, on_time, off_time):
    mode_byte = int(mode) & 0xFF
    cmd_byte = int(cmd) & 0xFF
    state_byte = 0x01 if state == "on" else 0x00
    dem_byte = max(1, min(int(dem), 5))

    def time_to_bytes(t):
        try:
            h, m = map(int, t.split(":"))
            return h & 0xFF, m & 0xFF
        except:
            return 0x00, 0x00

    on_h, on_m = time_to_bytes(on_time)
    off_h, off_m = time_to_bytes(off_time)

    return bytes([mode_byte, cmd_byte, state_byte, dem_byte, on_h, on_m, off_h, off_m])
