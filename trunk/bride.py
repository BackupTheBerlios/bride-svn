"""Main application.

"""

__version__ = 0.1

import optparse, os, cPickle
import wx
import SrcFrame, StatusWindow

ID_GOTO = 6000
ID_SEARCH = 6001
ID_REPLACE = 6002
ID_RECENT = 6003
ID_RECENT_FILES = 6004 # skip to 6014 (10 empty slots)

class Workspace(wx.Frame):
    def __init__(self, parent, cfgdir):
        title = 'brIDE - v. %s' % __version__
        wx.Frame.__init__(self, parent, -1, title, (-1,-1), (800,600))
        self.book = wx.Notebook(self, -1, size=(800,550))
        self.statwin = StatusWindow.create(self, (0,550), (800,50))
        self.clip = ''
        try:
            f = open(cfgdir+'recent.pick')
        except IOError:
            self.recent = []
        else:
            self.recent = cPickle.load(f)
        self.cfgdir = cfgdir
        self.InitMenu()

    def InitMenu(self):
        mbar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, '&New')
        wx.EVT_MENU(self, wx.ID_NEW, self.OnNew)
        file_menu.Append(wx.ID_OPEN, '&Open...')
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpen)
        file_menu.Append(wx.ID_SAVE, '&Save')
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSave)
        file_menu.Append(wx.ID_SAVEAS, 'Save as...')
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveAs)
        file_menu.AppendSeparator()
        recent = wx.Menu()
        for i, f in enumerate(self.recent[::-1]):
            recent.Append(ID_RECENT_FILES+i, f)
            wx.EVT_MENU(self, ID_RECENT_FILES+i, self.OnOpenRecent)
        file_menu.AppendMenu(ID_RECENT, '&Recent', recent)
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_CLOSE, '&Close')
        wx.EVT_MENU(self, wx.ID_CLOSE, self.OnClose)
        file_menu.Append(wx.ID_CLOSE_ALL, 'Close all')
        wx.EVT_MENU(self, wx.ID_CLOSE_ALL, self.OnCloseAll)
        file_menu.Append(wx.ID_EXIT, 'E&xit')
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnExit)
        mbar.Append(file_menu, '&File')
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_UNDO, 'Undo')
        wx.EVT_MENU(self, wx.ID_UNDO, self.OnUndo)
        edit_menu.Append(wx.ID_REDO, 'Redo')
        wx.EVT_MENU(self, wx.ID_REDO, self.PostToActive)
        edit_menu.AppendSeparator()
        edit_menu.Append(wx.ID_CUT, 'Cut')
        wx.EVT_MENU(self, wx.ID_CUT, self.OnCut)
        edit_menu.Append(wx.ID_COPY, 'Copy')
        wx.EVT_MENU(self, wx.ID_COPY, self.OnCopy)
        edit_menu.Append(wx.ID_PASTE, 'Paste')
        wx.EVT_MENU(self, wx.ID_PASTE, self.OnPaste)
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_GOTO, 'Go to line')
        wx.EVT_MENU(self, ID_GOTO, self.OnGoto)
        edit_menu.Append(ID_SEARCH, 'Search')
        wx.EVT_MENU(self, ID_SEARCH, self.OnSearch)
        edit_menu.Append(ID_REPLACE, 'Replace')
        wx.EVT_MENU(self, ID_REPLACE, self.OnReplace)
        mbar.Append(edit_menu, '&Edit')
        self.SetMenuBar(mbar)

    def OnExit(self, evt):
        if self.OnCloseAll(evt):
            try:
                f = open(self.cfgdir+'recent.pick', 'w')
            except IOError:
                print 'error saving recent files list'
            else:
                cPickle.dump(self.recent, f)
            self.Close()

    def OnNew(self, evt):
        SrcFrame.create(self)

    def OnOpen(self, evt):
        filename = wx.FileSelector('Open file', '', '', '',
                                   'python files (*.py)|*.py',
                                   wx.OPEN, self)
        if filename != '':
            self.Load(filename)
            
    def OnOpenRecent(self, evt):
        self.Load(self.recent[evt.GetId()-ID_RECENT_FILES])

    def Load(self, filename):
        SrcFrame.create(self, filename)
        if filename in self.recent:
            self.recent.remove(filename)
        self.recent.append(filename)
        
    def OnSave(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            page = self.book.GetPage(sel)
            if page.filename:
                page.Save()
            else:
                self.OnSaveAs(evt)

    def OnSaveAs(self, evt): 
        filename = wx.FileSelector('Save file', '', '', 'py',
                                   'python files (*.py)|*.py',
                                   wx.SAVE, self)
        if filename != '':
            sel = self.book.GetSelection()
            if sel != -1:
                self.book.GetPage(sel).Save(filename)

    def ClosePage(self, index):
        if self.book.GetPage(index).text.IsModified():
            return False
        else:
            success = self.book.DeletePage(index)
            self.book.SetSelection(0)
            return success

    def OnClose(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.ClosePage(sel)

    def OnCloseAll(self, evt):
        while self.book.GetPageCount() != 0:
            if not self.ClosePage(0):
                print 'some of the docs have not been save before'
                return False
        return True

    def OnUndo(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            if self.book.GetPage(sel).text.CanUndo():
                self.book.GetPage(sel).text.Undo()
            else:
                print 'No Undo available'

    def OnCut(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.clip = self.book.GetPage(sel).text.Copy(True)

    def OnCopy(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.clip = self.book.GetPage(sel).text.Copy()

    def OnPaste(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.clip = self.book.GetPage(sel).text.Paste(self.clip)

    def OnGoto(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.statwin.PassCommand(self.book.GetPage(sel).text.Goto)

    def OnSearch(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.statwin.PassCommand(self.book.GetPage(sel).text.Search)

    def OnReplace(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            dlg = wx.TextEntryDialog(self, 'Replace')
            if dlg.ShowModal() == wx.ID_OK:
                sub = dlg.GetValue()
                dlg = wx.TextEntryDialog(self, "Replace '%s' with" % sub)
                if dlg.ShowModal() == wx.ID_OK:
                    rep = dlg.GetValue()
                    self.book.GetPage(sel).text.OnReplace(sub, rep)

    def PostToActive(self, evt):
        wx.PostEvent(self.GetActiveChild().text, evt)

    def SetStatusText(self, text):
        self.statwin.SetText(text)

class Bride(wx.App):
    """Application class.

    """
    
    def __init__(self, files, cfgdir):
        """Constructor.

        The arguments are needed by OnInit():
        @param files: a files of files to be loaded on initialization.
        @param cfgdir: path to the configuration directory.
        """
        self.initargs = (files, cfgdir)
        wx.App.__init__(self)

    def OnInit(self):
        """Called on initialization.

        Checks the configuration directory, creates the workspace, and
        loads eventual files for editing.
        """
        files, cfgdir = self.initargs
        self.checkdir(cfgdir)
        ws = Workspace(None, cfgdir)
        for f in files:
            ws.Load(f)
        ws.Show(True)
        return True

    def checkdir(self, dir):
        """Checks if a directory is writable and eventually creates it.

        @param dir: Directory to check.
        """
        if not os.access(dir, os.W_OK):
            try:
                os.mkdir(dir)
            except OSError, e:
                print e
                print 'Error creating dir', dir
                raise e

    def OnExit(self):
        print 'exit'

def parse_cl():
    """Parse the command line.

    """
    parser = optparse.OptionParser(usage="usage: %prog [options] <file list>")
    parser.add_option("-c", dest="cfgdir", default=None, metavar="PATH",
                      help="set config. dir to PATH (defaults to ~/.bride")
    (opts, args) = parser.parse_args()
    if opts.cfgdir == None:
        opts.cfgdir = os.environ.get('HOME') + '/.bride/'
    return (opts, args)

if __name__=='__main__':
    (opts, args) = parse_cl()
    print 'Using wxPython version', wx.__version__
    app = Bride(args, opts.cfgdir)
    app.MainLoop()
