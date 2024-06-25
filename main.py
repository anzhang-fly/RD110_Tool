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

if hasattr(sys, '_MEIPASS'):
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))


def set_config(PROJECT_ABSOLUTE_PATH, frame):
    if not os.path.exists(PROJECT_ABSOLUTE_PATH+"\\config.ini"):
        return
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(PROJECT_ABSOLUTE_PATH+"\\config.ini", encoding='utf-8')
    Excel_file = conf.get("software", "Excel_file")
    json_file = conf.get("software", "json_file")

    if Excel_file or json_file:
        no_exist = []
        msg = wx.MessageBox(_(u'是否恢复上次文件'), _(u'提示'), wx.YES_NO)
        if msg == wx.YES:
            if Excel_file:
                if os.path.exists(Excel_file):
                    frame.text_ctrl_excel.SetValue(Excel_file)
                else:
                    conf.set("software", "Excel_file", "")
                    wx.MessageBox(Excel_file + _(u"文件不存在"), _(u"提示"), wx.YES_DEFAULT | wx.ICON_INFORMATION)

            if json_file:
                if os.path.exists(Excel_file):
                    frame.text_ctrl_json.SetValue(json_file)
                    frame.load_json_file(0, json_file)
                else:
                    conf.set("software", "json_file", "")
                    wx.MessageBox(json_file + _(u"文件不存在"), _(u"提示"), wx.YES_DEFAULT | wx.ICON_INFORMATION)

            with open(PROJECT_ABSOLUTE_PATH + "\\config.ini", "w+", encoding='utf-8') as f:
                conf.write(f)

        elif msg == wx.NO:
            conf.set("software", "Excel_file", "")
            conf.set("software", "json_file", "")
            with open(PROJECT_ABSOLUTE_PATH + "\\config.ini", "w+", encoding='utf-8') as f:
                conf.write(f)


class FactoryFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        self.count1 = 0
        self.port_list_num = 0

        # self.SetSize((1120, 650))
        self.SetSize((1600, 700))
        self.Center()
        # stdout log
        # sys.stdin是一个标准化输入的方法
        # input.stdin.readline()
        sys.stderr = RedirectErr(self, PROJECT_ABSOLUTE_PATH)  # 创建一个存放日志文件的对象（存放错误日志）
        sys.stdout = RedirectStd(self, PROJECT_ABSOLUTE_PATH)  # 创建一个存放输出文件的对象（存放输出日志）
        # module log
        self.logger = ModuleLog()  # 创建一个测试时的日志文件
        # Menu Bar
        self.menuBar = wx.MenuBar()  # 创建状态栏对象
        wxg_tmp_menu = wx.Menu()     # 创建一个状态栏“编辑”控件
        wxg_tmp_menu.Append(1002, _(u"编辑设备Excel文件"), "")               # 在“编辑”控件中添加一个子项目，项目名称为编辑Py文件，id=1002
        self.Bind(wx.EVT_MENU, self.__menu_handler, id=1002)        # 为编辑Py文件，绑定一个事件
        wxg_tmp_menu.Append(1003, _(u"编辑测试Excel文件"), "")            # 在“编辑”控件中添加一个子项目，项目名称为编辑Excel文件，id=1003
        self.Bind(wx.EVT_MENU, self.__menu_handler, id=1003)        # 为编辑Excel文件，绑定一个事件
        self.menuBar.Append(wxg_tmp_menu, _(u"编辑"))
        wxg_tmp_menu_1 = wx.Menu()  # 创建一个状态栏“日志”控件
        wxg_tmp_menu_1.Append(2001, _(u"工具日志"), "")              # 在“日志”控件中添加一个子项目，项目名称为工具日志，id=2001
        self.Bind(wx.EVT_MENU, self.__menu_handler, id=2001)        # 为工具日志，绑定一个事件
        wxg_tmp_menu_1.AppendSeparator()                            # 添加菜单分隔符
        wxg_tmp_menu_1.Append(2002, _(u"模块日志"), "")              # 在“日志”控件中添加一个子项目，模块日志，id=2002
        self.Bind(wx.EVT_MENU, self.__menu_handler, id=2002)        # 为模块日志，绑定一个事件
        self.menuBar.Append(wxg_tmp_menu_1, _(u"日志"))
        self.SetMenuBar(self.menuBar)
        # Menu Bar end
        # self.statusBar = self.CreateStatusBar(3)
        self.main_panel = wx.Panel(self, wx.ID_ANY)
        self.load_excel = wx.Button(self.main_panel, wx.ID_ANY, _("选择"))                           # 创建“选择”按钮控件
        self.text_ctrl_excel = wx.TextCtrl(self.main_panel, wx.ID_ANY, "", style=wx.TE_READONLY)    # 创建“可控文本”控件，属性只读
        self.load_json = wx.Button(self.main_panel, wx.ID_ANY, _("选择"))                         # 创建“选择”按钮控件
        self.text_ctrl_json = wx.TextCtrl(self.main_panel, wx.ID_ANY, "", style=wx.TE_READONLY)  # 创建“可控文本”控件，属性只读

        self.Bind(wx.EVT_BUTTON, self.__load_Excel_file, self.load_excel)    # 绑定“选择”按钮控件，绑定函数为__load_Excel_file
        self.Bind(wx.EVT_BUTTON, self.load_json_file, self.load_json)  # 绑定“选择”按钮控件，绑定函数为load_json_file

        self.button_all_start = wx.Button(self.main_panel, wx.ID_ANY, _("全部开始"))  # 创建“全部开始”按钮控件
        self.Bind(wx.EVT_BUTTON, self.test_all_start, self.button_all_start)         # 绑定“全部开始”按钮控件，绑定函数为test_all_start

        self.button_start_list = []
        self.ListCtrl_list = []
        self.port_ctrl_list = []
        self.port_imei_list = []
        self.port_iccid_list = []
        # 创建ListCtrl对象
        # style表示窗口样式， wx.LC_REPORT：报告模式，LC_HRULES：在报告模式中，显示行间标尺，LC_VRULES：在报告模式中，显示列间标尺，LC_SINGLE_SEL：指定单选模式
        self.ListCtrl = wx.ListCtrl(self.main_panel, -1, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.ListCtrl.SetMinSize((500, 650))  # 设置列表窗口最小尺寸
        # 在报表视图模式向列表添加新列
        self.ListCtrl.AppendColumn(_(u"端口"), format=wx.LIST_FORMAT_LEFT, width=70)
        self.ListCtrl.AppendColumn(_(u"浓度"), format=wx.LIST_FORMAT_LEFT, width=70)
        self.ListCtrl.AppendColumn(_(u"波长"), format=wx.LIST_FORMAT_LEFT, width=70)
        self.ListCtrl.AppendColumn(_(u"光强"), format=wx.LIST_FORMAT_LEFT, width=70)
        self.ListCtrl.AppendColumn(_(u"温度"), format=wx.LIST_FORMAT_LEFT, width=70)

        self.DeviceNum_list = []  # 用于存放设备id号
        # 创建一个表格，并初始化表格第一行内容
        self.__init_excel()
        self.DeviceNum_list = self.__excel_read_DeviceNum()
        print("DeviceNum_list:", self.DeviceNum_list)

        # event message queue
        self.message_queue = Queue(maxsize=10)  # 创建一个队列，队列最大容量10个项目
        self._channel_list = []
        threading.Thread(target=self.port_process_handler, args=()).start()  # 开启port_process_handler线程
        # self.lock = threading.Lock()

        self.procese_num = 0

        # 绑定关闭页面事件
        self.Bind(wx.EVT_CLOSE, self.close_window)

        # 订阅主题为“serialUpdate”的数据，并传入到port_update函数
        # pub message
        pub.subscribe(self.port_update, "serialUpdate")

        # ConfigParser（）是用来读取配置文件的包（ini配置文件）
        self.conf = configparser.ConfigParser(interpolation=None)
        if not os.path.exists(PROJECT_ABSOLUTE_PATH+"\\config.ini"):
            self.initConfigFile()
        self.conf.read(PROJECT_ABSOLUTE_PATH+"\\config.ini", encoding='utf-8')

        # 设置“开始”按钮和“全部开始”按钮的大小
        self.__set_properties()

        # 页面布局管理
        self.__do_layout()

    def __set_properties(self):
        for i in range(8):
            self.button_start_list[i].SetMinSize((150, 50))
        self.button_all_start.SetMinSize((150, 50))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, _("选择设备文件")), wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, _("选择配置文件")), wx.HORIZONTAL)
        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, _("工厂测试")), wx.HORIZONTAL)

        sizer_3.Add((4, 20), 0, 0, 0)
        sizer_3.Add(self.load_excel, 0, 0, 0)
        sizer_3.Add((20, 20), 0, 0, 0)
        sizer_3.Add(self.text_ctrl_excel, 1, 0, 0)
        sizer_3.Add((20, 20), 0, 0, 0)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)

        sizer_4.Add((4, 20), 0, 0, 0)
        sizer_4.Add(self.load_json, 0, 0, 0)
        sizer_4.Add((20, 20), 0, 0, 0)
        sizer_4.Add(self.text_ctrl_json, 1, 0, 0)
        sizer_4.Add((20, 20), 0, 0, 0)
        sizer_2.Add((20, 4), 0, 0, 0)
        sizer_2.Add(sizer_4, 0, wx.EXPAND, 0)

        for i in range(8):
            sizer_6 = wx.BoxSizer(wx.VERTICAL)
            sizer_6.Add(self.port_ctrl_list[i], 0, 0, 1)
            sizer_6.Add(self.ListCtrl_list[i], 1, 1, 1)
            sizer_6.Add((0, 10), 0, 0, 0)
            sizer_6.Add(self.button_start_list[i], 0, 1, 0)
            sizer_5.Add(sizer_6, 1, 0, 0)
        sizer_2.Add(sizer_5, 0, wx.EXPAND, 0)

        sizer_2.Add((0, 50), 0, 1, 1)
        sizer_2.Add(self.button_all_start, 0, 1, 1)

        self.main_panel.SetSizer(sizer_2)
        sizer_1.Add(self.main_panel, 1, wx.EXPAND | wx.TOP, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # sizer_5.SetLabel(_("测试中"))

    def __menu_handler(self, event):  # wxGlade: FactoryFrame.<event_handler>
        # if event.GetId() == 1001:
        #     DialogControl(self, "demo").Show()
        if event.GetId() == 1002:
            # notepad.exe表示记事本应用程序
            # file_path, app_path = "notepad.exe", PROJECT_ABSOLUTE_PATH + "\\module_test.py"
            # raw_file_path = r'%s' % file_path  # raw_file_path =  notepad.exe
            # raw_app_path = r'%s' % app_path     # raw_app_path = PROJECT_ABSOLUTE_PATH + "\\module_test.py"
            # subprocess.call([raw_file_path, raw_app_path])  # 执行打开记事本应用
            excel_flie = glob.glob("设备*.xlsx")
            excel_device_file = subprocess.Popen(["start", "/WAIT", os.path.join(PROJECT_ABSOLUTE_PATH, excel_flie[0])], shell=True)
            excel_device_file.poll()  # 执行打开excel应用
        elif event.GetId() == 1003:
            excel_file = subprocess.Popen(["start", "/WAIT", PROJECT_ABSOLUTE_PATH + "\\Test-Result.xlsx"], shell=True)
            # psutil.Process(excel_file.pid).get_children()[0].kill()
            excel_file.poll() # 执行打开excel应用
        elif event.GetId() == 2001:
            # 打开指定路径的文件夹
            p = subprocess.Popen("explorer.exe " + PROJECT_ABSOLUTE_PATH + "\\logs\\software\\", shell=True)
        elif event.GetId() == 2002:
            p = subprocess.Popen("explorer.exe " + PROJECT_ABSOLUTE_PATH + "\\logs\\apps\\", shell=True)
        event.Skip()  # 将事件传递给下一个适当的处理程序

    def initConfigFile(self):
        self.conf.add_section("software")  # 在.ini文件中增加一个名为“software”的段
        self.conf.set("software", "Excel_file", "")  # 在“software”段中增加字典Excel_file =
        self.conf.set("software", "json_file", "")  # 在“software”段中增加字典json_file =
        with open(PROJECT_ABSOLUTE_PATH + "\\config.ini", "w+", encoding='utf-8') as f:
            self.conf.write(f)   # 写入config.ini文件

    def __load_Excel_file(self, event):
        defDir, defFile = '', ''  # default dir/ default file
        # 创建一个文件对话框对象，defDir, defFile为空
        # dlg = wx.FileDialog(self, u'Open Py File', defDir, defFile, 'Python file (*.py)|*.py',
        #                     wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        dlg = wx.FileDialog(self, u'Open excel File', defDir, defFile, 'excel file (*.xlsx)|*.xlsx',
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        # ShowModal方法，显示对话框，如果点击了wx.OK按钮则返回wx.ID_OK, 否则返回wx.ID_CANCEL
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        self.text_ctrl_excel.SetValue(dlg.GetPath())  # 窗口栏显示py文件路径
        self.conf.set("software", "Excel_file", dlg.GetPath()) # py文件路径设置为.ini文件的Excel_file的value
        with open(PROJECT_ABSOLUTE_PATH + "\\config.ini", "w+", encoding='utf-8') as f:
            self.conf.write(f)

    def load_json_file(self, event, json_file=None):
        print("json button is press")
        if event != 0:
            defDir, defFile = '', ''  # default dir/ default file
            dlg = wx.FileDialog(self, u'Open Config File', defDir, defFile, 'Config file (*.json)|*.json',
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            json_file = dlg.GetPath()
        try:
            with codecs.open(json_file, 'r', 'utf-8') as f:
                data = json.load(f)  # data = {'info': [['Memory test', 'det_file_space', 1], ['Signal test', 'det_signal', 0]]}
                print(data)
                info = data["info"]   # info = [['Memory test', 'det_file_space', 1], ['Signal test', 'det_signal', 0]]
                self.testFunctions = [i[1:] for i in info]  # self.testFunctions = [['det_file_space', 1], ['det_signal', 0]]
                self.testMessages = [i[0] for i in info]    # self.testMessages = ['Memory test', 'Signal test']
            self.text_ctrl_json.SetValue(json_file)  # 窗口栏显示json文件路径
            self.conf.set("software", "json_file", json_file)    # 文件路径设置为.ini文件的json_file的value
            with open(PROJECT_ABSOLUTE_PATH + "\\config.ini", "w+", encoding='utf-8') as f:
                self.conf.write(f)

            for i, port_ctrl in enumerate(self.port_ctrl_list):  # 遍历com口
                ListCtrl.InsertItem(i, i)  # 插入新项
                ListCtrl.SetItem(j, 0, self.testMessages[j])
                if port_ctrl.GetValue():  # 获取com口号
                    self.ListCtrl_list[i].DeleteAllItems()  # 删除列表控件中的所有子项
                    for j, element in enumerate(self.testFunctions):
                        ListCtrl = self.ListCtrl_list[i]
                        # testFunction = self.testFunctions[j]
                        ListCtrl.InsertItem(j, j)  # 插入新项
                        ListCtrl.SetItem(j, 0, self.testMessages[j])  # 在第j项的第1个位置显示测试项
                        if element[1] == 1:
                            ListCtrl.SetItem(j, 1, _(u"人工检测"))  # 在第j项的第2个位置显示测试方式
                        else:
                            ListCtrl.SetItem(j, 1, _(u"自动检测"))
        except Exception as e:
            print(e)
            wx.MessageBox(_(u'请选择正确的配置文件'), u'提示', wx.YES_DEFAULT | wx.ICON_INFORMATION)
            return

    def test_start(self, event):
        button_event_id = event.GetId() - 100  # button ID 100开始

        if self.text_ctrl_json.GetValue():
            pass
        else:
            wx.MessageBox(_(u'请先选择配置文件'), u'提示', wx.YES_DEFAULT | wx.ICON_INFORMATION)
            return

        if self.text_ctrl_excel.GetValue():
            if self.port_ctrl_list[button_event_id].GetValue():
                # 点击开始时再初始化
                self.__port_det(True)  # 检测停止

                self.procese_num += 1
                self.button_all_start.Enable(False)
                self.button_start_list[button_event_id].Enable(False)
                # id = [0,1,2,3] "PortInfo = [com1,com2,com3,com4]
                self.message_queue.put(
                    {"id": button_event_id, "msg_id": "PortInit", "PortInfo": self.port_ctrl_list[button_event_id].GetValue()})
            else:
                return None
        else:
            wx.MessageBox(_(u'请先选择测试文件'), u'提示', wx.YES_DEFAULT | wx.ICON_INFORMATION)

    def test_all_start(self, event):
        self.__port_det(True)  # 检测停止
        self.count1 = self.count1 + 1  # 计数，用于检测点击几次全部开始按钮

        if self.text_ctrl_json.GetValue():
            pass
        else:
            wx.MessageBox(_(u'请先选择配置文件'), u'提示', wx.YES_DEFAULT | wx.ICON_INFORMATION)
            return

        if self.text_ctrl_excel.GetValue():
            pass
        else:
            wx.MessageBox(_(u'请先选择测试文件'), u'提示', wx.YES_DEFAULT | wx.ICON_INFORMATION)
            return None

        for i in self.port_ctrl_list:
            button_event_id = i.GetId() - 300
            if i.GetValue():  # 获取可控文本中的内容（此处为获取com口号）
                self.procese_num += 1
                self.button_all_start.Enable(False)  # 使能“全部开始”按键
                self.button_start_list[button_event_id].Enable(False)  # 使能“开始”按键
                # id = [0,1,2,3] "PortInfo = [com1,com2,com3,com4]
                self.message_queue.put(
                    {"id": button_event_id, "msg_id": "PortInit",
                     "PortInfo": self.port_ctrl_list[button_event_id].GetValue()})
            else:
                return None

    #  订阅了sendmessage发过来的数据：arg1 = serial_port，serial_port为一个列表，列表内容为检测到的com口
    def port_update(self, arg1):
        print("message:{}".format(arg1))
        self.port_list_num = len(arg1)
        self.message_queue.put({"msg_id": "PortUpdate", "PortInfo": arg1})

    def port_update_handler(self, arg1):
        # TODO 设置log按钮状态
        port_list = arg1["PortInfo"][:8] if len(arg1["PortInfo"]) > 8 else arg1["PortInfo"]  # 类似于C语言的三目运算符
        if len(port_list) < 8:
            self.button_all_start.Enable(False) if len(port_list) == 0 else self.button_all_start.Enable(True)
            port_list = port_list + [""] * (8 - len(port_list))
        if self._channel_list == [] or self._channel_list != port_list:
            self._channel_list = port_list

            self.ListCtrl.DeleteAllItems()

            for i, element in enumerate(self._channel_list):
                self.ListCtrl.InsertItem(i, i)
                self.ListCtrl.SetItem(i, 0, element)
                self.ListCtrl.SetItem(i, 1, "")
                self.ListCtrl.SetItem(i, 2, "")
                self.ListCtrl.SetItem(i, 3, "")
                self.ListCtrl.SetItem(i, 4, "")
                self.ListCtrl.SetItemBackgroundColour(i, (255, 255, 255, 255))

    def port_init_handler(self, arg1):
        for i in range(len(self._channel_list)):
            self.ListCtrl.SetItem(i, 2, "")
            self.ListCtrl.SetItem(i, 3, "")
            self.ListCtrl.SetItem(i, 4, "")
            self.ListCtrl.SetItem(i, 5, "")
            self.ListCtrl.SetItemBackgroundColour(i, (255, 255, 255, 255))
        self.message_queue.put(
            {"id": arg1["id"], "msg_id": "PortTest", "PortInfo": self.port_ctrl_list[arg1["id"]].GetValue()})

    def read_serial(self, ser):
        while True:
            if ser.in_waiting() > 0:
                # data = ser.read(self._conn.inWaiting()).decode("utf-8", errors="ignore")
                data = ser.readline().decode("utf-8").strip()
                print(f"Received from {ser.port}: {data}")

                if ser.port == 'com1':
                    self.ListCtrl.SetItem(0, 1, "")
                    self.ListCtrl.SetItem(0, 2, "")
                    self.ListCtrl.SetItem(0, 3, "")
                    self.ListCtrl.SetItem(0, 4, "")
                elif ser.port == 'com2':
                    self.ListCtrl.SetItem(1, 1, "")
                    self.ListCtrl.SetItem(1, 2, "")
                    self.ListCtrl.SetItem(1, 3, "")
                    self.ListCtrl.SetItem(1, 4, "")
                elif ser.port == 'com3':
                    self.ListCtrl.SetItem(2, 1, "")
                    self.ListCtrl.SetItem(2, 2, "")
                    self.ListCtrl.SetItem(2, 3, "")
                    self.ListCtrl.SetItem(2, 4, "")
                elif ser.port == 'com4':
                    self.ListCtrl.SetItem(3, 1, "")
                    self.ListCtrl.SetItem(3, 2, "")
                    self.ListCtrl.SetItem(3, 3, "")
                    self.ListCtrl.SetItem(3, 4, "")
                elif ser.port == 'com5':
                    self.ListCtrl.SetItem(4, 1, "")
                    self.ListCtrl.SetItem(4, 2, "")
                    self.ListCtrl.SetItem(4, 3, "")
                    self.ListCtrl.SetItem(1, 4, "")
                elif ser.port == 'com6':
                    self.ListCtrl.SetItem(5, 1, "")
                    self.ListCtrl.SetItem(5, 2, "")
                    self.ListCtrl.SetItem(5, 3, "")
                    self.ListCtrl.SetItem(5, 4, "")
                elif ser.port == 'com7':
                    self.ListCtrl.SetItem(6, 1, "")
                    self.ListCtrl.SetItem(6, 2, "")
                    self.ListCtrl.SetItem(6, 3, "")
                    self.ListCtrl.SetItem(6, 4, "")
                elif ser.port == 'com8':
                    self.ListCtrl.SetItem(7, 1, "")
                    self.ListCtrl.SetItem(7, 2, "")
                    self.ListCtrl.SetItem(7, 3, "")
                    self.ListCtrl.SetItem(7, 4, "")
                elif ser.port == 'com9':
                    self.ListCtrl.SetItem(8, 1, "")
                    self.ListCtrl.SetItem(8, 2, "")
                    self.ListCtrl.SetItem(8, 3, "")
                    self.ListCtrl.SetItem(8, 4, "")
                if ser.port == 'com10':
                    self.ListCtrl.SetItem(9, 1, "")
                    self.ListCtrl.SetItem(9, 2, "")
                    self.ListCtrl.SetItem(9, 3, "")
                    self.ListCtrl.SetItem(9, 4, "")
                elif ser.port == 'com11':
                    self.ListCtrl.SetItem(10, 1, "")
                    self.ListCtrl.SetItem(10, 2, "")
                    self.ListCtrl.SetItem(10, 3, "")
                    self.ListCtrl.SetItem(10, 4, "")
                elif ser.port == 'com12':
                    self.ListCtrl.SetItem(11, 1, "")
                    self.ListCtrl.SetItem(11, 2, "")
                    self.ListCtrl.SetItem(11, 3, "")
                    self.ListCtrl.SetItem(11, 4, "")
                elif ser.port == 'com13':
                    self.ListCtrl.SetItem(12, 1, "")
                    self.ListCtrl.SetItem(12, 2, "")
                    self.ListCtrl.SetItem(12, 3, "")
                    self.ListCtrl.SetItem(12, 4, "")
                elif ser.port == 'com14':
                    self.ListCtrl.SetItem(13, 1, "")
                    self.ListCtrl.SetItem(13, 2, "")
                    self.ListCtrl.SetItem(13, 3, "")
                    self.ListCtrl.SetItem(13, 4, "")
                elif ser.port == 'com15':
                    self.ListCtrl.SetItem(14, 1, "")
                    self.ListCtrl.SetItem(14, 2, "")
                    self.ListCtrl.SetItem(14, 3, "")
                    self.ListCtrl.SetItem(14, 4, "")
                elif ser.port == 'com16':
                    self.ListCtrl.SetItem(15, 1, "")
                    self.ListCtrl.SetItem(15, 2, "")
                    self.ListCtrl.SetItem(15, 3, "")
                    self.ListCtrl.SetItem(15, 4, "")

    def port_test_handler(self, arg1):
        print("start test")
        self.serial_threads = []
        try:
            # 循环开启每个串口并创建对应的线程
            for comx in self._channel_list:
                ser = serial.Serial(port=comx, baud=115200, parity=serial.PARITY_EVEN, timeout=1) # 打开一个端口
                thread = threading.Thread(target=self.read_serial, args=(ser,))
                self.serial_threads.append((ser, thread))
                thread.start()
                print(f"Opened {comx}")
        except Exception as e:
            wx.MessageBox(arg1["PortInfo"]+"串口异常，测试脚本写入失败, error %s"%str(e), u'Error', wx.YES_DEFAULT | wx.ICON_INFORMATION)

    def port_test_end_handler(self, arg1):
        self.__port_det(False)

    def __init_excel(self):
        # 初始化一个excel表格
        # self.__excel_handler = file_handler.ExcelHandler(PROJECT_ABSOLUTE_PATH + "\\Test-Result.xlsx")  # Init Excel
        excel_flie = glob.glob("设备*.xlsx")
        self.read_excel_handler = file_handler.ExcelHandler(os.path.join(PROJECT_ABSOLUTE_PATH, excel_flie[0]))  # Init Excel
        # 获取excel表格的行列数
        # rows, columns = self.__excel_handler.get_rows_columns()
        # if rows == 1 and columns == 1:
        #     # 设置某一单元格的值
        #     self.__excel_handler.set_cell_value(1, 1, "No.")
        #     self.__excel_handler.set_cell_value(1, 2, "Com Port")
        #     self.__excel_handler.set_cell_value(1, 3, "Test Result")
        #     self.__excel_handler.set_cell_value(1, 4, "Test Log")

    # def __excel_write(self, result):
    #     if self.__excel_handler:
    #         rows, columns = self.__excel_handler.get_rows_columns()
    #         self.__excel_handler.set_cell_value(rows + 1, 1, rows)
    #         for i, value in enumerate(result):
    #             self.__excel_handler.set_cell_value(rows + 1, i + 2, value)

    def __excel_write_Device(self, row, column, data):
        if self.read_excel_handler:
            self.read_excel_handler.set_cell_value(3+row, column, data)

    def __excel_read_DeviceNum(self):
        if self.read_excel_handler:
            columns_data = self.read_excel_handler.get_col_values_1(3, 3)  # 读取第3列数据（从第三行开始读）
            return columns_data   # 返回一个列表，列表数据为设备编号号

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
                    elif msg_id == "PortInit":
                        # threading.Thread(target=self.port_init_handler, args=(message,)).start()
                        self.port_init_handler(message)
                    elif msg_id == "PortTest":
                        threading.Thread(target=self.port_test_handler, args=(message,)).start()
                        # self.port_test_handler(message)
                    elif msg_id == "PortTestEnd":
                        threading.Thread(target=self.port_test_end_handler, args=(message,)).start()
                        # self.port_test_end_handler(message)
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
        try:
            # self.__excel_handler.close()
            self.read_excel_handler.close()
        except Exception as e:
            pass
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
        # gettext.bindtextdomain('Chinese', PROJECT_ABSOLUTE_PATH + "\\locale")
        # gettext.textdomain('Chinese')
        t = gettext.translation('Chinese', PROJECT_ABSOLUTE_PATH + "\\locale", languages=["zh_CN"])
        t.install()
        # _ = gettext.gettext
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
        # wx.App.__init__(self, redirect=False, filename=PROJECT_ABSOLUTE_PATH + "\\logs\\software\\run.log",
        #                 useBestVisual=True, clearSigInt=True)
        # print("init finish----")

    def OnInit(self):
        self.factory_frame = FactoryFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.factory_frame)
        self.factory_frame.Show()

        # 串口检测线程
        global tSerialDet
        tSerialDet = serial_list.SerialDetection()  # SerialDetection继承自threading.Thread
        # thread.setdaemon(daemonic),thread表示一个线程对象，daemonic是一个布尔值，用来决定线程是否为守护线程。
        # 如果daemonic为True，则该线程被设置为守护线程；如果daemonic为False，则该线程被设置为非守护线程。
        tSerialDet.setDaemon(True)  # 设置为守护线程，当主线程结束时，子线程全部结束
        tSerialDet.start()

        set_config(PROJECT_ABSOLUTE_PATH, self.factory_frame)
        return True


class ModuleLog(object):
    """log output file"""
    def __init__(self):
        if not os.path.exists(PROJECT_ABSOLUTE_PATH + "\\logs\\apps\\"):
            os.makedirs(PROJECT_ABSOLUTE_PATH + "\\logs\\apps\\")
        # os.walk（）方法是一种遍历目录数的函数，返回（root,dirs, files）
        # root代表当前遍历的目录路径，string类型
        # dirs代表root路径下的所有子目录名称，list类型，列表中的每个元素是string类型，代表子目录名称。
        # files代表root路径下的所有子文件名称，返回list类型，列表中的每个元素是string类型，代表子文件名称。
        for i in os.walk(PROJECT_ABSOLUTE_PATH + "\\logs\\apps\\"):
            self._log_file_list = i[2]  # 获取apps文件夹下的文件列表
        if len(self._log_file_list) >= 50:
            os.remove(PROJECT_ABSOLUTE_PATH + "\\logs\\apps\\" + self._log_file_list[0])  # 删除列表的第一个文件
        self._log_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"

    def write_file(self, port, data):
        try:
            tmp_data = "[" + port + "]\n" + data + "\n"
            with open(PROJECT_ABSOLUTE_PATH + "\\logs\\apps\\" + self._log_name, "a+", encoding="utf-8")as f:
                f.write(tmp_data)
            return True
        except:
            info = sys.exc_info()
            print("write file error.")
            print(info[0], info[1])
            return False


if __name__ == "__main__":
    file_name = os.path.basename(sys.executable)  #  file_name = python.exe
    app = MyApp()
    app.MainLoop()