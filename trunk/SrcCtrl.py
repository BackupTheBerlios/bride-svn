"""Control class for source.

"""

import wx

class SrcCtrl(wx.TextCtrl):
    def __init__(self, parent, id, text, sty):
        wx.TextCtrl.__init__(self, parent, id, text, style=sty)
        self.clip = ''
        self.frame = parent

    def Copy(self, cut=False):
        text = self.GetStringSelection()
        if cut:
            a, b = self.GetSelection()
            self.Remove(a, b)
        return text

    def Paste(self, text):
        a, b = self.GetSelection()
        self.Replace(a, b, text)

    def Goto(self, line):
        self.SetInsertionPoint(self.XYToPosition(0, int(line)-1))
        self.SetFocus()

    def Search(self, text):
        pos = self.GetValue().find(text, self.GetInsertionPoint())
        if pos != -1:
            self.SetSelection(pos, pos+len(text))
            self.SetFocus()
        else:
            pos = self.GetValue().find(text, 0, self.GetInsertionPoint())
            if pos != -1:
                self.SetSelection(pos, pos+len(text))
                self.SetFocus()

    def OnReplace(self, sub, rep):
        handler = lambda evt: self.ReplaceEvtHandler(evt, sub, rep)
        self.Bind(wx.EVT_KEY_DOWN, handler)
        self.Search(sub)

    def ReplaceEvtHandler(self, evt, sub, rep):
        kc = evt.GetKeyCode()
        if kc == wx.WXK_ESCAPE:
            pos = self.GetInsertionPoint()
            self.SetSelection(pos, pos)
            self.Unbind(wx.EVT_KEY_DOWN)
        elif kc == wx.WXK_SPACE:
            a, b = self.GetSelection()
            self.Replace(a, b, rep)
            self.Search(sub)
        elif kc == 78: # ASCII code for 'n'
            self.Search(sub)
        elif kc == 65: # ASCII code for 'a'
            a, b = self.GetSelection()
            while a != b:
                self.Replace(a, b, rep)
                self.Search(sub)
                a, b = self.GetSelection()

def create(parent, id, text, style):
    return SrcCtrl(parent, id, text, style)
