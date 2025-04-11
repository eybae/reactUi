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
    


    