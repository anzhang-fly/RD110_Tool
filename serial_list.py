#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project:Factory_test 
@File:serial_list.py
@Author:rivern.yuan
@Date:2022/9/6 15:59 
"""

import time
import threading
import serial.tools.list_ports
from pubsub import pub


class SerialDetection(threading.Thread):
    """
    class for detection port list
    """
    def __init__(self):
        super(SerialDetection, self).__init__()
        self.serPort = serial.tools.list_ports
        self._exit = False

    def exit_event(self):
        self._exit = True

    def enter_event(self):
        self._exit = False

    # def get_com_number(self, vid_pid, location):
    #     port_list = []
    #     for p in list(self.serPort.comports()):
    #         if p.vid == int(vid_pid.split(":")[0], 16) and p.pid == int(vid_pid.split(":")[1], 16):
    #             if location in p.location:
    #                 port_list.append(p.device)
    #     return port_list

    def get_com_number(self, vid_pid):
        port_list = []
        for p in list(self.serPort.comports()):
            if p.vid == int(vid_pid.split(":")[0], 16) and p.pid == int(vid_pid.split(":")[1], 16):
                port_list.append(p.device)
        return port_list

    def run(self):
        serial_list = []
        while True:
            if self._exit:
                pass
            else:
                if serial_list == [] or serial_list != self.serPort.comports():
                    serial_list = self.serPort.comports()
                    # serial_port = self.get_com_number("0x2C7C:0x6005", "x.8")
                    # serial_port.extend(self.get_com_number("0x2C7C:0x6005", "x.5"))
                    serial_port = self.get_com_number("0x10C4:0xEA60")
                    sorted_serial_port = sorted(serial_port, key=lambda x: int(x[3:]))
                    # serial_port.extend(self.get_com_number("0x2C7C:0x6002"))
                    # serial_port.extend(self.get_com_number("0x2C7C:0x6005"))
                    print("设备列表为{}".format(sorted_serial_port))
                    pub.sendMessage('serialUpdate', arg1=sorted_serial_port)
            time.sleep(1)


# 定义一个类来处理每个串口的通信
class SerialPortThread(threading.Thread):
    def __init__(self, port, baudrate=115200, timeout=1):
        threading.Thread.__init__(self)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.running = True

    def run(self):
        # 打开串口
        data_list = []
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        print(f"Started thread for {self.port}")
        while self.running:
            # 读取数据
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode("utf-8").strip()
                # data = self.ser.read(self.ser.in_waiting)
                # data_list.append(data)
                # data_list.append(self.ser.port)
                # print([data, self.ser.port])
                pub.sendMessage('serialData', arg1=[data, self.ser.port])
            # 添加一些延时以避免CPU占用过高
            time.sleep(0.2)

    def send_data(self, data):
        if self.ser and self.ser.is_open:
            # self.ser.reset_input_buffer()
            # self.ser.reset_output_buffer()
            self.ser.write(data.encode("utf-8"))
            # self.ser.write(data)
            print(f"Sent to {self.port}: {data}")

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        print(f"Stopped thread for {self.port}")

    def begin(self):
        self.ser.open()
        print(f"begin thread for {self.port}")


# 定义主函数来初始化和控制所有串口
def main():
    ports = [f'COM{i}' for i in range(1, 8)]  # 假设有16个串口，名称为COM1到COM16
    threads = []

    # 创建并启动线程
    for port in ports:
        thread = SerialPortThread(port)
        thread.start()
        threads.append(thread)

    try:
        while True:
            # 示例：发送数据到所有串口
            for thread in threads:
                thread.send_data(b'A3000003F\r\n')
            time.sleep(5)  # 每5秒发送一次数据
    except KeyboardInterrupt:
        print("Stopping all threads...")
        for thread in threads:
            thread.stop()
        for thread in threads:
            thread.join()
        print("All threads stopped.")


if __name__ == '__main__':
    # ser = SerialDetection()
    # ser.setDaemon(False)
    # ser.start()
    main()


