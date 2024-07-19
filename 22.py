# import wx
# class MyFrame(wx.Frame):
#     def __init__(self):
#         super().__init__(None,title="盒子布局",size=(400,300))
#         panel=wx.Panel(parent=self)
#         self.statictext=wx.StaticText(parent=panel,label='请单击OK！')
#         b=wx. Button(parent=panel,label='OK')
#         self.Bind(wx.EVT_BUTTON,self.on_click,b)
#         vbox=wx.BoxSizer(wx.VERTICAL) #垂直方向布局
#         vbox.Add(self.statictext,proportion=1,
#                  flag=wx.ALIGN_CENTER_HORIZONTAL|wx.FIXED_MINSIZE|wx.TOP,
#                  border=50)
#         vbox.Add(b,proportion=1,flag=wx.EXPAND|wx.BOTTOM,border=10)
#         panel.SetSizer(vbox)
#     def on_click(self,event):
#         self.statictext.SetLabelText('Hello World!')
# app = wx.App()
# frm=MyFrame()
# frm.Show()
# app.MainLoop()


# import wx
#
#
# class MyFrame(wx.Frame):
#     def __init__(self, parent, title):
#         super(MyFrame, self).__init__(parent, title=title, size=(300, 200))
#
#         panel = wx.Panel(self)
#         sizer = wx.BoxSizer(wx.VERTICAL)
#
#         self.combo = wx.ComboBox(panel, choices=["Option 1", "Option 2", "Option 3"])
#         self.combo.Bind(wx.EVT_COMBOBOX, self.on_combo_select)
#
#         sizer.Add(self.combo, 0, wx.ALL | wx.CENTER, 5)
#
#         panel.SetSizer(sizer)
#         self.Centre()
#
#         self.timer = wx.Timer(self)
#         self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
#         self.is_running = False
#
#     def on_combo_select(self, event):
#         if not self.is_running:
#             self.is_running = True
#             self.timer.Start(1000)  # 每1000毫秒（1秒）触发一次
#
#     def on_timer(self, event):
#         selection = self.combo.GetStringSelection()
#         print(f'You selected: {selection}')
#         # 这里可以添加其他需要重复执行的代码
#
#
# class MyApp(wx.App):
#     def OnInit(self):
#         frame = MyFrame(None, title="ComboBox Example")
#         frame.Show()
#         return True
#
#
# if __name__ == '__main__':
#     app = MyApp()
#     app.MainLoop()

#
import numpy as np

# 生成一些示例数据
x = [296993
,361981
,470752
,594500
,662857
]
y = Std_nongdu_h = [200000, 300000, 500000, 800000, 1000000]

# 进行一次多项式拟合
coefficients = np.polyfit(x, y, 3)

# 打印拟合的系数
print(coefficients)



# import numpy as np
# import openpyxl
#
# # 读取Excel文件
# file_path = r'F:\ZHYQ\www.xlsx'  # 将此路径替换为你的Excel文件路径
# workbook = openpyxl.load_workbook(file_path)
# sheet = workbook.active
#
# # 获取最大行数和列数
# max_row = sheet.max_row
# max_column = sheet.max_column
#
# # 初始化一个空的二维列表
# data_2d_list = [[] for _ in range(max_column)]
#
# # 将每列数据添加到对应的二维列表的子列表中，并转换为整数
# for col in range(1, max_column + 1):
#     for row in range(1, max_row + 1):
#         cell_value = sheet.cell(row=row, column=col).value
#         if cell_value is not None:
#             try:
#                 int_value = int(cell_value)
#                 data_2d_list[col - 1].append(int_value)
#             except ValueError:
#                 # 如果转换失败，可以选择记录错误或设置默认值
#                 data_2d_list[col - 1].append(None)
#         else:
#             data_2d_list[col - 1].append(None)
#
# print(data_2d_list)

