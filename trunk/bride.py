"""Main application.

"""

__version__ = 0.1

import optparse, os, cPickle
import wx
import StatusWindow, SrcCtrl

try:
    from IPython.Shell import IPShellWX
except ImportError, e:
    print 'IPython support disabled'
    __HAS_IPYTHON__ = False
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
    """Class implementing the workspace of the IDE.

    """
    def __init__(self, app):
        """Constructor.

        Creates the frames and menus.
        """
        title = 'brIDE - v. %s' % __version__
        wx.Frame.__init__(self, None, -1, title)
        self.book = wx.Notebook(self, -1)
        self.statwin = StatusWindow.create(self, (0,550), (800,50))
        self.recent = app.recent
        self.InitMenu()
        self.InitSizer()
        self.SetSize((800, 600))

    def InitSizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.book, 1, wx.EXPAND)
        sizer.Add(self.statwin, 0, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)

    ######### MENU MANAGEMENT ################

    def InitMenu(self):
        """Initializes the menus.

        The menu structure is defined and passed to _populate_menubar().
        The menu with the recent files is still handled statically by
        _add_recent_menu().
        """
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
        self._add_recent_menu(mbar)
        self.SetMenuBar(mbar)
        self.EnableMenuCommands(False)

    def EnableMenuCommands(self, enable):
        """Enables the menu items connected to documents operations.

        """
        mbar = self.GetMenuBar()
        hierarchy = (('File', ('Close', 'Close all', 'Save', 'Save as...')),
                     ('Edit', None))
        for m in hierarchy:
            if m[1] == None:
                mbar.EnableTop(mbar.FindMenu(m[0]), enable)
            else:
                menu = mbar.GetMenu(mbar.FindMenu(m[0]))
                for i in m[1]:
                    item = menu.FindItem(i)
                    menu.Enable(item, enable)

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

    def _add_recent_menu(self, mbar):
        recent = wx.Menu()
        for i, f in enumerate(self.recent[::-1]):
            recent.Append(ID_RECENT_FILES+i, os.path.basename(f))
            wx.EVT_MENU(self, ID_RECENT_FILES+i, self.OnOpenRecent)
        mbar.GetMenu(0).AppendSeparator()
        mbar.GetMenu(0).AppendMenu(ID_RECENT, '&Recent', recent)
                
    ######### FILE MENU COMMANDS ################
        
    def OnNew(self, evt):
        SrcCtrl.create(self)

    def OnOpen(self, evt):
        filename = wx.FileSelector('Open file', '', '', '',
                                   'python files (*.py)|*.py',
                                   wx.OPEN, self)
        if filename != '':
            self.Load(filename)
            
    def OnSave(self, evt):
        page = self.GetSelectedPage()
        if page.filename:
            page.Save()
        else:
            self.OnSaveAs(evt)

    def OnSaveAs(self, evt):
        filename = wx.FileSelector('Save file', '', '', 'py',
                                   'python files (*.py)|*.py',
                                   wx.SAVE, self)
        if filename != '':
            self.GetSelectedPage().Save(filename)

    def OnClose(self, evt):
        self.ClosePage(self.book.GetSelection())

    def OnCloseAll(self, evt):
        while self.book.GetPageCount() != 0:
            if not self.ClosePage(0):
                print 'some of the docs have not been saved before'
                return False
        return True

    def OnExit(self, evt):
        if self.OnCloseAll(evt):
            self.Close()

    def OnOpenRecent(self, evt):
        self.Load(self.recent[ID_RECENT_FILES-evt.GetId()-1])

    ######### EDIT MENU COMMANDS ################

    def OnUndo(self, evt):
        text = self.GetSelectedPage().text
        if text.CanUndo():
            text.Undo()

    def OnRedo(self, evt):
        text = self.GetSelectedPage().text
        if text.CanRedo():
            text.Redo()

    def OnCut(self, evt):
        self.GetSelectedPage().text.Cut()

    def OnCopy(self, evt):
        self.GetSelectedPage().text.Copy()

    def OnPaste(self, evt):
        self.GetSelectedPage().text.Paste()

    def OnGoto(self, evt):
        text = self.GetSelectedPage().text
        self.statwin.PassCommand(text.Goto)

    def OnSearch(self, evt):
        text = self.GetSelectedPage().text
        self.statwin.PassCommand(text.Search)

    def OnReplace(self, evt):
        dlg = wx.TextEntryDialog(self, 'Replace')
        if dlg.ShowModal() == wx.ID_OK:
            sub = dlg.GetValue()
            dlg = wx.TextEntryDialog(self, "Replace '%s' with" % sub)
            if dlg.ShowModal() == wx.ID_OK:
                rep = dlg.GetValue()
                self.GetSelectedPage().text.OnReplace(sub, rep)

    ######### TOOLS MENU COMMANDS ################

    def OnIPython(self, evt):
        """Creates a page with an IPython shell.

        Still under construction.
        """
        if __HAS_IPYTHON__:
            ipshell = IPShellWX()
            ipshell.run()
            #IPythonFrame.create(self)
        else:
            pass
        
    ######### OTHERS METHODS ################

    def Load(self, filename):
        SrcCtrl.create(self, filename)
        self.EnableMenuCommands(True)
        absname = os.path.abspath(filename)
        if absname in self.recent:
            self.recent.remove(absname)
        self.recent.append(absname)

    def GetSelectedPage(self):
        return self.book.GetPage(self.book.GetSelection())
        
    def ClosePage(self, index):
        if self.book.GetPage(index).IsModified():
            return False
        else:
            success = self.book.DeletePage(index)
            if self.book.GetPageCount() > 0:
                self.book.SetSelection(0)
            else:
                self.EnableMenuCommands(False)
            return success

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
