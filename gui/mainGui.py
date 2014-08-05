__author__ = 'Mario'
import wx
import wx.grid as grid
#import wx.html
import wx.html2
from DirectoryView import DirectoryCtrlView
import sys
from CanvasView import Canvas
from wx.lib.pubsub import pub as Publisher
import utilities
import wx.lib.agw.ultimatelistctrl as ULC
from ObjectListView.ObjectListView import FastObjectListView
import wx.lib.agw.aui as aui
import objectListViewDatabase as olv

from ODM2.Core.services import *


class MainGui(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                          size=wx.Size(1200, 750), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.pnlDocking = wx.Panel(id=wx.ID_ANY, name='pnlDocking', parent=self, size=wx.Size(1200, 750),
                                   style=wx.TAB_TRAVERSAL)


        #self.Bind(wx.EVT_CLOSE, self.onClose)
        self.initMenu()
        self.initAUIManager()
        self._init_sizers()

    def _init_sizers(self):
        # generated method, don't edit
        self.s = wx.BoxSizer(wx.VERTICAL)
        self._init_s_Items(self.s)
        self.SetSizer(self.s)

    def _init_s_Items(self, parent):
        # generated method, don't edit
        #parent.AddWindow(self._ribbon, 0, wx.EXPAND)
        parent.AddWindow(self.pnlDocking, 85, flag=wx.ALL | wx.EXPAND)

    def initAUIManager(self):

        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow(self.pnlDocking)
        # self.m_mgr.SetFlags(aui.AUI_MGR_DEFAULT)

        # self.output = wx.TextCtrl(self, -1, size=(100,100), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        self.Canvas = Canvas(self.pnlDocking)
        #self.Canvas.output.WriteText(
        self.nb = wx.Notebook(self.pnlDocking)




        page1 = DirectoryCtrlView(self.nb)
        page2 = ModelView(self.nb)
        page3 = LinkView(self.nb)
        # page4 = TimeSeries(self.nb)

        self.nb.AddPage(page1, "Directory")
        self.nb.AddPage(page2, "Model View")
        self.nb.AddPage(page3, "Link View")
        # self.nb.AddPage(page4, "Series Selector")

        self.nb.GetPage(0).SetLabel("Directory")
        self.nb.GetPage(1).SetLabel("Model View")
        self.nb.GetPage(2).SetLabel("Link View")
        # self.nb.GetPage(3).SetLabel("Series Selector")

        self.bnb = wx.Notebook(self.pnlDocking)

        output = consoleOutput(self.bnb)
        seriesselector = TimeSeries(self.bnb)

        self.bnb.AddPage(output, "Output")
        self.bnb.AddPage(seriesselector, "Series Selector")

        self.bnb.GetPage(0).SetLabel("Output")
        self.bnb.GetPage(1).SetLabel("Series Selector")



        self.m_mgr.AddPane(self.Canvas,
               aui.AuiPaneInfo().
               Center().
               Name("Canvas").
               Position(0).
               CloseButton(False).
               MaximizeButton(True).
               MinimizeButton(True).
               PinButton(True).
               Resizable().
               Movable().
               Floatable(True).
               MinSize(wx.Size(1000, 400)))

        self.m_mgr.AddPane(self.bnb,
              aui.AuiPaneInfo().
              Caption('Output').
              Center().
              Name("Console").
              Position(1).
              CloseButton(False).
              MaximizeButton(True)
              .Movable()
              .MinimizeButton(True).
              PinButton(True).
              Resizable().
              Floatable().
              MinSize(wx.Size(1000, 200)))


        self.m_mgr.AddPane(self.nb,
               aui.AuiPaneInfo().
               Left().
               Dock().
               CloseButton(False).
               MaximizeButton(True).
               MinimizeButton(True).
               MinimizeMode(mode=aui.framemanager.AUI_MINIMIZE_POS_SMART).
               PinButton(True).
               Resizable().
               MinSize(wx.Size(375,500)).
               Floatable().
               Movable().
               FloatingSize(size=(600, 800)).
               CloseButton(True))


        # self.m_mgr.AddPane(self.nb,
        #                    wx.aui.AuiPaneInfo().
        #                    Left().
        #                    CloseButton(False).
        #                    MaximizeButton(True).
        #                    MinimizeButton().
        #                    PinButton(True).
        #                    Resizable().
        #                    MinSize(wx.Size(375,500)).
        #                    Floatable())


        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnSelect)

        self.m_mgr.Update()

    def OnSelect(self,event):


        selected_page = self.bnb.GetPage(event.GetSelection())

        if selected_page.Label == 'Series Selector':
            selected_page.getKnownDatabases()



    def initMenu(self):
        ## Menu stuff
        #self.m_statusBar2 = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)

        self.m_menubar = wx.MenuBar()

        self.m_fileMenu = wx.Menu()
        #exit = wx.MenuItem(self.m_fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        exit = self.m_fileMenu.Append(wx.NewId(), '&Quit\tCtrl+Q', 'Quit application')

        self.m_menubar.Append(self.m_fileMenu, "&File")

        self.m_toolMenu = wx.Menu()
        self.m_menubar.Append(self.m_toolMenu, "&Tools")

        self.m_viewMenu = wx.Menu()
        self.m_menubar.Append(self.m_viewMenu, "&View")

        self.SetMenuBar(self.m_menubar)

        wx.CallAfter(self._postStart)

        ## Events
        self.Bind(wx.EVT_MENU, self.onClose, exit)

    def _postStart(self):
        ## Starts stuff after program has initiated
        self.Canvas.ZoomToFit(Event=None)

    def __del__(self):
        self.m_mgr.UnInit()

    def onClose(self, event):
        windowsRemaining = len(wx.GetTopLevelWindows())
        if windowsRemaining > 0:
            import wx.lib.agw.aui.framemanager as aui
            # logger.debug("Windows left to close: %d" % windowsRemaining)
            for item in wx.GetTopLevelWindows():
                #logger.debug("Windows %s" % item)
                if not isinstance(item, self.__class__):
                    if isinstance(item, aui.AuiFloatingFrame):
                        item.Destroy()
                    elif isinstance(item, aui.AuiSingleDockingGuide):
                        item.Destroy()
                    elif isinstance(item, aui.AuiDockingHintWindow):
                        item.Destroy()
                    elif isinstance(item, wx.Dialog):
                        item.Destroy()
                    item.Close()
        self.Destroy()


