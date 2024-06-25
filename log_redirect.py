#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project:FactoryTool 
@File:log_redirect.py
@Author:rivern.yuan
@Date:2022/10/11 9:47 
"""

import os
import datetime


class RedirectErr:
    """"""

    def __init__(self, obj, logpath):
        """Constructor"""
        if not os.path.exists(logpath + "\\logs\\software\\err\\"):
            os.makedirs(logpath + "\\logs\\software\\err\\")

        file_path = logpath + "\\logs\\software\\err\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "_run_err.log"
        self.filename = open(file_path, "a", encoding='utf-8')  # a表示「追加」；文件已存在，文件指针指向文件尾部，将内容追加在原文件后面；如果文件不存在，则新建文件写入

    def write(self, text):
        """"""
        if self.filename.closed:
            pass
        else:
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间
            self.filename.write('[' + str(curr_time) + '] ' + text)  # 向文件写入内容
            # flush() 方法是用来刷新缓冲区的，即将缓冲区中的数据立刻写入文件，同时清空缓冲区，不需要是被动的等待输出缓冲区写入。
            self.filename.flush()

    def flush(self):
        pass


class RedirectStd:
    """"""

    def __init__(self, obj, logpath):
        """Constructor"""
        if not os.path.exists(logpath + "\\logs\\software\\std\\"):
            os.makedirs(logpath + "\\logs\\software\\std\\")
        file_path = logpath + "\\logs\\software\\std\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "_run_std.log"
        self.filename = open(file_path, "a", encoding='utf-8')

    def write(self, text):
        """"""
        if self.filename.closed:
            pass
        else:
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if text != "":
                self.filename.write('[' + str(curr_time) + '] ' + text)
                self.filename.flush()

    def flush(self):
        pass


# class StandardOutWrite:
#     def write(self, x):
#         old_std.write(x.replace("\n", " [[%s]]\n" % str(datetime.datetime.now())))
