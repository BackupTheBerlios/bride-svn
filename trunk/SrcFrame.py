"""Class for the frame holding the source document.

"""

import os.path
import wx
import wx.stc as stc
import SrcCtrl

class SrcFrame(wx.Window):
    def __init__(self, parent, id, filename=None):
        wx.Window.__init__(self, parent, id, wx.DefaultPosition, parent.GetSize())
        self.filename = None
        self.parent = parent
        self.text = SrcCtrl.create(self, -1)
        wx.EVT_TEXT(self, self.text.GetId(), self.OnChange)
        self.text.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        if filename:
            self.Open(filename)

    def Open(self, filename):
        """Loads a file.

        This can raise an IOError.
        """
        self.filename = filename
        self.text.SetText(open(filename).read())
        self.text.EmptyUndoBuffer()
        self.text.Colourise(0, -1)
        self.text.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.text.SetMarginWidth(1, 25)

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

    def IsModified(self):
        return False

def create(ws, filename=None):
    win = SrcFrame(ws.book, -1, filename) 
    if filename:
        title = os.path.basename(filename)
    else:
        title = '[new]*'
    ws.book.AddPage(win, title, True)
    win.text.SetFocus()