# import numpy as np
#
# Std_nongdu_h = [200000, 300000, 500000, 800000, 1000000]
#
# my_list = [[0, 0, 0, 0, 0],
#            [324192, 399112, 521459, 661799, 735375],
#            [333788, 408734, 532428, 671437, 747485],
#            [0, 0, 0, 0, 0],
#            [333125, 408300, 535225, 673027, 745871],
#            [324518, 397134, 521771, 655983, 729501],
#            [298252, 364401, 473446, 596172, 660823],
#            [293538, 360709, 470783, 590543, 659425],
#            [321759, 396123, 516639, 653219, 725113],
#            [320899, 389278, 497701, 626825, 693114],
#            [321867, 387754, 503296, 627743, 695455],
#            [296993, 361981, 470752, 594500, 662857],
#            [329600, 405121, 526826, 668755, 742665],
#            [323541, 396592, 517498, 655046, 725661],
#            [316758, 385543, 502119, 630398, 699313],
#            [293290, 358655, 468401, 593245, 657374]]
#
# my_array = np.array(my_list)
# y = np.array(Std_nongdu_h)
#
# coefficients = []
# coefficients1 = []
#
# for i in range(16):
#     if np.all(my_array[i] == 0):
#         print("com_matrix[{}]全0".format(i))
#     else:
#         coef = np.polyfit(my_array[i], y, 3)
#         coef1 = list(reversed(coef))
#         coefficients.append(coef)
#         coefficients1.append(coef1)
#
# print(coefficients)
# print("********************************************")
# print(coefficients1)
# print("********************************************")
# for i in range(14):
#     print(coefficients1[i])


# import wx
#
#
# class MainFrame(wx.Frame):
#     def __init__(self, parent, title):
#         super(MainFrame, self).__init__(parent, title=title, size=(400, 300))
#
#         self.data = None  # 用于存储面板1获取的数据
#
#         self.panel1 = Panel1(self)
#         self.panel2 = Panel2(self)
#
#         self.panel2.Hide()
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#         sizer.Add(self.panel1, 1, wx.EXPAND)
#         sizer.Add(self.panel2, 1, wx.EXPAND)
#
#         self.SetSizer(sizer)
#         self.Centre()
#
#         self.current_panel = self.panel1
#
#     def switch_panel(self, new_panel):
#         self.current_panel.Hide()
#         new_panel.Show()
#         self.current_panel = new_panel
#         self.Layout()
#
#     def set_data(self, data):
#         self.data = data
#
#     def get_data(self):
#         return self.data
#
#
# class Panel1(wx.Panel):
#     def __init__(self, parent):
#         super(Panel1, self).__init__(parent)
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#
#         label = wx.StaticText(self, label="This is Panel 1")
#         self.text_ctrl = wx.TextCtrl(self, value="")
#         button = wx.Button(self, label="Go to Panel 2")
#         button.Bind(wx.EVT_BUTTON, self.on_button_click)
#
#         sizer.Add(label, 0, wx.ALL | wx.CENTER, 10)
#         sizer.Add(self.text_ctrl, 0, wx.ALL | wx.CENTER, 10)
#         sizer.Add(button, 0, wx.ALL | wx.CENTER, 10)
#
#         self.SetSizer(sizer)
#
#     def on_button_click(self, event):
#         data = self.text_ctrl.GetValue()
#         self.GetParent().set_data(data)
#         self.GetParent().panel2.update_data()
#         self.GetParent().switch_panel(self.GetParent().panel2)
#
#
# class Panel2(wx.Panel):
#     def __init__(self, parent):
#         super(Panel2, self).__init__(parent)
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#
#         self.label = wx.StaticText(self, label="This is Panel 2")
#         self.data_label = wx.StaticText(self, label="")
#         button = wx.Button(self, label="Go to Panel 1")
#         button.Bind(wx.EVT_BUTTON, self.on_button_click)
#
#         sizer.Add(self.label, 0, wx.ALL | wx.CENTER, 10)
#         sizer.Add(self.data_label, 0, wx.ALL | wx.CENTER, 10)
#         sizer.Add(button, 0, wx.ALL | wx.CENTER, 10)
#
#         self.SetSizer(sizer)
#
#     def on_button_click(self, event):
#         self.GetParent().switch_panel(self.GetParent().panel1)
#
#     def update_data(self):
#         data = self.GetParent().get_data()
#         self.data_label.SetLabel(f"Data from Panel 1: {data}")
#
#
# class MyApp(wx.App):
#     def OnInit(self):
#         frame = MainFrame(None, title="Panel Switch Example")
#         frame.Show()
#         return True
#
#
# if __name__ == '__main__':
#     app = MyApp()
#     app.MainLoop()



