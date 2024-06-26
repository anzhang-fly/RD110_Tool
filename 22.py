import wx
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None,title="盒子布局",size=(400,300))
        panel=wx.Panel(parent=self)
        self.statictext=wx.StaticText(parent=panel,label='请单击OK！')
        b=wx. Button(parent=panel,label='OK')
        self.Bind(wx.EVT_BUTTON,self.on_click,b)
        vbox=wx.BoxSizer(wx.VERTICAL) #垂直方向布局
        vbox.Add(self.statictext,proportion=1,
                 flag=wx.ALIGN_CENTER_HORIZONTAL|wx.FIXED_MINSIZE|wx.TOP,
                 border=50)
        vbox.Add(b,proportion=1,flag=wx.EXPAND|wx.BOTTOM,border=10)
        panel.SetSizer(vbox)
    def on_click(self,event):
        self.statictext.SetLabelText('Hello World!')
app = wx.App()
frm=MyFrame()
frm.Show()
app.MainLoop()