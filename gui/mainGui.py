__author__ = 'Mario'
import wx
import wx.html2
from DirectoryView import DirectoryCtrlView
from Toolbox import ToolboxPanel
import sys
from CanvasView import Canvas
from wx.lib.pubsub import pub as Publisher
from CanvasController import CanvasController
import wx.lib.agw.aui as aui
import objectListViewDatabase as olv
from api.ODM2.Core.services import *
import logging
from ContextMenu import GeneralContextMenu
import threading
from db import dbapi as dbapi
from objectListViewDatabase import ContextMenu
from frmMatPlotLib import MatplotFrame
from api.ODM2.Simulation.services import readSimulation
from api.ODM2.Results.services import readResults




#Save Features
import xml.etree.ElementTree as et
from xml.dom import minidom
import datatypes


class MainGui(wx.Frame):
    def __init__(self, parent, cmd):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Environmental Model Integration Project", pos=wx.DefaultPosition,
                          size=wx.Size(1200, 750), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.pnlDocking = wx.Panel(id=wx.ID_ANY, name='pnlDocking', parent=self, size=wx.Size(1200, 750),
                                   style=wx.TAB_TRAVERSAL)

        # save cmd object in pnlDocking so that children can access it
        self.pnlDocking.__setattr__('cmd',cmd)

        self.Bind(wx.EVT_CLOSE, self.onClose)
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

        #self.m_mgr.SetFlags(aui.AUI_MGR_DEFAULT)
        # self.output = wx.TextCtrl(self, -1, size=(100,100), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.Canvas = Canvas(self.pnlDocking)
        self.Directory = DirectoryCtrlView(self.pnlDocking)
        self.Toolbox = ToolboxPanel(self.pnlDocking)
        self.Toolbox.Hide()


        self.bnb = wx.Notebook(self.pnlDocking)
        output = consoleOutput(self.bnb)

        # seriesoutput = OutputTimeSeries(self.bnb)
        seriesselector = TimeSeries(self.bnb)
        seriesoutput = SimulationDataTable(self.bnb)

        self.bnb.AddPage(output, "Console")
        self.bnb.AddPage(seriesselector, "Time Series")
        self.bnb.AddPage(seriesoutput, "Simulations")
        # self.bnb.AddPage(seriesoutput, "Output Time Series")

        self.bnb.GetPage(0).SetLabel("Console")
        self.bnb.GetPage(1).SetLabel("Time Series")
        # self.bnb.GetPage(2).SetLabel("Output Time Series")

        self.bnb.GetPage(2).SetLabel("Simulations")


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
                           MinSize(wx.Size(1200, 200)))


        self.m_mgr.AddPane(self.Directory,
                           aui.AuiPaneInfo().
                           Left().
                           Dock().
                           CloseButton(False).
                           MaximizeButton(True).
                           MinimizeButton(True).
                           MinimizeMode(mode=aui.framemanager.AUI_MINIMIZE_POS_SMART).
                           PinButton(True).
                           Resizable().
                           MinSize(wx.Size(275,400)).
                           Floatable().
                           Movable().
                           FloatingSize(size=(600, 800)).
                           Show(show=False).Hide().
                           CloseButton(True))

        self.m_mgr.AddPane(self.Toolbox,
                           aui.AuiPaneInfo().
                           Left().
                           Dock().
                           CloseButton(False).
                           MaximizeButton(True).
                           MinimizeButton(True).
                           MinimizeMode(mode=aui.framemanager.AUI_MINIMIZE_POS_SMART).
                           PinButton(True).
                           Resizable().
                           MinSize(wx.Size(275,400)).
                           Floatable().
                           Movable().
                           FloatingSize(size=(600, 800)).
                           Show(show=True).
                           CloseButton(True))

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnSelect)

        self.m_mgr.Update()

    def OnSelect(self,event):

        try:
            selected_page = self.bnb.GetPage(event.GetSelection())


            # update databases in a generic way
            if len(selected_page.connection_combobox.GetItems()) == 0:
            # if 'getKnownDatabases' in dir(selected_page):
                 selected_page.getKnownDatabases()

        except: pass

    def initMenu(self):
        ## Menu stuff
        #self.m_statusBar2 = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)

        self.m_menubar = wx.MenuBar()

        self.m_fileMenu = wx.Menu()
        #exit = wx.MenuItem(self.m_fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        Save = self.m_fileMenu.Append(wx.NewId(), '&Save Configuration\tCtrl+S', 'Save Configuration')
        Open = self.m_fileMenu.Append(wx.NewId(), '&Load Configuration\tCtrl+O', 'Load Configuration')
        exit = self.m_fileMenu.Append(wx.NewId(), '&Quit\tCtrl+Q', 'Quit application')

        self.m_menubar.Append(self.m_fileMenu, "&File")

        self.m_toolMenu = wx.Menu()
        self.m_menubar.Append(self.m_toolMenu, "&Tools")


        self.m_viewMenu = wx.Menu()
        ShowAll = self.m_viewMenu.Append(wx.NewId(), '&Toolbox\tCtrl+A', 'Show all associated files', wx.ITEM_RADIO)
        ShowDir = self.m_viewMenu.Append(wx.NewId(), '&Directory\tCtrl+D', 'Shows file directory', wx.ITEM_RADIO)
        self.m_menubar.Append(self.m_viewMenu, "&View")

        self.SetMenuBar(self.m_menubar)

        wx.CallAfter(self._postStart)

        ## Events
        self.Bind(wx.EVT_MENU, self.SaveConfiguration, Save)
        self.Bind(wx.EVT_MENU, self.LoadConfiguration, Open)
        self.Bind(wx.EVT_MENU, self.onClose, exit)
        self.Bind(wx.EVT_MENU, self.onDirectory, ShowDir)
        self.Bind(wx.EVT_MENU, self.onAllFiles, ShowAll)

    def _postStart(self):
        ## Starts stuff after program has initiated
        self.Canvas.ZoomToFit(Event=None)

    def __del__(self):
        self.m_mgr.UnInit()

    def onClose(self, event):
        dlg = wx.MessageDialog(None, 'Are you sure you want to exit?', 'Question',
                               wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING)

        if dlg.ShowModal() !=wx.ID_NO:
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
            wx.GetApp().ExitMainLoop()

    def LoadConfiguration(self,event):


        if wx.MessageBox("This will overlay on the current configuration.", "Please confirm",
                         wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
            return

        # else: proceed asking to the user the new file to open

        openFileDialog = wx.FileDialog(self, "Open SIM file", "", "",
                                       "Simulation Files (*.sim)|*.sim", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # proceed loading the file chosen by the user
        # this can be done with e.g. wxPython input streams:
        input_stream = (openFileDialog.GetPath())
        Publisher.sendMessage('SetLoadPath',file=input_stream) #send message to canvascontroller
        #
        # data = wx.FileDataObject()
        # data.AddFile(input_stream)
        #
        # obj = event.GetSelection()
        # data = wx.FileDataObject()
        #
        # dropSource = wx.DropSource(openFileDialog)
        # dropSource.SetData(data)
        # x = 0
        # y = 0
        # dropSource.DoDragDrop()

        # if not input_stream.IsOk():
        #
        #     wx.LogError("Cannot open file '%s'."%openFileDialog.GetPath())
        #     return
        # pass

    def SaveConfiguration(self,event):
        save = wx.FileDialog(self.Canvas.GetTopLevelParent(), "Save Configuration","","",
                             "Simulation Files (*.sim)|*.sim", wx.FD_SAVE  | wx.FD_OVERWRITE_PROMPT)

        if save.ShowModal() == wx.ID_OK:
            self.save_path = save.GetPath() + ".sim"
        else:
            save.Destroy()


        Publisher.sendMessage('SetSavePath',path=save.GetPath()) #send message to canvascontroller.SaveSimulation

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

class AllFileView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

class TimeSeries(wx.Panel):
    """

    """

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,500 ), style = wx.TAB_TRAVERSAL )

        self._databases = {}
        self._connection_added = True

        self.__logger = logging.getLogger('root')


        connection_choices = []
        self.connection_combobox = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size(200, 23), connection_choices, 0)
        self.__selected_choice_idx = 0
        self.connection_combobox.SetSelection( self.__selected_choice_idx)

        self.connection_refresh_button = wx.Button(self, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0)
        self.addConnectionButton = wx.Button( self, wx.ID_ANY, u"Add Connection", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_olvSeries = olv.OlvSeries(self, pos = wx.DefaultPosition, size = wx.DefaultSize, id = wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER  )
        self.table_columns = ["ResultID", "FeatureCode", "Variable", "Unit", "Type", "Organization", "Date Created"]
        self.m_olvSeries.DefineColumns(self.table_columns)

        # Bindings
        self.addConnectionButton.Bind(wx.EVT_LEFT_DOWN, self.AddConnection)
        self.addConnectionButton.Bind(wx.EVT_MOUSEWHEEL, self.AddConnection_MouseWheel)

        self.connection_refresh_button.Bind(wx.EVT_LEFT_DOWN, self.OLVRefresh)
        self.connection_combobox.Bind(wx.EVT_CHOICE,self.DbChanged)


        # Sizers
        seriesSelectorSizer = wx.BoxSizer( wx.VERTICAL )
        buttonSizer = wx.BoxSizer( wx.HORIZONTAL )
        buttonSizer.SetMinSize( wx.Size( -1,45 ) )

        buttonSizer.Add( self.connection_combobox, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        buttonSizer.Add( self.addConnectionButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        buttonSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        buttonSizer.Add( self.connection_refresh_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        seriesSelectorSizer.Add( buttonSizer, 0, wx.ALL|wx.EXPAND, 5 )
        seriesSelectorSizer.Add( self.m_olvSeries, 1, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( seriesSelectorSizer )
        self.Layout()

        #databases = Publisher.sendMessage('getDatabases')
        Publisher.subscribe(self.getKnownDatabases, "getKnownDatabases")  # sends message to CanvasController
        Publisher.subscribe(self.connection_added_status, "connectionAddedStatus")


        # build custom context menu
        menu = TimeSeriesContextMenu(self.m_olvSeries)
        self.m_olvSeries.setContextMenu(menu)

    def DbChanged(self, event):
        self.OLVRefresh(event)

    def getKnownDatabases(self, value = None):
        if value is None:
            Publisher.sendMessage('getDatabases')
        else:
            self._databases = value
            choices = ['---']
            for k,v in self._databases.iteritems():
                choices.append(self._databases[k]['name'])
            self.connection_combobox.SetItems(choices)

            # set the selected choice
            self.connection_combobox.SetSelection( self.__selected_choice_idx)

    def connection_added_status(self,value=None,connection_string=''):
        if value is not None:
            self._connection_added = value
            self._conection_string = connection_string
        return self._connection_added

    def AddConnection_MouseWheel(self, event):
        '''
        This is intentionally empty to disable mouse scrolling in the AddConnection combobox
        :param event: EVT_MOUSEWHEEL
        :return: None
        '''
        pass

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

    def refresh_database(self):

        # get the name of the selected database
        selected_db = self.connection_combobox.GetStringSelection()

        #set the selected choice
        self.__selected_choice_idx = self.connection_combobox.GetSelection()

        for key, db in self._databases.iteritems():

            # get the database session associated with the selected name
            if db['name'] == selected_db:

                # query the database and get basic series info

                from db import dbapi as dbapi
                from gui.objectListViewDatabase import Database

                u = dbapi.utils(db['session'])
                series = u.getAllSeries()

                if series is None:
                    d = {key: value for (key, value) in
                         zip([col.lower().replace(' ','_') for col in self.table_columns],["" for c in self.table_columns])}
                    record_object = type('DataRecord', (object,), d)
                    data = [record_object]
                else:

                    # loop through all of the returned data
                    data = []
                    for s in series:
                        d = {
                            'resultid' : s.ResultID,
                            'variable' : s.VariableObj.VariableCode,
                            'unit' : s.UnitObj.UnitsName,
                            'date_created' : s.FeatureActionObj.ActionObj.BeginDateTime,
                            'type' : s.FeatureActionObj.ActionObj.ActionTypeCV,
                            'featurecode' : s.FeatureActionObj.SamplingFeatureObj.SamplingFeatureCode,
                            'organization' : s.FeatureActionObj.ActionObj.MethodObj.OrganizationObj.OrganizationName
                        }

                        record_object = type('DataRecord', (object,), d)
                        data.extend([record_object])

                        # resultid = s.ResultID
                        # variable = s.VariableObj.VariableCode
                        # unit = s.UnitObj.UnitsName
                        # date_created = s.FeatureActionObj.ActionObj.BeginDateTime
                        # type = s.FeatureActionObj.ActionObj.ActionTypeCV
                        # featurecode = s.FeatureActionObj.SamplingFeatureObj.SamplingFeatureCode
                        # organization = s.FeatureActionObj.ActionObj.MethodObj.OrganizationObj.OrganizationName
                        #
                        #data.extend([Database(resultid,featurecode,variable,unit,data_type,org,date_created)])
                        #table_columns = ["ResultID", "FeatureCode", "Variable", "Unit", "Type", "Organization", "Date Created"]

                        # record =olv.DataRecord([('resultid',resultid),
                        #                      ('variable',variable),
                        #                      ('unit',unit),
                        #                      ('date_created',date_created),
                        #                      ('type',type),
                        #                      ('featurecode',featurecode),
                        #                      ('organization',organization)])
                        #
                        # data.extend([record])

                # set the data objects in the olv control
                self.m_olvSeries.SetObjects(data)

                # set the current database in canvas controller
                Publisher.sendMessage('SetCurrentDb',value=selected_db)  # sends to CanvasController.getCurrentDbSession

                #self.__logger.info ('Database "%s" refreshed'%self.connection_combobox.GetStringSelection())
                # exit
                break

        return

    def OLVRefresh(self, event):

        thr = threading.Thread(target=self.refresh_database, args=(), kwargs={})
        thr.start()

        # refresh the object list view
        #Publisher.sendMessage("olvrefresh")

class DataSeries(wx.Panel):
    """

    """

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,500 ), style = wx.TAB_TRAVERSAL )

        self._databases = {}
        self._connection_added = True

        connection_choices = []
        self.connection_combobox = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size(200, 23), connection_choices, 0)
        self.__selected_choice_idx = 0
        self.connection_combobox.SetSelection(0)

        self.connection_refresh_button = wx.Button(self, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0)
        self.addConnectionButton = wx.Button( self, wx.ID_ANY, u"Add Connection", wx.DefaultPosition, wx.DefaultSize, 0 )

        self.table = olv.OlvSeries(self, pos = wx.DefaultPosition, size = wx.DefaultSize, id = wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER  )

        # Bindings
        self.addConnectionButton.Bind(wx.EVT_LEFT_DOWN, self.AddConnection)
        self.addConnectionButton.Bind(wx.EVT_MOUSEWHEEL, self.AddConnection_MouseWheel)

        self.connection_refresh_button.Bind(wx.EVT_LEFT_DOWN, self.database_refresh)
        self.connection_combobox.Bind(wx.EVT_CHOICE,self.DbChanged)


        # Sizers
        seriesSelectorSizer = wx.BoxSizer( wx.VERTICAL )
        buttonSizer = wx.BoxSizer( wx.HORIZONTAL )
        buttonSizer.SetMinSize( wx.Size( -1,45 ) )

        buttonSizer.Add( self.connection_combobox, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        buttonSizer.Add( self.addConnectionButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        buttonSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        buttonSizer.Add( self.connection_refresh_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        seriesSelectorSizer.Add( buttonSizer, 0, wx.ALL|wx.EXPAND, 5 )
        seriesSelectorSizer.Add( self.table, 1, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( seriesSelectorSizer )
        self.Layout()

        #databases = Publisher.sendMessage('getDatabases')
        Publisher.subscribe(self.getKnownDatabases, "getKnownDatabases")  # sends message to CanvasController
        Publisher.subscribe(self.connection_added_status, "connectionAddedStatus")

        # initialize databases
        self.getKnownDatabases()

    def DbChanged(self, event):
        self.database_refresh(event)

    def getKnownDatabases(self, value = None):
        if value is None:
            Publisher.sendMessage('getDatabases')
        else:
            self._databases = value
            choices = ['---']
            for k,v in self._databases.iteritems():
                choices.append(self._databases[k]['name'])
            self.connection_combobox.SetItems(choices)

            # set the selected choice
            self.connection_combobox.SetSelection( self.__selected_choice_idx)

    def connection_added_status(self,value=None,connection_string=''):
        if value is not None:
            self._connection_added = value
            self._conection_string = connection_string
        return self._connection_added

    def AddConnection_MouseWheel(self, event):
        '''
        This is intentionally empty to disable mouse scrolling in the AddConnection combobox
        :param event: EVT_MOUSEWHEEL
        :return: None
        '''
        pass

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

    def load_data(self):
        raise Exception('Abstract method. Must be overridden!')

    def database_refresh(self, event):

        thr = threading.Thread(target=self.load_data, args=(), kwargs={})
        thr.start()

class SimulationDataTable(DataSeries):
    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)

        super(SimulationDataTable, self ).__init__(parent)

        self.table_columns = ["Simulation ID", "Simulation Name", "Model Name", "Simulation Start", "Simulation End", "Date Created","Owner"]
        #table_columns = ["ResultID", "FeatureCode", "Variable", "Unit", "Type", "Organization", "Date Created"]
        self.table.DefineColumns(self.table_columns)

        self.__selected_choice_idx = 0

        # build custom context menu
        menu = SimulationContextMenu(self.table)
        self.table.setContextMenu(menu)

    def load_data(self):

        # get the name of the selected database
        selected_db = self.connection_combobox.GetStringSelection()

        #set the selected choice
        self.__selected_choice_idx = self.connection_combobox.GetSelection()

        for key, db in self._databases.iteritems():

            # get the database session associated with the selected name
            if db['name'] == selected_db:

                # query the database and get basic series info



                u = dbapi.utils(db['session'])
                #simulations = u.getAllSeries()
                simulations = u.getAllSimulations()


                sim_ids = []
                if simulations is None:
                    d = {key: value for (key, value) in
                         zip([col.lower().replace(' ','_') for col in self.table_columns],["" for c in self.table_columns])}
                    record_object = type('DataRecord', (object,), d)
                    data = [record_object]
                else:
                    data = []

                    # loop through all of the returned data

                    for s in simulations:

                        simulation_id = s.Simulation.SimulationID

                        # only add if the simulation id doesn't already exist in sim_ids
                        if simulation_id not in sim_ids:
                            sim_ids.append(simulation_id)

                            d = {
                                'simulation_id' : s.Simulation.SimulationID,
                                'simulation_name' : s.Simulation.SimulationName,
                                'model_name' : s.Model.ModelName,
                                'date_created' : s.Action.BeginDateTime,
                                'owner' : s.Person.PersonLastName,
                                'simulation_start' : s.Simulation.SimulationStartDateTime,
                                'simulation_end' : s.Simulation.SimulationEndDateTime,
                            }

                            record_object = type('DataRecord', (object,), d)
                            data.extend([record_object])

                # set the data objects in the olv control
                self.table.SetObjects(data)

                # set the current database in canvas controller
                Publisher.sendMessage('SetCurrentDb',value=selected_db)  # sends to CanvasController.getCurrentDbSession


class TimeSeriesContextMenu(ContextMenu):
    def __init__(self, parent):
        super(TimeSeriesContextMenu, self).__init__(parent)


class SimulationContextMenu(ContextMenu):
    def __init__(self, parent):
        super(SimulationContextMenu, self).__init__(parent)

    def getData(self,simulationID):

        session = self.parent.getDbSession()
        if session is not None:


            readsim = readSimulation(session)
            core = readCore(session)
            readres = readResults(session)
            results = readsim.getResultsBySimulationID(simulationID)

            res = {}
            for r in results:

                variable_name = r.VariableObj.VariableCode
                result_values = readres.getTimeSeriesValuesByResultId(int(r.ResultID))

                dates = []
                values = []
                for val in result_values:
                    dates.append(val.ValueDateTime)
                    values.append(val.DataValue)


                # save data series based on variable
                if variable_name in res:
                    res[variable_name].append([dates,values,r])
                else:
                    res[variable_name] = [[dates,values,r]]



            return res

    def OnPlot(self, event):
        print 'overriding plot!'

        obj, id = self.Selected()
        #obj = self.__list_obj

        # create a plot frame
        PlotFrame = None
        xlabel = None
        title = None
        variable = None
        units = None
        warning = None
        x_series = []
        y_series = []
        labels = []
        id = self.parent.GetFirstSelected()
        while id != -1:
            # get the result
            simulationID = obj.GetItem(id,0).GetText()

            # get resultid from simulation id

            # get data for this row
            # x,y, resobj = self.getData(simulationID)
            results = self.getData(simulationID)



            if PlotFrame is None:

                # todo: plot more than just this first variable
                key = results.keys()[0]


                resobj = results[key][0][2]
                # set metadata based on first series
                xlabel = '%s, [%s]' % (resobj.UnitObj.UnitsName, resobj.UnitObj.UnitsAbbreviation)
                title = '%s' % (resobj.VariableObj.VariableCode)

                # save the variable and units to validate future time series
                variable = resobj.VariableObj.VariableCode
                units = resobj.UnitObj.UnitsName

                PlotFrame = MatplotFrame(self.Parent, title, xlabel)

                for x,y,resobj in results[key]:
                    # store the x and Y data
                    x_series.append(x)
                    y_series.append(y)
                    labels.append(int(resobj.ResultID))


                # PlotFrame.add_series(x,y)

            elif warning is None:
                warning = 'Multiple Variables/Units were selected.  I currently don\'t support plotting heterogeneous time series. ' +\
                          'Some of the selected time series will not be shown :( '

            # get the next selected item
            id = obj.GetNextSelected(id)

        if warning:
            dlg = wx.MessageDialog(self.parent, warning, '', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()

        # plot the data
        PlotFrame.plot(xlist=x_series, ylist=y_series, labels=labels)
        PlotFrame.Show()






































class consoleOutput(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)


        # Add a panel so it looks the correct on all platforms
        log = wx.TextCtrl(self, -1, size=(100,100),
                          style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        #redir= RedirectText(log)
        #sys.stdout=redir


        # # Add widgets to a sizer
        sizer = wx.BoxSizer()
        sizer.Add(log, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)


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

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

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