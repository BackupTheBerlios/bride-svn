"""Main application.

"""

__version__ = 0.1

import optparse, os, cPickle
import wx
import SrcFrame, StatusWindow

try:
    from IPython.Shell import IPShellWX
except ImportError, e:
    print 'IPython support disabled'
else:
    __HAS_IPYTHON__ = True
    import IPythonFrame

ID_GOTO = 6000
ID_SEARCH = 6001
ID_REPLACE = 6002
ID_RECENT = 6003
ID_RECENT_FILES = 6004 # skip to 6014 (10 empty slots)
ID_IPYTHON = 6014

class Workspace(wx.Frame):
    def __init__(self, app):
        title = 'brIDE - v. %s' % __version__
        wx.Frame.__init__(self, None, -1, title, (-1,-1), (800,600))
        self.book = wx.Notebook(self, -1, size=(800,550))
        self.statwin = StatusWindow.create(self, (0,550), (800,50))
        self.clip = ''
        self.recent = app.recent
        self.InitMenu()

    def InitMenu(self):
        menu = [('&File', (('&New', wx.ID_NEW, self.OnNew),
                           ('&Open', wx.ID_OPEN, self.OnOpen),
                           ('&Save', wx.ID_SAVE, self.OnSave),
                           ('Save as...', wx.ID_SAVEAS, self.OnSaveAs),
                           None,
                           ('&Close', wx.ID_CLOSE, self.OnClose),
                           ('Close all', wx.ID_CLOSE_ALL, self.OnCloseAll),
                           ('E&xit', wx.ID_EXIT, self.OnExit))),
                ('&Edit', (('Undo', wx.ID_UNDO, self.OnUndo),
                           ('Redo', wx.ID_REDO, self.OnRedo),
                           None,
                           ('Cut', wx.ID_CUT, self.OnCut),
                           ('Copy', wx.ID_COPY, self.OnCopy),
                           ('Paste', wx.ID_PASTE, self.OnPaste),
                           None,
                           ('Goto...', ID_GOTO, self.OnGoto),
                           ('Search...', ID_SEARCH, self.OnSearch),
                           ('Replace...', ID_REPLACE, self.OnReplace)))]
        if __HAS_IPYTHON__:
            menu.append(('&Tools', (('IPython', ID_IPYTHON, self.OnIPython),)))
        mbar = wx.MenuBar()
        self._populate_menubar(mbar, menu)
        recent = wx.Menu()
        for i, f in enumerate(self.recent[::-1]):
            recent.Append(ID_RECENT_FILES+i, os.path.basename(f))
            wx.EVT_MENU(self, ID_RECENT_FILES+i, self.OnOpenRecent)
        mbar.GetMenu(0).AppendSeparator()
        mbar.GetMenu(0).AppendMenu(ID_RECENT, '&Recent', recent)
        self.SetMenuBar(mbar)

    def _populate_menubar(self, mbar, hierarchy):
        for m in hierarchy:
            menu = wx.Menu()
            self._populate_menu(menu, m[1])
            mbar.Append(menu, m[0])

    def _populate_menu(self, menu, items):
        for i in items:
            if i == None:
                menu.AppendSeparator()
            else:
                menu.Append(i[1], i[0])
                wx.EVT_MENU(self, i[1], i[2])
                
    def OnIPython(self, evt):
        if __HAS_IPYTHON__:
            ipshell = IPShellWX()
            ipshell.run()
            #IPythonFrame.create(self)
        else:
            pass

    def OnExit(self, evt):
        if self.OnCloseAll(evt):
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
        self.Load(self.recent[ID_RECENT_FILES-evt.GetId()-1])

    def Load(self, filename):
        SrcFrame.create(self, filename)
        absname = os.path.abspath(filename)
        if absname in self.recent:
            self.recent.remove(absname)
        self.recent.append(absname)
        
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
        if self.book.GetPage(index).IsModified():
            return False
        else:
            success = self.book.DeletePage(index)
            if self.book.GetPageCount() > 0:
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

    def OnRedo(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            if self.book.GetPage(sel).text.CanRedo():
                self.book.GetPage(sel).text.Redo()
            else:
                print 'No Redo available'

    def OnCut(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.clip = self.book.GetPage(sel).text.Cut()

    def OnCopy(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.clip = self.book.GetPage(sel).text.Copy()

    def OnPaste(self, evt):
        sel = self.book.GetSelection()
        if sel != -1:
            self.clip = self.book.GetPage(sel).text.Paste()

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
        self._check_dir(cfgdir)
        self.cfgdir = cfgdir
        self._load_recent()
        ws = Workspace(self)
        for f in files:
            ws.Load(f)
        ws.Show(True)
        return True

    def _load_recent(self):
        """Loads list of recent files.

        """
        try:
            f = open(self.cfgdir+'recent.pick')
        except IOError:
            self.recent = []
        else:
            self.recent = cPickle.load(f)

    def _save_recent(self):
        """Saves list of recent files.

        """
        try:
            f = open(self.cfgdir+'recent.pick', 'w')
        except IOError:
            print 'error saving recent files list'
        else:
            cPickle.dump(self.recent, f)
        
    def _check_dir(self, dir):
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
        """Clean up before exiting.

        It saves the lists of recent files.
        """
        self._save_recent()

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