class ModelView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #Canvas.ObjectHit()
        t = wx.StaticText(self, -1, "This view shows relevant model information.", (60,60))



        self.contents = wx.html2.WebView.New(self)



        #self.contents = wx.html.HtmlWindow (self, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
        #self.contents.SetPage("New Text")



        sizer = wx.BoxSizer()
        sizer.Add(self.contents, 1, wx.ALL|wx.EXPAND, 5)
        parent.SetSizer(sizer)
        self.SetSizerAndFit(sizer)

    def setText(self, value=None):
        self.contents.SetPage(value,"")

class LinkView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This view shows relations between models.", (60,60))

class TimeSeries(wx.Panel):
    """

    """

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,500 ), style = wx.TAB_TRAVERSAL )

        self._databases = {}
        self._connection_added = True

        m_choice3Choices = []
        self.m_choice3 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice3Choices, 0 )
        self.m_choice3.SetSelection( 0 )
        self.addConnectionButton = wx.Button( self, wx.ID_ANY, u"Add Connection", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_olvSeries = olv.OlvSeries(self, pos = wx.DefaultPosition, size = wx.DefaultSize, id = wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER  )

        # Bindings
        self.addConnectionButton.Bind(wx.EVT_LEFT_DOWN, self.AddConnection)

        # Sizers
        seriesSelectorSizer = wx.BoxSizer( wx.VERTICAL )
        buttonSizer = wx.BoxSizer( wx.HORIZONTAL )
        buttonSizer.SetMinSize( wx.Size( -1,45 ) )

        buttonSizer.Add( self.m_choice3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        buttonSizer.Add( self.addConnectionButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        seriesSelectorSizer.Add( buttonSizer, 0, wx.ALL|wx.EXPAND, 5 )
        seriesSelectorSizer.Add( self.m_olvSeries, 1, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( seriesSelectorSizer )
        self.Layout()

        databases = Publisher.sendMessage('GetDatabases')
        Publisher.subscribe(self.getKnownDatabases, "getKnownDatabases")
        Publisher.subscribe(self.connection_added_status, "connectionAddedStatus")


        # self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [], 0 )
        # self.m_choice2.SetSelection( 0 )
        # bSizer2.Add( self.m_choice2, 0, wx.ALL, 5 )


        self.m_choice3.Bind(wx.EVT_CHOICE,self.DbChanged)




        # self.m_button1 = wx.Button( self, wx.ID_ANY, u"Add Connection", wx.DefaultPosition, wx.DefaultSize, 0 )
        # bSizer2.Add( self.m_button1, 0, wx.ALL, 5 )

        # self.list = ULC.UltimateListCtrl(self, wx.ID_ANY, agwStyle=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL)
        #
        # self.list.InsertColumn(0, "Column 1")
        # self.list.InsertColumn(1, "Column 2")
        #
        # index = self.list.InsertStringItem(sys.maxint, "Item 1")
        # self.list.SetStringItem(index, 1, "Sub-item 1")
        #
        # index = self.list.InsertStringItem(sys.maxint, "Item 2")
        # self.list.SetStringItem(index, 1, "Sub-item 2")
        #
        # choice = wx.Choice(self.list, -1, choices=["one", "two"])
        # index = self.list.InsertStringItem(sys.maxint, "A widget")
        #
        # self.list.SetItemWindow(index, 1, choice, expand=True)
        #
        # bSizer3.Add(self.list, 1, wx.EXPAND)

        # Publisher.subscribe(self.refresh, "refreshDialogDatabases")
        # bSizer3.Add(objectListViewDatabase.MainPanel(self))


        # self.SetSizer( bSizer1 )
        # self.Layout()


    def DbChanged(self, event):


        # get the name of the selected database
        selected_db = self.m_choice3.GetStringSelection()

        for key, db in self._databases.iteritems():

            # get the database session associated with the selected name
            if db['name'] == selected_db:


                # query the database and get basic series info

                core_connection = readCore(db['session'])

                from db import api as dbapi
                from gui.objectListViewDatabase import Database

                u = dbapi.utils(db['session'])
                series = u.getAllSeries()
                #all_results = core_connection.getAllResult()

                # loop through all of the returned data
                data = []
                for s in series:
                    # resultid
                    r = s.ResultID

                    # sitename
                    sn = '?'
                    # sitecode
                    sc = '?'
                    # variablename
                    v = s.VariableObj.VariableCode
                    # variableunit
                    u = s.UnitObj.UnitsName
                    # time unit
                    t = '?'
                    # begin
                    b = '?'
                    # end
                    e = '?'

                    data.extend([Database(r,sn,sc,v,u,t,b,e)])

                # set the data objects in the olv control
                self.m_olvSeries.SetObjects(data)


                # exit
                break

        return

    def getKnownDatabases(self, value = None):
        if value is None:
            Publisher.sendMessage('getDatabases')
        else:
            self._databases = value
            choices = ['---']
            for k,v in self._databases.iteritems():
                choices.append(self._databases[k]['name'])
            self.m_choice3.SetItems(choices)

    def connection_added_status(self,value=None,connection_string=''):
        if value is not None:
            self._connection_added = value
            self._conection_string = connection_string
        return self._connection_added



    def AddConnection(self, event):

        params = []

        while 1:
            dlg = AddConnectionDialog(self, -1, "Sample Dialog", size=(350, 200),
                             style=wx.DEFAULT_DIALOG_STYLE,
                             )
            dlg.CenterOnScreen()

            if params:
                dlg.set_values(title=params[0],
                                  desc = params[1],
                                  engine = params[2],
                                  address = params[3],
                                  name = params[4],
                                  user = params[5],
                                  pwd = params[6])

            # this does not return until the dialog is closed.
            val = dlg.ShowModal()


            if val == 5101:
                # cancel is selected
                return
            elif val == 5100:
                params = dlg.getConnectionParams()

                dlg.Destroy()



                # create the database connection
                Publisher.sendMessage('DatabaseConnection',
                                      title=params[0],
                                      desc = params[1],
                                      engine = params[2],
                                      address = params[3],
                                      name = params[4],
                                      user = params[5],
                                      pwd = params[6])

                if self.connection_added_status():
                    Publisher.sendMessage('getDatabases')
                    return
                else:

                    wx.MessageBox('I was unable to connect to the database with the information provided :(', 'Info', wx.OK | wx.ICON_ERROR)


    def __del__( self ):
        pass


class consoleOutput(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(self, -1, size=(100,100),
                          style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        redir= RedirectText(log)
        sys.stdout=redir

        # # Add widgets to a sizer
        sizer = wx.BoxSizer()
        sizer.Add(log, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        # redirect text here
        # redir= RedirectText(log)
        # sys.stdout=redir

        self.SetSizerAndFit(sizer)

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)

class AddConnectionDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents

        gridsizer = wx.FlexGridSizer(rows=7,cols=2,hgap=5,vgap=5)

        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Database Connection")
        titleSizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        ######################################################

        label = wx.StaticText(self, -1, "*Title :")
        label.SetFont(label.GetFont().MakeBold())
        label.SetHelpText("Title of the database connection")
        self.title = wx.TextCtrl(self, wx.ID_ANY, '', size=(200,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.title, 0, wx.EXPAND)


        label = wx.StaticText(self, -1, "Description :")
        label.SetHelpText("Description of the database connection")
        self.description = wx.TextCtrl(self, -1, "", size=(80,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.description, 0, wx.EXPAND)

        ######################################################


        label = wx.StaticText(self, -1, "*Engine :")
        label.SetFont(label.GetFont().MakeBold())
        label.SetHelpText("Database Parsing Engine (e.g. mysql, psycopg2, etc)")
        #self.engine = wx.TextCtrl(self, -1, "", size=(80,-1))
        engine_choices = ['PostgreSQL', 'MySQL']
        self.engine = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, engine_choices, 0 )
        self.engine.SetSelection( 0 )
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.engine, 0, wx.EXPAND)


        label = wx.StaticText(self, -1, "*Address :")
        label.SetFont(label.GetFont().MakeBold())
        label.SetHelpText("Database Address")
        self.address = wx.TextCtrl(self, -1, "", size=(80,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.address, 0, wx.EXPAND)

        label = wx.StaticText(self, -1, "*Database :")
        label.SetFont(label.GetFont().MakeBold())
        label.SetHelpText("Database Name")
        self.name = wx.TextCtrl(self, -1, "", size=(80,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.name, 0, wx.EXPAND)

        label = wx.StaticText(self, -1, "*User :")
        label.SetFont(label.GetFont().MakeBold())
        label.SetHelpText("Database Username")
        self.user = wx.TextCtrl(self, -1, "", size=(80,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.user, 0, wx.EXPAND)

        label = wx.StaticText(self, -1, "Password :")
        label.SetHelpText("Database Password")
        self.password = wx.TextCtrl(self, -1, "", size=(80,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridsizer.Add(box,0,wx.ALIGN_LEFT)
        gridsizer.Add(self.password, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(titleSizer, 0, wx.CENTER)
        sizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(gridsizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizeHints(250,300,500,400)


        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        self.btnok = wx.Button(self, wx.ID_OK)
        self.btnok.SetDefault()
        btnsizer.AddButton(self.btnok)
        self.btnok.Disable()

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)


        #self.engine.Bind(wx.EVT_TEXT, self.OnTextEnter)
        self.address.Bind(wx.EVT_TEXT, self.OnTextEnter)
        self.name.Bind(wx.EVT_TEXT, self.OnTextEnter)
        self.user.Bind(wx.EVT_TEXT, self.OnTextEnter)
        self.title.Bind(wx.EVT_TEXT, self.OnTextEnter)


    def set_values(self,title,desc,engine, address, name, user,pwd):
        self.title.Value = title
        self.description.Value = desc
        self.engine.Value = engine
        self.address.Value = address
        self.name.Value = name
        self.user.Value = user
        self.password.Value = pwd

    def getConnectionParams(self):

        engine = self.engine.GetStringSelection().lower()

        #engine = self.engine.GetValue()
        address = self.address.GetValue()
        name = self.name.GetValue()
        user = self.user.GetValue()
        pwd = self.password.GetValue()
        title = self.title.GetValue()
        desc = self.description.GetValue()

        return title,desc, engine,address,name,user,pwd,title,desc

    def OnTextEnter(self, event):
        if self.address.GetValue() == '' or  \
                self.name.GetValue() == '' or  \
                self.user.GetValue() == '' or \
                self.title.GetValue() =='' :
            self.btnok.Disable()
        else:
            self.btnok.Enable()
