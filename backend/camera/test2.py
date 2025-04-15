from serial import Serial

ser = Serial('/dev/ttyUSB0', 9600)
cmd = bytearray([0xFF, 0x00, 0x00, 0x04, 0x20, 0x00])
cmd.append(sum(cmd[1:]) % 256)
ser.write(cmd)



