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
import numpy as np

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

        self.comx_nongdu = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # 标气浓度数组
        self.Std_nongdu_l = [0, 5000, 10000, 30000, 80000, 120000, 200000]
        self.Std_nongdu_h = [200000, 300000, 500000, 800000, 1000000]
        # 低浓度数组
        self.data_0 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_8 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_12 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_20 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # 高浓度数组
        self.data_20_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_30 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_50 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_80 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_100 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.fit_coefficients_matrix_l = np.zeros((16, 4))  # 存放低浓度拟合系数的二维数组
        self.fit_coefficients_matrix_h = np.zeros((16, 4))  # 存放低浓度拟合系数的二维数组

        self.nongdu_g = ''
        self.port_g = ''
        self.select1 = ["N2", "0.5%", "1%", "3%", "8%", "12%", "20%"]
        self.select2 = ["20%", "30%", "50%", "80%", "100%"]

        self.SetSize((1500, 800))
        self.Center()

        self.main_panel = wx.Panel(self, wx.ID_ANY)

        self.SelectStatictext1 = wx.StaticText(self.main_panel, label='浓度选择')
        self.SelectStatictext2 = wx.StaticText(self.main_panel, label='浓度选择')

        # self.close = wx.Button(self.main_panel, wx.ID_ANY, ("关闭端口"))
        # self.Bind(wx.EVT_BUTTON, self.close_com, self.close)

        # self.open = wx.Button(self.main_panel, wx.ID_ANY, ("打开端口"))
        # self.Bind(wx.EVT_BUTTON, self.open_com, self.open)

        self.OPEN = wx.RadioButton(self.main_panel, wx.ID_ANY, ("打开端口"))
        self.Bind(wx.EVT_RADIOBUTTON, self.open_com, self.OPEN)

        self.CLOSE = wx.RadioButton(self.main_panel, wx.ID_ANY, ("关闭端口"))
        self.Bind(wx.EVT_RADIOBUTTON, self.close_com, self.CLOSE)

        self.OPEN.SetValue(True)

        self.MODE = wx.Button(self.main_panel, wx.ID_ANY, ("低标模式"))
        self.Bind(wx.EVT_BUTTON, self.switch_mode, self.MODE)

        self.HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("高标模式"))
        self.Bind(wx.EVT_BUTTON, self.High_model, self.HIGH)

        self.RECORD_DATA_LOW = wx.Button(self.main_panel, wx.ID_ANY, ("低标数值记录"))
        self.Bind(wx.EVT_BUTTON, self.RECORD_DATA_LOW_OP, self.RECORD_DATA_LOW)

        self.RECORD_DATA_HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("高标数值记录"))
        self.Bind(wx.EVT_BUTTON, self.RECORD_DATA_HIGH_OP, self.RECORD_DATA_HIGH)

        self.BD_DATA_LOW = wx.Button(self.main_panel, wx.ID_ANY, ("低标数据"))
        self.Bind(wx.EVT_BUTTON, self.BD_DATA_LOW_OP, self.BD_DATA_LOW)

        self.BD_RESULT_LOW = wx.Button(self.main_panel, wx.ID_ANY, ("低标结果"))

        self.BD_DATA_HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("高标数据"))
        self.Bind(wx.EVT_BUTTON, self.BD_DATA_HIGH_OP, self.BD_DATA_HIGH)

        self.BD_RESULT_HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("高标结果"))

        self.NIHE_LOW = wx.Button(self.main_panel, wx.ID_ANY, ("低标拟合"))
        self.Bind(wx.EVT_BUTTON, self.NIHE_LOW_OP, self.NIHE_LOW)

        self.NIHE_HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("高标拟合"))
        self.Bind(wx.EVT_BUTTON, self.NIHE_HIGH_OP, self.NIHE_HIGH)

        self.WRITE_XISHU_LOW = wx.Button(self.main_panel, wx.ID_ANY, ("写入低标系数"))

        self.WRITE_XISHU_HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("写入高标系数"))

        self.READ_XISHU_LOW = wx.Button(self.main_panel, wx.ID_ANY, ("读取低标系数"))

        self.READ_XISHU_HIGH = wx.Button(self.main_panel, wx.ID_ANY, ("读取高标系数"))

        self.cb1 = wx.ComboBox(self.main_panel, wx.ID_ANY, choices=self.select1, style=wx.CB_READONLY)
        self.cb1.SetSelection(0)
        self.cb1.Bind(wx.EVT_COMBOBOX, self.OnSelect1)

        self.cb2 = wx.ComboBox(self.main_panel, wx.ID_ANY, choices=self.select2, style=wx.CB_READONLY)
        self.cb2.SetSelection(0)
        self.cb2.Bind(wx.EVT_COMBOBOX, self.OnSelect2)

        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer1, self.timer1)
        self.is_running1 = False

        self.timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer2, self.timer2)
        self.is_running2 = False

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
        self.ListCtrl1.AppendColumn((u"N2"), format=wx.LIST_FORMAT_CENTER, width=70)
        self.ListCtrl1.AppendColumn((u"0.5%"), format=wx.LIST_FORMAT_CENTER, width=70)
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

        self.ListCtrl3 = wx.ListCtrl(self.main_panel, -1, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.ListCtrl3.SetMinSize((80, 400))
        # 在报表视图模式向列表添加新列
        self.ListCtrl3.AppendColumn((u"均值"), format=wx.LIST_FORMAT_CENTER, width=70)

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
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("低标按钮")), wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("")), wx.HORIZONTAL)

        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("高标按钮")), wx.HORIZONTAL)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("实时数据")), wx.HORIZONTAL)
        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("低标")), wx.HORIZONTAL)
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("高标")), wx.HORIZONTAL)
        sizer_9 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, ("记录数值")), wx.HORIZONTAL)

        sizer_3.Add(self.SelectStatictext1, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.cb1, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.MODE, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.RECORD_DATA_LOW, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.BD_DATA_LOW, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.BD_RESULT_LOW, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.NIHE_LOW, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.WRITE_XISHU_LOW, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.READ_XISHU_LOW, 0, 0, 0)
        sizer_3.Add((50, 0), 0, 0, 0)
        sizer_3.Add(self.OPEN, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)
        sizer_3.Add(self.CLOSE, 0, 0, 0)
        sizer_3.Add((10, 0), 0, 0, 0)

        sizer_8.Add(self.SelectStatictext2, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.cb2, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.HIGH, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.RECORD_DATA_HIGH, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.BD_DATA_HIGH, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.BD_RESULT_HIGH, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.NIHE_HIGH, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.WRITE_XISHU_HIGH, 0, 0, 0)
        sizer_8.Add((10, 0), 0, 0, 0)
        sizer_8.Add(self.READ_XISHU_HIGH, 0, 0, 0)

        sizer_5.Add(self.ListCtrl, 0, 0, 0)
        sizer_6.Add(self.ListCtrl1, 0, 0, 0)
        sizer_7.Add(self.ListCtrl2, 0, 0, 0)
        sizer_9.Add(self.ListCtrl3, 0, 0, 0)

        sizer_4.Add(sizer_5, 0, 0, 0)
        sizer_4.Add(sizer_6, 0, 0, 0)
        sizer_4.Add(sizer_7, 0, 0, 0)
        sizer_4.Add(sizer_9, 0, 0, 0)

        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_2.Add((10, 10), 0, 0, 0)
        sizer_2.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_2.Add((10, 10), 0, 0, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)

        self.main_panel.SetSizer(sizer_2)
        sizer_1.Add(self.main_panel, 1, wx.EXPAND | wx.TOP, 0)
        self.SetSizer(sizer_1)
        self.Layout()

    def close_com(self, event):
        print("Stopping all threads...")
        for thread in self.Serial_threads:
            if thread != "":
                thread.stop()
        for thread in self.Serial_threads:
            if thread != "":
                thread.join()
        print("All threads stopped.")
        self.Serial_threads.clear()

    def open_com(self, event):
        print("opening all threads...")
        for port in self._channel_list:
            if 'COM' in port:
                serial_thread = serial_list.SerialPortThread(port)
                serial_thread.start()
                self.Serial_threads.append(serial_thread)
                print(f"Opened {port}")
        print("All threads opened.")

    def switch_mode(self, event):
        for thread in self.Serial_threads:
            thread.send_data('A3000003F\r\n')

    def High_model(self, event):
        for thread in self.Serial_threads:
            thread.send_data('A9000009F\r\n')

    def RECORD_DATA_LOW_OP(self, event):
        low_nongdu_select = self.cb1.GetStringSelection()
        print("按下低浓度记录数据按钮", low_nongdu_select)

        if low_nongdu_select == 'N2':
            for i in range(16):
                self.data_0[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_0[i])
        if low_nongdu_select == '0.5%':
            for i in range(16):
                self.data_05[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_05[i])
        if low_nongdu_select == '1%':
            for i in range(16):
                self.data_1[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_1[i])
        if low_nongdu_select == '3%':
            for i in range(16):
                self.data_3[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_3[i])
        if low_nongdu_select == '8%':
            for i in range(16):
                self.data_8[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_8[i])
        if low_nongdu_select == '12%':
            for i in range(16):
                self.data_12[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_12[i])
        if low_nongdu_select == '20%':
            for i in range(16):
                self.data_20[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, self.data_20[i])

    def RECORD_DATA_HIGH_OP(self, event):
        high_nongdu_select = self.cb2.GetStringSelection()
        if high_nongdu_select == '20%':
            for i in range(16):
                self.data_20_1[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, str(self.data_20_1[i]))
        if high_nongdu_select == '30%':
            for i in range(16):
                self.data_30[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, str(self.data_30[i]))
        if high_nongdu_select == '50%':
            for i in range(16):
                self.data_50[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, str(self.data_50[i]))
        if high_nongdu_select == '80%':
            for i in range(16):
                self.data_80[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, str(self.data_80[i]))
        if high_nongdu_select == '100%':
            for i in range(16):
                self.data_100[i] = self.comx_nongdu[i]
                self.ListCtrl3.SetItem(i, 0, str(self.data_100[i]))

    def BD_DATA_LOW_OP(self, event):
        self.timer1.Stop()
        self.timer2.Stop()
        self.is_running1 = False
        self.is_running2 = False
        for i in range(16):
            self.ListCtrl1.SetItem(i, 0, str(self.data_0[i]))
            self.ListCtrl1.SetItem(i, 1, str(self.data_05[i]))
            self.ListCtrl1.SetItem(i, 2, str(self.data_1[i]))
            self.ListCtrl1.SetItem(i, 3, str(self.data_3[i]))
            self.ListCtrl1.SetItem(i, 4, str(self.data_8[i]))
            self.ListCtrl1.SetItem(i, 5, str(self.data_12[i]))
            self.ListCtrl1.SetItem(i, 6, str(self.data_20[i]))

    def BD_DATA_HIGH_OP(self, event):
        self.timer1.Stop()
        self.timer2.Stop()
        self.is_running1 = False
        self.is_running2 = False
        for i in range(16):
            self.ListCtrl2.SetItem(i, 0, str(self.data_20_1[i]))
            self.ListCtrl2.SetItem(i, 1, str(self.data_30[i]))
            self.ListCtrl2.SetItem(i, 2, str(self.data_50[i]))
            self.ListCtrl2.SetItem(i, 3, str(self.data_80[i]))
            self.ListCtrl2.SetItem(i, 4, str(self.data_100[i]))

    def NIHE_LOW_OP(self, event):

        # print(self.data_0)
        # print(self.data_05)
        # print(self.data_1)
        # print(self.data_3)
        # print(self.data_8)
        # print(self.data_12)
        # print(self.data_20)

        y = np.array(self.Std_nongdu_l)
        com_matrix = np.zeros((16, 7))  # 存放用于拟合的原始数据
        for i in range(16):
            com_matrix[i][0] = self.data_0[i]
            com_matrix[i][1] = self.data_05[i]
            com_matrix[i][2] = self.data_1[i]
            com_matrix[i][3] = self.data_3[i]
            com_matrix[i][4] = self.data_8[i]
            com_matrix[i][5] = self.data_12[i]
            com_matrix[i][6] = self.data_20[i]

        for i in range(16):
            self.fit_coefficients_matrix_l[i] = np.polyfit(com_matrix[i], y, 3)
        print(self.fit_coefficients_matrix_l)

    def NIHE_HIGH_OP(self, event):

        # print(self.data_20)
        # print(self.data_30)
        # print(self.data_50)
        # print(self.data_80)
        # print(self.data_100)

        y = np.array(self.Std_nongdu_h)
        com_matrix = np.zeros((16, 7))  # 存放用于拟合的原始数据
        for i in range(16):
            com_matrix[i][0] = self.data_20[i]
            com_matrix[i][1] = self.data_30[i]
            com_matrix[i][2] = self.data_50[i]
            com_matrix[i][3] = self.data_80[i]
            com_matrix[i][4] = self.data_100[i]

        for i in range(16):
            self.fit_coefficients_matrix_h[i] = np.polyfit(com_matrix[i], y, 3)
        print(self.fit_coefficients_matrix_h)

    def OnSelect1(self, event):
        if not self.is_running1:
            self.timer2.Stop()
            self.is_running2 = False
            self.is_running1 = True
            self.timer1.Start(10)  # 每10毫秒触发一次

    def on_timer1(self, event):
        select1 = self.cb1.GetStringSelection()
        # print(f'You selected: {select1}')
        # 这里可以添加其他需要重复执行的代码
        if select1 == "N2":
            self.fill_low_data(0)
        elif select1 == "0.5%":
            self.fill_low_data(1)
        elif select1 == "1%":
            self.fill_low_data(2)
        elif select1 == "3%":
            self.fill_low_data(3)
        elif select1 == "8%":
            self.fill_low_data(4)
        elif select1 == "12%":
            self.fill_low_data(5)
        elif select1 == "20%":
            self.fill_low_data(6)

    def fill_low_data(self, i):
        if self.port_g == 'COM1':
            self.ListCtrl1.SetItem(0, i, self.nongdu_g)
        elif self.port_g == 'COM2':
            self.ListCtrl1.SetItem(1, i, self.nongdu_g)
        elif self.port_g == 'COM3':
            self.ListCtrl1.SetItem(2, i, self.nongdu_g)
        elif self.port_g == 'COM4':
            self.ListCtrl1.SetItem(3, i, self.nongdu_g)
        elif self.port_g == 'COM5':
            self.ListCtrl1.SetItem(4, i, self.nongdu_g)
        elif self.port_g == 'COM6':
            self.ListCtrl1.SetItem(5, i, self.nongdu_g)
        elif self.port_g == 'COM7':
            self.ListCtrl1.SetItem(6, i, self.nongdu_g)
        elif self.port_g == 'COM8':
            self.ListCtrl1.SetItem(7, i, self.nongdu_g)
        elif self.port_g == 'COM9':
            self.ListCtrl1.SetItem(8, i, self.nongdu_g)
        elif self.port_g == 'COM10':
            self.ListCtrl1.SetItem(9, i, self.nongdu_g)
        elif self.port_g == 'COM11':
            self.ListCtrl1.SetItem(10, i, self.nongdu_g)
        elif self.port_g == 'COM12':
            self.ListCtrl1.SetItem(11, i, self.nongdu_g)
        elif self.port_g == 'COM13':
            self.ListCtrl1.SetItem(12, i, self.nongdu_g)
        elif self.port_g == 'COM14':
            self.ListCtrl1.SetItem(13, i, self.nongdu_g)
        elif self.port_g == 'COM15':
            self.ListCtrl1.SetItem(14, i, self.nongdu_g)
        elif self.port_g == 'COM16':
            self.ListCtrl1.SetItem(15, i, self.nongdu_g)

    def OnSelect2(self, event):
        if not self.is_running2:
            self.timer1.Stop()
            self.is_running1 = False
            self.is_running2 = True
            self.timer2.Start(10)  # 每10毫秒触发一次
    def on_timer2(self, event):
        select2 = self.cb2.GetStringSelection()
        # print(f'You selected: {select2}')
        if select2 == "20%":
            self.fill_high_data(0)
        elif select2 == "30%":
            self.fill_high_data(1)
        elif select2 == "50%":
            self.fill_high_data(2)
        elif select2 == "80%":
            self.fill_high_data(3)
        elif select2 == "100%":
            self.fill_high_data(4)

    def fill_high_data(self, i):
        if self.port_g == 'COM1':
            self.ListCtrl2.SetItem(0, i, self.nongdu_g)
        elif self.port_g == 'COM2':
            self.ListCtrl2.SetItem(1, i, self.nongdu_g)
        elif self.port_g == 'COM3':
            self.ListCtrl2.SetItem(2, i, self.nongdu_g)
        elif self.port_g == 'COM4':
            self.ListCtrl2.SetItem(3, i, self.nongdu_g)
        elif self.port_g == 'COM5':
            self.ListCtrl2.SetItem(4, i, self.nongdu_g)
        elif self.port_g == 'COM6':
            self.ListCtrl2.SetItem(5, i, self.nongdu_g)
        elif self.port_g == 'COM7':
            self.ListCtrl2.SetItem(6, i, self.nongdu_g)
        elif self.port_g == 'COM8':
            self.ListCtrl2.SetItem(7, i, self.nongdu_g)
        elif self.port_g == 'COM9':
            self.ListCtrl2.SetItem(8, i, self.nongdu_g)
        elif self.port_g == 'COM10':
            self.ListCtrl2.SetItem(9, i, self.nongdu_g)
        elif self.port_g == 'COM11':
            self.ListCtrl2.SetItem(10, i, self.nongdu_g)
        elif self.port_g == 'COM12':
            self.ListCtrl2.SetItem(11, i, self.nongdu_g)
        elif self.port_g == 'COM13':
            self.ListCtrl2.SetItem(12, i, self.nongdu_g)
        elif self.port_g == 'COM14':
            self.ListCtrl2.SetItem(13, i, self.nongdu_g)
        elif self.port_g == 'COM15':
            self.ListCtrl2.SetItem(14, i, self.nongdu_g)
        elif self.port_g == 'COM16':
            self.ListCtrl2.SetItem(15, i, self.nongdu_g)

    def port_update(self, arg1):
        print("message:{}".format(arg1))
        self.message_queue.put({"msg_id": "PortUpdate", "PortInfo": arg1})

    def port_recieve_data(self, arg1):
        print("recieve data:{}".format(arg1))
        # print(arg1[0])
        # print(type(arg1[0]))
        if "REPLY" in arg1[0]:
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
                self.comx_nongdu[0] = nongdu
                self.ListCtrl.SetItem(0, 1, nongdu)
                self.ListCtrl.SetItem(0, 2, wavelength)
                self.ListCtrl.SetItem(0, 3, guangqiang)
                self.ListCtrl.SetItem(0, 4, wendu)
            elif arg1[1] == 'COM2':
                self.comx_nongdu[1] = nongdu
                self.ListCtrl.SetItem(1, 1, nongdu)
                self.ListCtrl.SetItem(1, 2, wavelength)
                self.ListCtrl.SetItem(1, 3, guangqiang)
                self.ListCtrl.SetItem(1, 4, wendu)
            elif arg1[1] == 'COM3':
                self.comx_nongdu[2] = nongdu
                self.ListCtrl.SetItem(2, 1, nongdu)
                self.ListCtrl.SetItem(2, 2, wavelength)
                self.ListCtrl.SetItem(2, 3, guangqiang)
                self.ListCtrl.SetItem(2, 4, wendu)
            elif arg1[1] == 'COM4':
                self.comx_nongdu[3] = nongdu
                self.ListCtrl.SetItem(3, 1, nongdu)
                self.ListCtrl.SetItem(3, 2, wavelength)
                self.ListCtrl.SetItem(3, 3, guangqiang)
                self.ListCtrl.SetItem(3, 4, wendu)
            elif arg1[1] == 'COM5':
                self.comx_nongdu[4] = nongdu
                self.ListCtrl.SetItem(4, 1, nongdu)
                self.ListCtrl.SetItem(4, 2, wavelength)
                self.ListCtrl.SetItem(4, 3, guangqiang)
                self.ListCtrl.SetItem(4, 4, wendu)
            elif arg1[1] == 'COM6':
                self.comx_nongdu[5] = nongdu
                self.ListCtrl.SetItem(5, 1, nongdu)
                self.ListCtrl.SetItem(5, 2, wavelength)
                self.ListCtrl.SetItem(5, 3, guangqiang)
                self.ListCtrl.SetItem(5, 4, wendu)
            elif arg1[1] == 'COM7':
                self.comx_nongdu[6] = nongdu
                self.ListCtrl.SetItem(6, 1, nongdu)
                self.ListCtrl.SetItem(6, 2, wavelength)
                self.ListCtrl.SetItem(6, 3, guangqiang)
                self.ListCtrl.SetItem(6, 4, wendu)
            elif arg1[1] == 'COM8':
                self.comx_nongdu[7] = nongdu
                self.ListCtrl.SetItem(7, 1, nongdu)
                self.ListCtrl.SetItem(7, 2, wavelength)
                self.ListCtrl.SetItem(7, 3, guangqiang)
                self.ListCtrl.SetItem(7, 4, wendu)
            elif arg1[1] == 'COM9':
                self.comx_nongdu[8] = nongdu
                self.ListCtrl.SetItem(8, 1, nongdu)
                self.ListCtrl.SetItem(8, 2, wavelength)
                self.ListCtrl.SetItem(8, 3, guangqiang)
                self.ListCtrl.SetItem(8, 4, wendu)
            if arg1[1] == 'COM10':
                self.comx_nongdu[9] = nongdu
                self.ListCtrl.SetItem(9, 1, nongdu)
                self.ListCtrl.SetItem(9, 2, wavelength)
                self.ListCtrl.SetItem(9, 3, guangqiang)
                self.ListCtrl.SetItem(9, 4, wendu)
            elif arg1[1] == 'COM11':
                self.comx_nongdu[10] = nongdu
                self.ListCtrl.SetItem(10, 1, nongdu)
                self.ListCtrl.SetItem(10, 2, wavelength)
                self.ListCtrl.SetItem(10, 3, guangqiang)
                self.ListCtrl.SetItem(10, 4, wendu)
            elif arg1[1] == 'COM12':
                self.comx_nongdu[11] = nongdu
                self.ListCtrl.SetItem(11, 1, nongdu)
                self.ListCtrl.SetItem(11, 2, wavelength)
                self.ListCtrl.SetItem(11, 3, guangqiang)
                self.ListCtrl.SetItem(11, 4, wendu)
            elif arg1[1] == 'COM13':
                self.comx_nongdu[12] = nongdu
                self.ListCtrl.SetItem(12, 1, nongdu)
                self.ListCtrl.SetItem(12, 2, wavelength)
                self.ListCtrl.SetItem(12, 3, guangqiang)
                self.ListCtrl.SetItem(12, 4, wendu)
            elif arg1[1] == 'COM14':
                self.comx_nongdu[13] = nongdu
                self.ListCtrl.SetItem(13, 1, nongdu)
                self.ListCtrl.SetItem(13, 2, wavelength)
                self.ListCtrl.SetItem(13, 3, guangqiang)
                self.ListCtrl.SetItem(13, 4, wendu)
            elif arg1[1] == 'COM15':
                self.comx_nongdu[14] = nongdu
                self.ListCtrl.SetItem(14, 1, nongdu)
                self.ListCtrl.SetItem(14, 2, wavelength)
                self.ListCtrl.SetItem(14, 3, guangqiang)
                self.ListCtrl.SetItem(14, 4, wendu)
            elif arg1[1] == 'COM16':
                self.comx_nongdu[15] = nongdu
                self.ListCtrl.SetItem(15, 1, nongdu)
                self.ListCtrl.SetItem(15, 2, wavelength)
                self.ListCtrl.SetItem(15, 3, guangqiang)
                self.ListCtrl.SetItem(15, 4, wendu)
        else:
            pass

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
                self.ListCtrl3.InsertItem(i, i)

                self.ListCtrl.SetItem(i, 0, element)
                self.ListCtrl.SetItem(i, 1, "")
                self.ListCtrl.SetItem(i, 2, "")
                self.ListCtrl.SetItem(i, 3, "")
                self.ListCtrl.SetItem(i, 4, "")
                self.ListCtrl.SetItemBackgroundColour(i, (255, 255, 255))
        self.message_queue.put({"msg_id": "PortTest"})

    def port_test_handler(self):
        print("start test")
        try:
            # 循环开启每个串口并创建对应的线程
            for port in self._channel_list:
                if 'COM' in port:
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