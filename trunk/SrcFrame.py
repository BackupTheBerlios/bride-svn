"""Class for the frame holding the source document.

"""

import os.path
import wx
import SrcCtrl

class SrcFrame(wx.Window):
    def __init__(self, parent, id, filename=None):
        wx.Window.__init__(self, parent, id)
        self.filename = None
        self.parent = parent
        self.text = SrcCtrl.create(self, -1, '', 
                                   style=(wx.TE_MULTILINE | wx.TE_RICH2))
        wx.EVT_TEXT(self, self.text.GetId(), self.OnChange)
        self.text.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        if filename:
            self.Open(filename)

    def Open(self, filename):
        self.filename = filename
        self.text.LoadFile(filename)

    def Save(self, filename=None):
        if filename:
            self.filename = filename
        if self.filename:
            self.text.SaveFile(self.filename)
        else:
            raise ValueError, 'no value for the filename'

    def Close(self):
        raise NotImplementedError

    def OnChange(self, evt):
        pass

    def OnLeftDown(self, evt):
        evt.Skip()
        wx.CallAfter(self.LogPosition, evt)

    def LogPosition(self, evt):
        x, y = self.text.PositionToXY(self.text.GetInsertionPoint())
        self.parent.GetParent().SetStatusText('ROW = %d | COL = %d' % (x, y+1))

def create(ws, filename=None):
    win = SrcFrame(ws.book, -1, filename) 
    if filename:
        title = os.path.basename(filename)
    else:
        title = '[new]*'
    ws.book.AddPage(win, title, True)
    win.text.SetFocus()
