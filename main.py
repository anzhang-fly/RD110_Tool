#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project:Factory_test
@File:serial_handler.py
@Author:rivern.yuan
@Date:2022/9/15 21:09
"""

import sys
import os
import time
import wx
import locale
import gettext
import asyncio
import datetime
import subprocess
import threading
import file_handler
import serial_list
import serial_handler
import configparser
from log_redirect import RedirectErr, RedirectStd
from pubsub import pub
from queue import Queue
import codecs
import json
import glob
import serial
import json

if hasattr(sys, '_MEIPASS'):
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

class FactoryFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)

        self.Serial_threads = []
        self.Recieve_data = []
        self.nongdu_g = ''
        self.port_g = ''
        self.select1 = ["0", "5000", "1%", "3%", "8%", "12%", "20%"]
        self.select2 = ["20%", "30%", "50%", "80%", "100%"]

        # self.SetSize((1120, 650))
        self.SetSize((1500, 1000))
        self.Center()

        self.main_panel = wx.Panel(self, wx.ID_ANY)

        self.SelectStatictext1 = wx.StaticText(self.main_panel, label='低浓度标定')
        self.SelectStatictext2 = wx.StaticText(self.main_panel, label='高浓度标定')

        self.close = wx.RadioButton(self.main_panel, wx.ID_ANY, ("关闭端口"))
        self.Bind(wx.EVT_BUTTON, self.close_com, self.close)

        self.open = wx.RadioButton(self.main_panel, wx.ID_ANY, ("打开端口"))
        self.Bind(wx.EVT_BUTTON, self.open_com, self.open)

        self.mode = wx.Button(self.main_panel, wx.ID_ANY, ("模式切换"))
        self.Bind(wx.EVT_BUTTON, self.switch_mode, self.mode)

        self.BD_DATA = wx.Button(self.main_panel, wx.ID_ANY, ("标定数据"))

        self.BD_RESULT = wx.Button(self.main_panel, wx.ID_ANY, ("标定结果"))

        self.RECORD_DATA = wx.Button(self.main_panel, wx.ID_ANY, ("记录数值"))

        self.NIHE = wx.Button(self.main_panel, wx.ID_ANY, ("拟合"))

        self.WRITE_XISHU = wx.Button(self.main_panel, wx.ID_ANY, ("写入系数"))

        self.READ_XISHU = wx.Button(self.main_panel, wx.ID_ANY, ("读取系数"))

        self.cb1 = wx.ComboBox(self.main_panel,wx.ID_ANY, choices=self.select1, style=wx.CB_READONLY)
        self.cb1.SetSelection(0)
        self.cb1.Bind(wx.EVT_COMBOBOX, self.OnSelect1)

        self.cb2 = wx.ComboBox(self.main_panel, wx.ID_ANY, choices=self.select2, style=wx.CB_READONLY)
        self.cb2.SetSelection(0)
        self.cb1.Bind(wx.EVT_COMBOBOX, self.OnSelect2)

        # 实时数据显示
        self.ListCtrl = wx.ListCtrl(self.main_panel, -1, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.ListCtrl.SetMinSize((360, 400))
        # 在报表视图模式向列表添加新列
        self.ListCtrl.AppendColumn((u"端口"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl.AppendColumn((u"浓度"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl.AppendColumn((u"波长"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl.AppendColumn((u"光强"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl.AppendColumn((u"温度"), format=wx.LIST_FORMAT_CENTER, width=70)

        # 低浓度标定数据
        self.ListCtrl1 = wx.ListCtrl(self.main_panel, -1, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.ListCtrl1.SetMinSize((495, 400))
        # 在报表视图模式向列表添加新列
        self.ListCtrl1.AppendColumn((u"0"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"5000"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"1%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"3%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"8%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"12%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"20%"), format=wx.LIST_FORMAT_CENTER, width=70)

        # 高浓度标定数据
        self.ListCtrl2 = wx.ListCtrl(self.main_panel, -1,style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.ListCtrl2.SetMinSize((355, 400))
        # 在报表视图模式向列表添加新列
        self.ListCtrl2.AppendColumn((u"20%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl2.AppendColumn((u"30%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl2.AppendColumn((u"50%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl2.AppendColumn((u"80%"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl2.AppendColumn((u"100%"), format=wx.LIST_FORMAT_CENTER, width=70)

        # event message queue
        self.message_queue = Queue(maxsize=10)  # 创建一个队列，队列最大容量10个项目
        self._channel_list = []

        # 开启port_process_handler线程
        threading.Thread(target=self.port_process_handler, args=()).start()

        # serialUpdate主题传过来的数据是serial_port，serial_port是一个列表，列表内容是所有端口号
        pub.subscribe(self.port_update, "serialUpdate")
        # serialdata主题传过来的数据是data_list，data_list为json格式，数据内容是一个列表，data_list[0]为串口接受的收据，data_list[1]对应的串口号
        pub.subscribe(self.port_recieve_data, "serialData")

        # 页面布局管理
        self.__do_layout()


    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("按钮")), wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("")), wx.HORIZONTAL)

        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("选择")), wx.HORIZONTAL)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("实时数据")), wx.HORIZONTAL)
        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("低标")), wx.HORIZONTAL)
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("高标")), wx.HORIZONTAL)

        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.close, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.open, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.mode, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.BD_DATA, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.BD_RESULT, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.RECORD_DATA, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.NIHE, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.WRITE_XISHU, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.READ_XISHU, 0, 0, 0)

        sizer_5.Add(self.ListCtrl, 0, 0, 0)
        sizer_6.Add(self.ListCtrl1, 0, 0, 0)
        sizer_7.Add(self.ListCtrl2, 0, 0, 0)

        sizer_4.Add(sizer_5, 0, 0, 0)
        sizer_4.Add(sizer_6, 0, 0, 0)
        sizer_4.Add(sizer_7, 0, 0, 0)

        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.SelectStatictext1, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.cb1, 0, 0, 0)
        sizer_8.Add((20, 0), 0, 0, 0)
        sizer_8.Add(self.SelectStatictext2, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.cb2, 0, 0, 0)

        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_2.Add((10, 10), 0, 0, 0)
        sizer_2.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_2.Add((10, 10), 0, 0, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)

        self.main_panel.SetSizer(sizer_2)
        sizer_1.Add(self.main_panel, 1, wx.EXPAND | wx.TOP, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # sizer_5.SetLabel(_("测试中"))


    def close_com(self, event):
        print("Stopping all threads...")
        for thread in self.Serial_threads:
            thread.stop()
        for thread in self.Serial_threads:
            thread.join()
        print("All threads stopped.")
        self.Serial_threads.clear()

    def open_com(self, event):
        print("opening all threads...")
        for port in self._channel_list:
            serial_thread = serial_list.SerialPortThread(port)
            serial_thread.start()
            self.Serial_threads.append(serial_thread)
            print(f"Opened {port}")
        print("All threads opened.")

    def switch_mode(self, event):
        for thread in self.Serial_threads:
            thread.send_data('A3000003F')

    def OnSelect1(self, e):
        select1 = e.GetString()
        if select1 == "0":
            self.fill_low_data(0)
        if select1 == "5000":
            self.fill_low_data(1)
        if select1 == "1%":
            self.fill_low_data(2)
        if select1 == "3%":
            self.fill_low_data(3)
        if select1 == "8%":
            self.fill_low_data(4)
        if select1 == "12%":
            self.fill_low_data(5)
        if select1 == "20%":
            self.fill_low_data(6)

    def fill_low_data(self, i):
        if self.port_g == 'COM1':
            self.ListCtrl1.SetItem(0, i, self.nongdu_g)
        if self.port_g == 'COM2':
            self.ListCtrl1.SetItem(1, i, self.nongdu_g)
        if self.port_g == 'COM3':
            self.ListCtrl1.SetItem(2, i, self.nongdu_g)
        if self.port_g == 'COM4':
            self.ListCtrl1.SetItem(3, i, self.nongdu_g)
        if self.port_g == 'COM5':
            self.ListCtrl1.SetItem(4, i, self.nongdu_g)
        if self.port_g == 'COM6':
            self.ListCtrl1.SetItem(5, i, self.nongdu_g)
        if self.port_g == 'COM7':
            self.ListCtrl1.SetItem(6, i, self.nongdu_g)
        if self.port_g == 'COM8':
            self.ListCtrl1.SetItem(7, i, self.nongdu_g)
        if self.port_g == 'COM9':
            self.ListCtrl1.SetItem(8, i, self.nongdu_g)
        if self.port_g == 'COM10':
            self.ListCtrl1.SetItem(9, i, self.nongdu_g)
        if self.port_g == 'COM11':
            self.ListCtrl1.SetItem(10, i, self.nongdu_g)
        if self.port_g == 'COM12':
            self.ListCtrl1.SetItem(11, i, self.nongdu_g)
        if self.port_g == 'COM13':
            self.ListCtrl1.SetItem(12, i, self.nongdu_g)
        if self.port_g == 'COM14':
            self.ListCtrl1.SetItem(13, i, self.nongdu_g)
        if self.port_g == 'COM15':
            self.ListCtrl1.SetItem(14, i, self.nongdu_g)
        if self.port_g == 'COM16':
            self.ListCtrl1.SetItem(15, i, self.nongdu_g)


    def OnSelect2(self, e):
        select2 = e.GetString()
        if select2 == "2%0":
            self.fill_high_data(0)
        if select2 == "30%":
            self.fill_high_data(1)
        if select2 == "50%":
            self.fill_high_data(2)
        if select2 == "80%":
            self.fill_high_data(3)
        if select2 == "100%":
            self.fill_high_data(4)

    def fill_high_data(self, i):
        if self.port_g == 'COM1':
            self.ListCtrl2.SetItem(0, i, self.nongdu_g)
        if self.port_g == 'COM2':
            self.ListCtrl2.SetItem(1, i, self.nongdu_g)
        if self.port_g == 'COM3':
            self.ListCtrl2.SetItem(2, i, self.nongdu_g)
        if self.port_g == 'COM4':
            self.ListCtrl2.SetItem(3, i, self.nongdu_g)
        if self.port_g == 'COM5':
            self.ListCtrl2.SetItem(4, i, self.nongdu_g)
        if self.port_g == 'COM6':
            self.ListCtrl2.SetItem(5, i, self.nongdu_g)
        if self.port_g == 'COM7':
            self.ListCtrl2.SetItem(6, i, self.nongdu_g)
        if self.port_g == 'COM8':
            self.ListCtrl2.SetItem(7, i, self.nongdu_g)
        if self.port_g == 'COM9':
            self.ListCtrl2.SetItem(8, i, self.nongdu_g)
        if self.port_g == 'COM10':
            self.ListCtrl2.SetItem(9, i, self.nongdu_g)
        if self.port_g == 'COM11':
            self.ListCtrl2.SetItem(10, i, self.nongdu_g)
        if self.port_g == 'COM12':
            self.ListCtrl2.SetItem(11, i, self.nongdu_g)
        if self.port_g == 'COM13':
            self.ListCtrl2.SetItem(12, i, self.nongdu_g)
        if self.port_g == 'COM14':
            self.ListCtrl2.SetItem(13, i, self.nongdu_g)
        if self.port_g == 'COM15':
            self.ListCtrl2.SetItem(14, i, self.nongdu_g)
        if self.port_g == 'COM16':
            self.ListCtrl2.SetItem(15, i, self.nongdu_g)

    def port_update(self, arg1):
        print("message:{}".format(arg1))
        self.message_queue.put({"msg_id": "PortUpdate", "PortInfo": arg1})

    def port_recieve_data(self, arg1):

        print("recieve data:{}".format(arg1))
        json_string = arg1[0]
        data = json.loads(json_string)
        data_list = data['REPLY']['DATA']

        nongdu = str(data_list[1])
        wavelength = str(data_list[2])
        guangqiang = str(data_list[3])
        wendu = str(data_list[4])

        self.port_g = arg1[1]
        self.nongdu_g = nongdu

        if arg1[1] == 'COM1':
            self.ListCtrl.SetItem(0, 1, nongdu)
            self.ListCtrl.SetItem(0, 2, wavelength)
            self.ListCtrl.SetItem(0, 3, guangqiang)
            self.ListCtrl.SetItem(0, 4, wendu)
        elif arg1[1] == 'COM2':
            self.ListCtrl.SetItem(1, 1, nongdu)
            self.ListCtrl.SetItem(1, 2, wavelength)
            self.ListCtrl.SetItem(1, 3, guangqiang)
            self.ListCtrl.SetItem(1, 4, wendu)
        elif arg1[1] == 'COM3':
            self.ListCtrl.SetItem(2, 1, nongdu)
            self.ListCtrl.SetItem(2, 2, wavelength)
            self.ListCtrl.SetItem(2, 3, guangqiang)
            self.ListCtrl.SetItem(2, 4, wendu)
        elif arg1[1] == 'COM4':
            self.ListCtrl.SetItem(3, 1, nongdu)
            self.ListCtrl.SetItem(3, 2, wavelength)
            self.ListCtrl.SetItem(3, 3, guangqiang)
            self.ListCtrl.SetItem(3, 4, wendu)
        elif arg1[1] == 'COM5':
            self.ListCtrl.SetItem(4, 1, nongdu)
            self.ListCtrl.SetItem(4, 2, wavelength)
            self.ListCtrl.SetItem(4, 3, guangqiang)
            self.ListCtrl.SetItem(1, 4, wendu)
        elif arg1[1] == 'COM6':
            self.ListCtrl.SetItem(5, 1, nongdu)
            self.ListCtrl.SetItem(5, 2, wavelength)
            self.ListCtrl.SetItem(5, 3, guangqiang)
            self.ListCtrl.SetItem(5, 4, wendu)
        elif arg1[1] == 'COM7':
            self.ListCtrl.SetItem(6, 1, nongdu)
            self.ListCtrl.SetItem(6, 2, wavelength)
            self.ListCtrl.SetItem(6, 3, guangqiang)
            self.ListCtrl.SetItem(6, 4, wendu)
        elif arg1[1] == 'COM8':
            self.ListCtrl.SetItem(7, 1, nongdu)
            self.ListCtrl.SetItem(7, 2, wavelength)
            self.ListCtrl.SetItem(7, 3, guangqiang)
            self.ListCtrl.SetItem(7, 4, wendu)
        elif arg1[1] == 'COM9':
            self.ListCtrl.SetItem(8, 1, nongdu)
            self.ListCtrl.SetItem(8, 2, wavelength)
            self.ListCtrl.SetItem(8, 3, guangqiang)
            self.ListCtrl.SetItem(8, 4, wendu)
        if arg1[1] == 'COM10':
            self.ListCtrl.SetItem(9, 1, nongdu)
            self.ListCtrl.SetItem(9, 2, wavelength)
            self.ListCtrl.SetItem(9, 3, guangqiang)
            self.ListCtrl.SetItem(9, 4, wendu)
        elif arg1[1] == 'COM11':
            self.ListCtrl.SetItem(10, 1, nongdu)
            self.ListCtrl.SetItem(10, 2, wavelength)
            self.ListCtrl.SetItem(10, 3, guangqiang)
            self.ListCtrl.SetItem(10, 4, wendu)
        elif arg1[1] == 'COM12':
            self.ListCtrl.SetItem(11, 1, nongdu)
            self.ListCtrl.SetItem(11, 2, wavelength)
            self.ListCtrl.SetItem(11, 3, guangqiang)
            self.ListCtrl.SetItem(11, 4, wendu)
        elif arg1[1] == 'COM13':
            self.ListCtrl.SetItem(12, 1, nongdu)
            self.ListCtrl.SetItem(12, 2, wavelength)
            self.ListCtrl.SetItem(12, 3, guangqiang)
            self.ListCtrl.SetItem(12, 4, wendu)
        elif arg1[1] == 'COM14':
            self.ListCtrl.SetItem(13, 1, nongdu)
            self.ListCtrl.SetItem(13, 2, wavelength)
            self.ListCtrl.SetItem(13, 3, guangqiang)
            self.ListCtrl.SetItem(13, 4, wendu)
        elif arg1[1] == 'COM15':
            self.ListCtrl.SetItem(14, 1, nongdu)
            self.ListCtrl.SetItem(14, 2, wavelength)
            self.ListCtrl.SetItem(14, 3, guangqiang)
            self.ListCtrl.SetItem(14, 4, wendu)
        elif arg1[1] == 'COM16':
            self.ListCtrl.SetItem(15, 1, nongdu)
            self.ListCtrl.SetItem(15, 2, wavelength)
            self.ListCtrl.SetItem(15, 3, guangqiang)
            self.ListCtrl.SetItem(15, 4, wendu)

    def port_update_handler(self, arg1):
        # TODO 设置log按钮状态
        port_list = arg1["PortInfo"][:16] if len(arg1["PortInfo"]) > 16 else arg1["PortInfo"]  # 类似于C语言的三目运算符
        if len(port_list) < 16:
            port_list = port_list + [""] * (16 - len(port_list))
        if self._channel_list == [] or self._channel_list != port_list:
            self._channel_list = port_list

            self.ListCtrl.DeleteAllItems()

            for i, element in enumerate(self._channel_list):
                self.ListCtrl.InsertItem(i, i)
                self.ListCtrl1.InsertItem(i, i)
                self.ListCtrl2.InsertItem(i, i)

                self.ListCtrl.SetItem(i, 0, element)
                self.ListCtrl.SetItem(i, 1, "")
                self.ListCtrl.SetItem(i, 2, "")
                self.ListCtrl.SetItem(i, 3, "")
                self.ListCtrl.SetItem(i, 4, "")
                self.ListCtrl.SetItemBackgroundColour(i, (255,255,255))
        self.message_queue.put({"msg_id": "PortTest"})

    def port_test_handler(self):
        print("start test")
        try:
            # 循环开启每个串口并创建对应的线程
            for port in self._channel_list:
                if port != '':
                    serial_thread = serial_list.SerialPortThread(port)
                    serial_thread.start()
                    self.Serial_threads.append(serial_thread)
                    print(f"Opened {port}")
        except Exception as e:
            wx.MessageBox("串口异常，测试脚本写入失败, error %s"%str(e), u'Error', wx.YES_DEFAULT | wx.ICON_INFORMATION)

    def port_process_handler(self):
        while True:
            try:
                message = self.message_queue.get(True, 5)  # Block = True, timeout=5, 表示队列中无数据可取时，阻塞5s，抛出empty异常
            except Exception as e:
                message = None  # 异常提示
            try:
                if message:
                    # print("message:{}".format(message))
                    msg_id = message.get("msg_id")
                    if msg_id == "exit":
                        pass
                    elif msg_id == "PortUpdate":
                        # threading.Thread(target=self.port_update_handler, args=(message,)).start()
                        self.port_update_handler(message)
                    elif msg_id == "PortTest":
                        # threading.Thread(target=self.port_test_handler, args=(message,)).start()
                        self.port_test_handler()
                    else:
                        pass
            except Exception as e:
                print(e)

    @staticmethod
    def __port_det(flag):
        if flag:
            tSerialDet.exit_event()
        else:
            tSerialDet.enter_event()

    # end of class FactoryFrame
    def close_window(self, event):
        self.Destroy()
        time.sleep(0.2)
        wx.GetApp().ExitMainLoop()
        wx.Exit()
        process_name = "taskkill /F /IM " + file_name
        p = subprocess.Popen(process_name, shell=True)

class MyApp(wx.App):
    languageTab = locale.getdefaultlocale()[0]
    print("languageTab: ", languageTab)
    # languageTab = "en"
    # 根据系统语言自动设置语言
    if languageTab == "zh_CN":
        t = gettext.translation('Chinese', PROJECT_ABSOLUTE_PATH + "\\locale", languages=["zh_CN"])
        t.install()
    elif languageTab == "en":
        t = gettext.translation('English', PROJECT_ABSOLUTE_PATH + "\\locale", languages=["en"])
        t.install()
    else:
        languageTab = "en"
        t = gettext.translation('English', PROJECT_ABSOLUTE_PATH + "\\locale", languages=["en"])
        t.install()

    def __init__(self):
        # print("init-----")
        wx.App.__init__(self, redirect=False, filename="", useBestVisual=True, clearSigInt=True)

    def OnInit(self):
        self.factory_frame = FactoryFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.factory_frame)
        self.factory_frame.Show()

        # 串口检测线程
        global tSerialDet
        tSerialDet = serial_list.SerialDetection()  # SerialDetection继承自threading.Thread
        tSerialDet.setDaemon(True)  # 设置为守护线程，当主线程结束时，子线程全部结束
        tSerialDet.start()

        return True


if __name__ == "__main__":
    file_name = os.path.basename(sys.executable)  #  file_name = python.exe
    app = MyApp()
    app.MainLoop()