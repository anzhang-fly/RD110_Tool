# import serial.tools.list_ports
#
# port_list = []
# port = serial.tools.list_ports.comports()
# for p in list(port):
#     port_list.append(p.device)
# print(port_list)

import serial
import threading
import time

# 定义串口配置列表，每个元素包括串口名和波特率
serial_configs = [
    ('COM1', 9600),
    ('COM2', 9600),
    ('COM3', 9600),
    ('COM4', 9600),
    ('COM5', 9600),
    ('COM6', 9600),
    ('COM7', 9600),
    ('COM8', 9600),
    ('COM9', 9600),
    ('COM10', 9600),
    ('COM11', 9600),
    ('COM12', 9600),
    ('COM13', 9600),
    ('COM14', 9600),
    ('COM15', 9600),
    ('COM16', 9600),
]

# 定义串口读取函数
def read_serial(ser):
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            print(f"Received from {ser.port}: {data}")

try:
    # 创建串口对象和线程列表
    serial_threads = []

    # 循环开启每个串口并创建对应的线程
    for port, baudrate in serial_configs:
        ser = serial.Serial(port, baudrate, timeout=1)
        thread = threading.Thread(target=read_serial, args=(ser,))
        serial_threads.append((ser, thread))
        thread.start()
        print(f"Opened {port} with baudrate {baudrate}")

    # 主线程可以继续执行其他任务
    while True:
        time.sleep(1)

except serial.SerialException as e:
    print(f"Serial port error: {e}")

finally:
    # 关闭所有串口
    for ser, thread in serial_threads:
        if ser.is_open:
            ser.close()
        thread.join()


import json
# 解析JSON字符串
json_string = '{"name": "Alice", "age": 25, "city": "New York"}'
data = json.loads(json_string)
print(data)
print(data['name'])
print(data['age'])

# 将Python对象转换为JSON字符串
data = {
    "name": "Bob",
    "age": 30,
    "city": "San Francisco"
}
json_string = json.dumps(data)
print(json_string)
