import serial
import time

try:
    ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
    print("✅ Serial 연결됨")

    # LEFT 명령
    cmd = b"\x81\x01\x06\x01\x03\x03\x01\x03\xFF"
    ser.write(cmd)
    print("▶️ LEFT 전송 완료")

    time.sleep(2)

    # STOP 명령
    stop = b"\x81\x01\x06\x01\x03\x03\x03\x03\xFF"
    ser.write(stop)
    print("⏹️ STOP 전송 완료")

except Exception as e:
    print("❌ Serial 오류:", e)
