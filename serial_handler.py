#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project:Factory_test 
@File:serial_handler.py
@Author:rivern.yuan
@Date:2022/9/6 15:03 
"""
import serial
import time
import asyncio


class SerialPort(object):
    '''
    class for serial operation
    '''
    def __init__(self, port, baud):
        self._port = port
        self._baud = baud
        self._conn = None

    def _open_conn(self):
        self._conn = serial.Serial(self._port, self._baud, parity=serial.PARITY_EVEN, timeout=1)
        return self._conn

    def _close_conn(self):
        self._conn.close()
        self._conn = None

    def _send_cmd(self, cmd):
        self._conn.write((cmd + '\r\n').encode())

    def _recv_cmd(self):
        time.sleep(.2)
        byte_n = self._conn.inWaiting()  # 返回接收缓存中的字节数
        if byte_n > 0:
            return self._conn.read(byte_n)  # 读取接收缓存中的字节

    def _test_conn(self):
        self._send_cmd("1")
        # recv: b'1\r\n1\r\n>>> ' 测试正常交互
        test_recv = self._recv_cmd()
        if test_recv:
            if len(test_recv) == 10:
                return True
            else:
                print(test_recv)
                raise SerialError(self._port, "串口持续输出中，请检查运行状态")
        else:
            raise SerialError(self._port, "串口堵塞，请检查串口连通性")


class SerialHandler(SerialPort):
    """write test script & read test result """
    def __init__(self, port, baud=115200):
        super(SerialHandler, self).__init__(port, baud)
        self.init()

    def write_module(self, source, py_cmd, filename="test.py"):
        # self._test_conn()

        self._conn.write(b"\x01")
        # 写入文件 f=open('/usr/test.py','wb')
        self._send_cmd("f=open('/usr/" + filename + "','wb')")   # ‘wb’:以二进制格式进行写入，而不是文本模式
        self._send_cmd("w=f.write")  # 将f.write（）方法赋值给w，意味着f.write（data）和w（data）是同样的操作
        while True:
            # 从source文件写入usr/test.py中
            time.sleep(.1)
            data = source.read(255)  # 从source中读取255字节的数据
            if not data:
                break
            else:
                # 将source中读取255字节的数据写入usr/test.py
                # repr()函数的作用是产生对象的“官方”字符串表示形式，通常用于调试和日志记录。对于二进制数据，
                # 这种表示形式能够清晰地显示数据的内容，并且可以直接复制粘贴到Python代码中使用。
                # data = b'\x48\x65\x6c\x6c\x6f\x20\x77\x6f\x72\x6c\x64'
                # repr(data)返回值为b'Hello world'
                # b'...' 表示这是一个 bytes 对象
                self._send_cmd("w(" + repr(data) + ")")
                self._conn.write(b"\x04")
        self._send_cmd("f.close()")
        self._conn.write(b"\x04")
        self._conn.write(b"\x02")
        self._conn.write(b"\x04")

        source.close()  # 关闭文件
        self.exec_cmd(py_cmd[0])
        return True

    def write_FactoryTestCmd(self, num):
        self._conn.write(("TEST"+str(num)).encode("utf-8"))

    def write_DeviceNum(self, DeviceNum):
        self._conn.write(DeviceNum.encode("utf-8"))

    def read_FromFactoryTest(self):
        start_time = time.time()
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > 10:
                data = ''
                break
            if self._conn.inWaiting() > 0:
                data = self._conn.read(self._conn.inWaiting()).decode("utf-8", errors="ignore")
                break
            time.sleep(0.5)
        return data

    def exec_py(self, cmd):
        self._send_cmd(cmd[0])
        self._conn.flushInput()
        self._send_cmd(cmd[1])
        time.sleep(1)
        return self.ret_result()

    def exec_cmd(self, cmd):
        self._send_cmd(cmd)

    async def run_cmd(self,source:list, log_text_ctrl):
        result_list = ""
        for i in source:
            self._send_cmd(i)
            await asyncio.sleep(.1)
            result_list += self.ret_result()
            log_text_ctrl.SetValue(result_list)
        return result_list

    def ret_result(self):
        data = ""
        for i in range(6):
            data += self._conn.read(self._conn.inWaiting()).decode("utf-8", errors="ignore")
            if data.endswith(">>> "):
                break
            time.sleep(0.5)
        return data

    def exit_test(self):
        self._close_conn()

    def init(self):
        self._open_conn()


class SerialError(Exception):
    '''
    exception for serial blocking connection
    '''
    def __init__(self, _port, _error):
        self._port = _port
        self._error = _error

    def __str__(self):
        return self._port + " " + self._error


if __name__ == '__main__':
    ser = SerialHandler("COM63")


