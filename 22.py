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


# import numpy as np
#
# # 生成一些示例数据
# x = np.array([0, 1, 2, 3, 4])
# y = np.array([1.1, 2.0, 2.9, 4.2, 5.1])
#
# # 进行一次多项式拟合
# coefficients = np.polyfit(x, y, 3)
#
# # 打印拟合的系数
# print(coefficients)



import numpy as np
import random


Std_nongdu = [0, 5000, 10000, 30000, 80000, 120000, 200000]
data_0 = []
data_05 = []
data_1 = []
data_3 = []
data_8 = []
data_12 = []
data_20 = []

y = np.array(Std_nongdu)
def shuzu(shuzu):
    for _ in range(16):
        shuzu.append(random.randint(1, 100))

shuzu(data_0)
shuzu(data_05)
shuzu(data_1)
shuzu(data_3)
shuzu(data_8)
shuzu(data_12)
shuzu(data_20)

print(data_0)
print(data_05)
print(data_1)
print(data_3)
print(data_8)
print(data_12)
print(data_20)

com_matrix = np.zeros((16, 7))
fit_coefficients_matrix = np.zeros((16, 4))
print(com_matrix)

for i in range(16):
    com_matrix[i][0] = data_0[i]
    com_matrix[i][1] = data_05[i]
    com_matrix[i][2] = data_1[i]
    com_matrix[i][3] = data_3[i]
    com_matrix[i][4] = data_8[i]
    com_matrix[i][5] = data_12[i]
    com_matrix[i][6] = data_20[i]
print(com_matrix)

for i in range(16):
    fit_coefficients_matrix[i] = np.polyfit(com_matrix[i], y, 3)
print(fit_coefficients_matrix)
print(len(fit_coefficients_matrix[0]))

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



