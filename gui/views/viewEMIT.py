__author__ = 'Mario'
from gui.controller.logicDirectory import LogicDirectory
from gui.controller.logicToolbox import LogicToolbox
from gui.controller.logicCanvas import LogicCanvas
import wx
import wx.html2
from wx.lib.pubsub import pub as Publisher
import wx.lib.agw.aui as aui
from gui import events
from wx.lib.newevent import NewEvent
from coordinator.emitLogging import elog
from viewLowerPanel import viewLowerPanel
import os

# create custom events
wxCreateBox, EVT_CREATE_BOX = NewEvent()
wxStdOut, EVT_STDDOUT= NewEvent()
wxDbChanged, EVT_DBCHANGED= NewEvent()


class ViewEMIT(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Environmental Model Integration Project", pos=wx.DefaultPosition,
                          size=wx.Size(1200, 750), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.pnlDocking = wx.Panel(id=wx.ID_ANY, name='pnlDocking', parent=self, size=wx.Size(1200, 750),
                                   style=wx.TAB_TRAVERSAL)
        self.bnb = wx.Notebook(self.pnlDocking)
        lowerpanel = viewLowerPanel(self.bnb)

        self.parent = parent

        self.initMenu()

        # creating components
        self.Directory = LogicDirectory(self.pnlDocking)
        self.Toolbox = LogicToolbox(self.pnlDocking)
        self.Canvas = LogicCanvas(self.pnlDocking)

        self.Toolbox.Hide()
        self.initAUIManager()
        self._init_sizers()

        self.filename = None
        self.loadingpath = None

        self.Center()

        self.Show()


    def _init_sizers(self):
        self.s = wx.BoxSizer(wx.VERTICAL)
        self.s.AddWindow(self.pnlDocking, 85, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.s)


    def initAUIManager(self):

        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow(self.pnlDocking)

        self.m_mgr.AddPane(self.Canvas,
                           aui.AuiPaneInfo().
                           Center().
                           Name("Canvas").
                           CloseButton(False).
                           MaximizeButton(False).
                           MinimizeButton(False).
                           Floatable(False).
                           BestSize(wx.Size(1000, 400))
        )

        self.m_mgr.AddPane(self.Directory,
                           aui.AuiPaneInfo().
                           Left().
                           Dock().
                           CloseButton(False).
                           MaximizeButton(False).
                           MinimizeButton(False).
                           PinButton(False).
                           BestSize(wx.Size(275, 400)).
                           Floatable(False).
                           Movable(False).
                           Show(show=False).Hide()
                           )

        self.m_mgr.AddPane(self.Toolbox,
                           aui.AuiPaneInfo().
                           Left().
                           Dock().
                           Name("Toolbox").
                           CloseButton(False).
                           MaximizeButton(False).
                           MinimizeButton(False).
                           PinButton(False).
                           BestSize(wx.Size(275, 400)).
                           Floatable(False).
                           Movable(False).
                           Show(show=True)
                           )

        self.m_mgr.AddPane(self.bnb,
                           aui.AuiPaneInfo().
                           Bottom().
                           Name("Console").
                           CloseButton(False).
                           MaximizeButton(False).
                           MinimizeButton(False).
                           PinButton(False).
                           Movable(False).
                           Floatable(False).
                           BestSize(wx.Size(1200, 225)).CaptionVisible(False)
                           )

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnSelect)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.m_mgr.Update()

        self._default_perspective = self.m_mgr.SavePerspective()

    # def OnPageChange(self, page):
    #
    #     index = self.notebook_pages[page]
    #     self.bnb.SetSelection(index)

    def OnSelect(self, event):

        try:
            # update databases in a generic way
            selected_page = self.bnb.GetPage(event.GetSelection())
            if len(selected_page.connection_combobox.GetItems()) == 0:
                 selected_page.refreshConnectionsListBox()

        except: pass

    def initMenu(self):
        ## Menu stuff
        #self.m_statusBar2 = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)

        self.m_menubar = wx.MenuBar()

        self.m_fileMenu = wx.Menu()
        #exit = wx.MenuItem(self.m_fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        Load = self.m_fileMenu.Append(wx.NewId(), '&Load\tCtrl+O', 'Load Configuration')
        Save = self.m_fileMenu.Append(wx.NewId(), '&Save Configuration\tCtrl+S', 'Save Configuration')
        SaveAs = self.m_fileMenu.Append(wx.NewId(), '&Save Configuration As', 'Save Configuration')
        Settings = self.m_fileMenu.Append(wx.NewId(), "Settings...")
        exit = self.m_fileMenu.Append(wx.NewId(), '&Quit\tCtrl+Q', 'Quit application')

        self.m_menubar.Append(self.m_fileMenu, "&File")

        self.m_toolMenu = wx.Menu()
        # self.m_menubar.Append(self.m_toolMenu, "&Tools")


        self.m_viewMenu = wx.Menu()
        ShowAll = self.m_viewMenu.Append(wx.NewId(), '&Toolbox\tCtrl+A', 'Show all associated files', wx.ITEM_RADIO)
        ShowDir = self.m_viewMenu.Append(wx.NewId(), '&Directory\tCtrl+D', 'Shows file directory', wx.ITEM_RADIO)
        separator = self.m_viewMenu.Append(wx.NewId(), 'separate', 'separate', wx.ITEM_SEPARATOR)
        MinimizeConsole = self.m_viewMenu.Append(wx.NewId(), '&Console Off', 'Minimizes the Console', wx.ITEM_CHECK)

        defaultview = self.m_viewMenu.Append(wx.NewId(), '&Default View', 'Returns the view to the default (inital) state', wx.ITEM_NORMAL)

        self.m_menubar.Append(self.m_viewMenu, "&View")

        self.m_optionMenu = wx.Menu()
        self.m_menubar.Append(self.m_optionMenu, "Options")
        ShowSim = self.m_optionMenu.Append(wx.NewId(), 'Show Configurations', 'Shows the saved configurations files in the toolbox', wx.ITEM_RADIO)
        HideSim = self.m_optionMenu.Append(wx.NewId(), 'Hide Configurations', 'Only shows Hydrology models in the toolbox', wx.ITEM_RADIO)


        self.m_runMenu = wx.Menu()
        self.applicationRun = self.m_runMenu.Append(wx.NewId(), '&Run Configuration', 'Runs the existing configurations')
        separator = self.m_runMenu.Append(wx.NewId(), 'separate', 'separate', wx.ITEM_SEPARATOR)
        databaseSave = self.m_runMenu.Append(wx.NewId(), '&Save Results to Database', 'Saves the result to the default database', wx.ITEM_CHECK)
        viewResult = self.m_runMenu.Append(wx.NewId(), '&View Results', 'View the result', wx.ITEM_CHECK)
        viewResult.Check()
        self.m_menubar.Append(self.m_runMenu, "&Run")

        self.SetMenuBar(self.m_menubar)

        wx.CallAfter(self._postStart)

        ## Events
        # View Option Bindings
        self.Bind(wx.EVT_MENU, self.SaveConfiguration, Save)
        self.Bind(wx.EVT_MENU, self.SaveConfigurationAs, SaveAs)
        self.Bind(wx.EVT_MENU, self.LoadConfiguration, Load)
        self.Bind(wx.EVT_MENU, self.Settings, Settings)
        self.Bind(wx.EVT_MENU, self.onClose, exit)
        events.onSaveFromCanvas += self.SaveConfigurationAs

        # View Option Bindings
        self.Bind(wx.EVT_MENU, self.onDirectory, ShowDir)
        self.Bind(wx.EVT_MENU, self.onAllFiles, ShowAll)
        self.Bind(wx.EVT_MENU, self.onConsole, MinimizeConsole)
        self.Bind(wx.EVT_MENU, self.defaultview, defaultview)


        # Run Option Bindings
        self.Bind(wx.EVT_MENU_OPEN, self.onRunSelected)

    def Settings(self, event):
        settings = viewMenuBar()
        settings.Show()
        pass

    def onRunSelected(self, event):
        if event.GetMenu() == self.m_runMenu:
            print len(self.Canvas.links)
            if len(self.Canvas.links) > 0:
                self.applicationRun.Enable(True)
            else:
                self.applicationRun.Enable(False)

    def onClose(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Question',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

    def defaultview(self, event):
        """
        Restore previously saved perspective
        """
        self.m_mgr.LoadPerspective(self._default_perspective)


    def _postStart(self):
        ## Starts stuff after program has initiated
        self.Canvas.ZoomToFit(event=None)

    def __del__(self):
        self.m_mgr.UnInit()

    def LoadConfiguration(self,event):

        openFileDialog = wx.FileDialog(self, "Load New File", "", "",
                                       "Simulation Files (*.sim)|*.sim|MDL Files (*.mdl)|*.mdl", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_OK:
            filename = openFileDialog.GetFilename()
            elog.info("Filename is: " + filename)
            # proceed loading the file chosen by the user
            # this can be done with e.g. wxPython input streams:
            filepath = (openFileDialog.GetPath())
            try:
                Publisher.sendMessage('SetLoadPath',file=filepath)  # send message to canvascontroller
            except:
                elog.error("Could not load file")

            self.filename = openFileDialog.GetFilename()
            self.loadingpath = filepath

    def SaveConfiguration(self,event):
        if self.loadingpath == None:
            save = wx.FileDialog(self.Canvas.GetTopLevelParent(), "Save Configuration","","",
                                 "Simulation Files (*.sim)|*.sim", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

            if save.ShowModal() == wx.ID_OK:
                self.save_path = save.GetPath() + ".sim"
            else:
                save.Destroy()

            Publisher.sendMessage('SetSavePath',path=save.GetPath()) #send message to canvascontroller.SaveSimulation

            self.loadingpath = save.GetPath()
        else:
            Publisher.sendMessage('SetSavePath', path=self.loadingpath)

    def SaveConfigurationAs(self,event):
        # Executes from File ->Save As
        save = wx.FileDialog(self.Canvas.GetTopLevelParent(), "Save Configuration","","",
                             "Simulation Files (*.sim)|*.sim", wx.FD_SAVE  | wx.FD_OVERWRITE_PROMPT)

        if save.ShowModal() == wx.ID_OK:
            self.save_path = save.GetPath()
            if self.save_path[-4] != '.':  # check if extension was added
                self.save_path += '.sim'
            self.loadingpath = self.save_path
            Publisher.sendMessage('SetSavePath',path=self.save_path) #send message to canvascontroller.SaveSimulation
            txt = save.Filename.split('.sim')[0]
            e = dict(cat=self.Toolbox.cat, txt=txt, fullpath=save.Path)
            events.onSimulationSaved.fire(**e)  # calls loadSIMFile from logicToolBox
        else:
            save.Destroy()

    def onDirectory(self, event):
        ToolboxPane = self.m_mgr.GetPane(self.Toolbox)
        ToolboxPane.Hide()
        DirectoryPane = self.m_mgr.GetPane(self.Directory)
        DirectoryPane.Show(show=True)
        self.m_mgr.Update()
        pass

    def onAllFiles(self, event):
        DirectoryPane = self.m_mgr.GetPane(self.Directory)
        DirectoryPane.Hide()
        ToolboxPane = self.m_mgr.GetPane(self.Toolbox)
        ToolboxPane.Show(show=True)
        self.m_mgr.Update()
        pass

    def onConsole(self, event):
        ConsolePane = self.m_mgr.GetPane(self.bnb)
        Toggle = 1
        if event.Selection == 0:
            ConsolePane.Show(show=True)
            Toggle = 1
        if event.Selection == 1:
            ConsolePane.Hide()
            Toggle = 0
        self.m_mgr.Update()
        pass

    # todo: temporarily disabled until we fix the AUI manager bugs
    # def defaultview(self, event):
    #     self.onAllFiles(event)
    #     ConsolePane = self.m_mgr.GetPane(self.bnb)
    #     ConsolePane.Show(show=True)
    #     # self.m_mgr.ClosePane(self.bnb)
    #     # self.m_mgr.AddPane(self.bnb,
    #     #                    aui.AuiPaneInfo().
    #     #                    Center().
    #     #                    Name("Console").
    #     #                    Position(1).
    #     #                    CloseButton(False).
    #     #                    MaximizeButton(True)
    #     #                    .Movable()
    #     #                    .MinimizeButton(True).
    #     #                    PinButton(True).
    #     #                    Resizable().
    #     #                    Floatable().
    #     #                    MinSize(wx.Size(1200, 200)))
    #     self.m_mgr.Update()
    #
    #     pass

class ModelView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.contents = wx.html2.WebView.New(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.contents, 1, wx.ALL|wx.EXPAND, 5)
        parent.SetSizer(sizer)
        self.SetSizerAndFit(sizer)

    def setText(self, value=None):
        self.contents.SetPage(value, "")

class AllFileView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

class viewMenuBar(wx.Frame):

    def __init__(self):
        #  Read the settings file
        currentdir = os.path.dirname(os.path.abspath(__file__))
        self.settingspath = os.path.abspath(os.path.join(currentdir, '../../data/settings'))
        file = open(self.settingspath, 'r')
        fileinfo = file.readlines()

        value = fileinfo[1].split(' = ')
        value = value[1].split('\n')
        w = value[0]
        w = int(w)
        value = fileinfo[2].split(' = ')
        value = value[1].split('\n')
        h = value[0]
        h = int(h)

        boolist = []

        for i in range(3, len(fileinfo)):
            value = fileinfo[i].split(' = ')
            value = value[1].split('\n')
            if value[0] == 'True':
                boolist.append(True)
            else:
                boolist.append(False)

        self.infoIsChecked = boolist[0]
        self.warningIsChecked = boolist[1]
        self.criticalIsChecked = boolist[2]
        self.errorIsChecked = boolist[3]

        file.close()

        wx.Frame.__init__(self, parent=None, id=-1, title="Settings...", pos=wx.DefaultPosition, size=wx.Size(w, h))
        self.panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.statusbar = self.CreateStatusBar()
        # self.statusbar = wx.StatusBar(parent=self, id=wx.ID_ANY, style=wx.STB_DEFAULT_STYLE)
        self.SettingsStatusBar()

        self.c1 = wx.CheckBox(self.panel, id=wx.ID_ANY, label="Show Info Messages")
        self.c2 = wx.CheckBox(self.panel, id=wx.ID_ANY, label="Show Warning Messages")
        self.c3 = wx.CheckBox(self.panel, id=wx.ID_ANY, label="Show Critical Messages")
        self.c4 = wx.CheckBox(self.panel, id=wx.ID_ANY, label="Show Error Messages")

        self.c1.SetValue(self.infoIsChecked)
        self.c2.SetValue(self.warningIsChecked)
        self.c3.SetValue(self.criticalIsChecked)
        self.c4.SetValue(self.errorIsChecked)

        self.saveButton = wx.Button(self.panel, 1, 'Save')

        sizer.Add(self.c1, 1, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        sizer.Add(self.c2, 1, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        sizer.Add(self.c3, 1, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        sizer.Add(self.c4, 1, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        sizer.Add(self.saveButton, 1, flag=wx.wx.ALL | wx.ALIGN_CENTER, border=5)
        # sizer.Add(self.gauge, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=0)

        self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)




        self.panel.SetSizer(sizer)
        self.Centre()
        self.Show()

    def OnSave(self, event):
        self.timer.Start(25)
        # self.OnTimer()
        cb = self.getCheckboxValue()
        file = open(self.settingspath, 'w')
        file.writelines(['0\n',
                         'w = 350\n',
                         'h = 350\n',
                         'showinfo = '+str(cb.values()[0])+'\n',
                         'showwarning = '+str(cb.values()[1])+'\n',
                         'showcritical = '+str(cb.values()[2]+'\n'),
                         'showerror = '+str(cb.values()[3]+'\n')])
        file.close()
        # self.timer.Stop()
        # self.statusbar.SetStatusText('Settings saved, %s ' % wx.Now())

    def getCheckboxValue(self):
        info = self.c1.GetValue()
        warn = self.c2.GetValue()
        critical = self.c3.GetValue()
        error = self.c4.GetValue()
        cb = {'info': str(info), 'warn': str(warn), 'critical': str(critical), 'error': str(error)}
        return cb

    def SettingsStatusBar(self):
        self.count = 0
        self.timer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.gauge = wx.Gauge(self.statusbar, range=50, size=(100, 10))

    def OnTimer(self, e):
        self.count += 1
        self.gauge.Show()
        self.gauge.SetValue(self.count)

        if self.count >= 50:
            self.timer.Stop()
            self.statusbar.SetStatusText('Settings saved, %s ' % wx.Now())
            self.count = 0
            self.gauge.Hide()
        else:
            #  This will show the number the gauge is at.
            # self.statusbar.SetStatusText(str(self.gauge.GetValue()))
            # self.OnTimer()
            pass


# class viewMenuBar(wx.Frame):
#     def __init__(self):
#         self.cfg = wx.Config('myconfig')
#         currentdir = os.path.dirname(os.path.abspath(__file__))
#         self.settingspath = os.path.abspath(os.path.join(currentdir, '../../data/settings'))
#         self.cfg.SetPath(self.settingspath)
#         if self.cfg.Exists('width'):
#             w, h = self.cfg.ReadInt('width'), self.cfg.ReadInt('height')
#         else:
#             w, h = 250, 250
#
#         self.infoIsChecked = self.cfg.ReadBool("info")
#         self.warningIsChecked = self.cfg.ReadBool("warning")
#
#         wx.Frame.__init__(self, parent=None, id=-1, title="Settings...", pos=wx.DefaultPosition, size=wx.Size(w, h))
#         self.panel = wx.Panel(self)
#
#         wx.StaticText(self.panel, -1, 'Width:', (20, 20))
#         wx.StaticText(self.panel, -1, 'Height:', (20, 70))
#         self.sc1 = wx.SpinCtrl(self.panel, -1, str(w), (80, 15), (60, -1), min=200, max=500)
#         self.sc2 = wx.SpinCtrl(self.panel, -1, str(h), (80, 65), (60, -1), min=200, max=500)
#         wx.Button(self.panel, 1, 'Save', pos=(20, 120))
#
#         self.c1 = wx.CheckBox(self.panel, id=wx.ID_ANY, label="Show Info Messages", pos=(50, 200))
#         self.c2 = wx.CheckBox(self.panel, id=wx.ID_ANY, label="Show Warning Messages", pos=(50, 225))
#
#         self.c1.SetValue(self.infoIsChecked)
#         self.c2.SetValue(self.warningIsChecked)
#         print self.cfg.GetPath()
#
#         self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)
#         self.statusbar = self.CreateStatusBar()
#         self.Centre()
#
#     def OnSave(self, event):
#         self.cfg.WriteInt("width", self.sc1.GetValue())
#         self.cfg.WriteInt("height", self.sc2.GetValue())
#         self.cfg.WriteBool("info", self.c1.GetValue())
#         self.cfg.WriteBool("warning", self.c2.GetValue())
#         self.statusbar.SetStatusText('Configuration saved, %s ' % wx.Now())
#         self.RefreshSettings()
#
#     def teststatusbar(self, event):
#         for i in range(1, 1000):
#             self.statusbar.SetStatusText("Progress %d" % i)
#
#     def RefreshSettings(self):
#         elog.showinfo = self.c1.GetValue()
#         elog.showwarning = self.c2.GetValue()
#         print self.c1.GetValue()
#         print self.c2.GetValue()
