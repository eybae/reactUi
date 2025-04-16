# python 3.11

import json
import base64, binascii, codecs
from datetime import timedelta, date, datetime
import csv
import os

# hexa decimal to decimal converter
dict = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
def converted_value(hexadecimal):
    decimal = 0
    for i in range(len(hexadecimal)):
        decimal += dict[hexadecimal[i]] * (16**(len(hexadecimal) - i -1))
    return decimal

def encode(data):     
    base64_message = base64.b64encode(bytes.fromhex(data)).decode()
    return base64_message

# received data parsing --> dictionary
def dataDecode(base64_message):    
    devData = {"mode" : 0,
                 "cmd" : 0,                 
                 "state" : 0,
                 "dem" : 0}
    nowTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = base64.b64decode(base64_message).hex()  
    #devData['time'] = nowTime
    devData['mode'] = converted_value(data[0:2])
    devData['cmd'] = converted_value(data[2:4])
    devData['state'] = converted_value(data[4:6])    
    devData['dem'] = converted_value(data[6:8])
    return devData	
 
def log_device_data(device_name, dev_data):
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    time_str = now.strftime("%H:%M:%S")

    # logs/dev2/2025/04/11.log
    log_dir = os.path.join("logs", device_name, year, month)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{day}.log")

    log_line = f"{time_str}, mode: {dev_data['mode']}, cmd: {dev_data['cmd']}, state: {dev_data['state']}, dem: {dev_data['dem']}\n"

    with open(log_path, "a") as f:
        f.write(log_line)
          
# device data parsing for db saving
def deviceDataParsing(json_payload):
    devName = json_payload.get('deviceName', 'unknown')
    
    dev_data = {}  # 기본값 선언 (예: 비어있는 dict)

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

    on_h, on_m = map(int, on_time.split(":"))
    off_h, off_m = map(int, off_time.split(":"))
    
    #state_val = 1 if state == 'on' else 0

    return bytes([mode_byte, cmd_byte, state_byte, dem_byte, on_h, on_m, off_h, off_m])

    


    