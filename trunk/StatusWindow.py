
import time
import wx

class StatusWindow(wx.Window):

    def __init__(self, parent, pos, size):
        wx.Window.__init__(self, parent, -1, pos, size)
        self.text = wx.TextCtrl(self, -1, style=(wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB))
        wx.EVT_TEXT_ENTER(self.text, -1, self.OnEnter)
        self.static = wx.StaticText(self, -1, '')
        self.ShowText(False)
        self.command = None

    def PassCommand(self, cmd):
        self.ShowText(True)
        self.command = cmd
        self.text.SetFocus()

    def OnEnter(self, evt):
        par = self.text.GetValue()
        self.command(par, self)
        self.ShowText(False)

    def ShowText(self, show=True):
        self.text.Show(show)
        self.static.Show(not show)

    def SetText(self, text):
        self.static.SetLabel(text)

def create(parent, pos, size):
    return StatusWindow(parent, pos, size)
        
