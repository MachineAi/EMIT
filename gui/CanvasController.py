
__author__ = 'Mario'

import wx
import random
import math
import math
#from GUIControl import GUIBase
import textwrap as tw
ver = 'local'
from utilities import gui

import sys
sys.path.append("..")
for x in sys.path:
    print x

from wx.lib.floatcanvas import FloatCanvas as FC
from wx.lib.floatcanvas.Utilities import BBox
from wx.lib.floatcanvas.NavCanvas import NavCanvas
from wx.lib.pubsub import pub as Publisher
import numpy as N
import os
import math
import markdown2
from LinkDialogueBox import LinkBox
import CanvasObjects
import LinkWizard
from LinkStart import LinkStart
from ContextMenu import LinkContextMenu, ModelContextMenu, GeneralContextMenu
from wrappers import odm2_data
import xml.etree.ElementTree as et
from xml.dom import minidom

import datatypes
from DirectoryView import DirectoryCtrlView as DCV
from api.ODM2.Core.services import readCore
from api.ODM2.Results.services import readResults
from api.ODM2.Core.services import readCore

class CanvasController:
    def __init__(self, cmd, Canvas):
        self.Canvas = Canvas
        self.FloatCanvas = self.Canvas.Canvas
        self.cmd = cmd

        self.UnBindAllMouseEvents()

        self.MoveObject = None
        self.Moving = False

        self.initBindings()
        self.initSubscribers()

        defaultCursor = wx.StockCursor(wx.CURSOR_DEFAULT)
        defaultCursor.Name = 'default'
        self._Cursor = defaultCursor

        self.Canvas.ZoomToFit(Event=None)

        dt = FileDrop(self, self.Canvas, self.cmd)
        self.Canvas.SetDropTarget(dt)

        self.linkRects = []
        self.links = {}
        self.models = {}
        self.dbmodel_required_db = {}

        self.link_clicks = 0


        self._currentDbSession = self.cmd.get_default_db()

    def UnBindAllMouseEvents(self):
        ## Here is how you unbind FloatCanvas mouse events
        self.Canvas.Unbind(FC.EVT_LEFT_DOWN)
        self.Canvas.Unbind(FC.EVT_LEFT_UP)
        self.Canvas.Unbind(FC.EVT_LEFT_DCLICK)

        self.Canvas.Unbind(FC.EVT_MIDDLE_DOWN)
        self.Canvas.Unbind(FC.EVT_MIDDLE_UP)
        self.Canvas.Unbind(FC.EVT_MIDDLE_DCLICK)

        self.Canvas.Unbind(FC.EVT_RIGHT_DOWN)
        self.Canvas.Unbind(FC.EVT_RIGHT_UP)
        self.Canvas.Unbind(FC.EVT_RIGHT_DCLICK)

        self.EventsAreBound = False

    def initBindings(self):
        self.FloatCanvas.Bind(FC.EVT_MOTION, self.OnMove )
        self.FloatCanvas.Bind(FC.EVT_LEFT_UP, self.OnLeftUp )
        # self.FloatCanvas.Bind(FC.EVT_RIGHT_DOWN, self.onRightDown)
        self.FloatCanvas.Bind(FC.EVT_LEFT_DOWN, self.onLeftDown)
        self.FloatCanvas.Bind(FC.EVT_RIGHT_DOWN, self.LaunchContext)

    def initSubscribers(self):
        Publisher.subscribe(self.createBox, "createBox")
        Publisher.subscribe(self.setCursor, "setCursor")
        Publisher.subscribe(self.run, "run")
        Publisher.subscribe(self.clear, "clear")
        Publisher.subscribe(self.AddDatabaseConnection, "DatabaseConnection")
        Publisher.subscribe(self.getDatabases, "getDatabases")
        Publisher.subscribe(self.getCurrentDbSession, "SetCurrentDb")
        Publisher.subscribe(self.SaveSimulation, "SetSavePath")
        Publisher.subscribe(self.loadsimulation, "SetLoadPath")
        Publisher.subscribe(self.addModel, "AddModel")  # subscribes to object list view

    def OnMove(self, event):
        """
        Updates the status bar with the world coordinates
        and moves the object it is clicked on

        """

        if self.Moving:
            dxy = event.GetPosition() - self.StartPoint
            # Draw the Moving Object:
            dc = wx.ClientDC(self.FloatCanvas)
            dc.SetPen(wx.Pen('WHITE', 2, wx.SHORT_DASH))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetLogicalFunction(wx.XOR)
            if self.MoveObject is not None:
                dc.DrawPolygon(self.MoveObject)
            self.MoveObject = self.StartObject + dxy
            dc.DrawPolygon(self.MoveObject)

    def LaunchContext(self, event):

        # get hit object
        #self.GetHitObject(event, event.EventType)

        # if canvas is selected
        if type(event) == wx.lib.floatcanvas.FloatCanvas._MouseEvent:
            self.Canvas.PopupMenu(GeneralContextMenu(self), event.GetPosition())

        elif type(event) == wx.lib.floatcanvas.FloatCanvas.Polygon:
            #if object is link
            if event.type == "ArrowHead":
                self.Canvas.PopupMenu(LinkContextMenu(self,event), event.HitCoordsPixel.Get())

            # if object is model
            elif event.type == 'Model':
                self.Canvas.PopupMenu(ModelContextMenu(self,event), event.HitCoordsPixel.Get())

        # # if object is neither
        # else:
        #     self.Canvas.PopupMenu(GeneralContextMenu(self), event.GetPosition())


        #self.Canvas.ClearAll()
        #self.Canvas.Draw()

    def run(self):

        self.cmd.run_simulation()

    def getCurrentDbSession(self, value = None):
        if value is not None:
            dbs = self.cmd.get_db_connections()
            for db in dbs.iterkeys():
                if dbs[db]['name'] == value:
                    self._currentDbSession = dbs[db]['session']
                    break
        return self._currentDbSession

    def RemoveLink(self, link_obj):

        # remove the link entry in self.links
        link = self.links.pop(link_obj)

        # remove the link from the cmd
        from_id = link[0].ID
        to_id = link[1].ID

        # get the link id
        links = self.cmd.get_links_btwn_models(from_id,to_id)

        # remove all links
        for link in links:
            linkid = link.get_id()
            self.cmd.remove_link_by_id(linkid)

        # redraw the canvas
        self.RedrawConfiguration()

    def onLeftDown(self, event):
        pass

    def setCursor(self, value=None):
        #print "Cursor was set to value ", dir(value), value.GetHandle()
        self._Cursor=value

    def getCursor(self):
        return self._Cursor

    def createBox(self, xCoord, yCoord, id=None, name=None, color='#A2CAF5'):

        if name:


            w, h = 180, 120
            WH = (w/2, h/2)
            x,y = xCoord, yCoord
            FontSize = 14
            #filename = os.path.basename(filepath)

            # get the coordinates for the rounded rectangle
            rect_coords = CanvasObjects.build_rounded_rectangle((x,y), width=w, height=h)

            R = self.FloatCanvas.AddObject(FC.Polygon(rect_coords,FillColor=color,InForeground=True))

            #R = self.FloatCanvas.AddRectangle((x,y), (w,h), LineWidth = 2, FillColor = "BLUE",InForeground=True)
            #R.HitFill = True
            R.ID = id
            R.Name = name
            R.wh = (w,h)
            R.xy = (x,y)

            # set the shape type so that we can identify it later
            R.type = CanvasObjects.ShapeType.Model

            width = 15
            wrappedtext = tw.wrap(unicode(name), width)
            # new_line = []
            # for line in wrappedtext:
            #
            #     frontpadding = int(math.floor((width - len(line))/2))
            #     backpadding = int(math.ceil((width - len(line))/2))
            #     line = ' '*frontpadding + line
            #     line += ' '*backpadding
            #     new_line.append(line)

            #FC.DrawLabel(self, text, rect, alignment=wxALIGN_LEFT|wxALIGN_TOP, indexAccel=-1)

            #label = self.FloatCanvas.AddObject(textbox)

            # define the font
            font = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            # print "font", font.GetPixelSize()
            #
            # textwidth =len(max(wrappedtext))*font.GetPixelSize()[1]
            # textheight = len(wrappedtext)*font.GetPixelSize()[1]
            # location = (x - .25*textwidth,y+.5*textheight)

            label = self.FloatCanvas.AddScaledTextBox(unicode(name), (x,y), #(x+1, y+h/2),
                                        Color = "Black",  Size = FontSize, Width= w-10, Position = "cc", Alignment = "center",
                                        Weight=wx.BOLD, Style=wx.ITALIC, InForeground=True, Font = font, LineWidth = 0, LineColor = None)


            # set the type of this object so that we can find it later
            label.type = CanvasObjects.ShapeType.Label

            # add this text as an attribute of the rectangle
            R.Text = label

            print '> ', name, ' has been added to the canvas.'
            #print dir(label), label
            #R.Bind(FC.EVT_FC_LEFT_UP, self.OnLeftUp )

            R.Bind(FC.EVT_FC_LEFT_DOWN, self.ObjectHit)
            R.Bind(FC.EVT_FC_RIGHT_DOWN, self.LaunchContext)

            ### R.Bind(FC.EVT_FC_RIGHT_DOWN, self.RightClickCb )
            #self.Canvas.Bind(FC.EVT_FC_LEFT_DOWN, self.ObjectHit, id=R.ID)

            self.models[R]=id

            self.FloatCanvas.Draw()

        else:
            # print "Nothing Selected"
            pass

    def createLine(self, R1, R2):
        #print "creating link", R1, R2
        x1,y1  = (R1.BoundingBox[0] + (R1.wh[0]/2, R1.wh[1]/2))
        x2,y2  = (R2.BoundingBox[0] + (R2.wh[0]/2, R2.wh[1]/2))

        length = (((x2 - x1)**2)+(y2 - y1)**2)**.5
        dy = (y2 - y1)
        dx = (x2 - x1)
        angle = 90- math.atan2(dy,dx) *180/math.pi

        #print 'angle: ',angle
        from matplotlib.pyplot import cm
        cmap = cm.Blues
        line = CanvasObjects.get_line_pts((x1,y1),(x2,y2),order=4, num=200)
        linegradient = CanvasObjects.get_hex_from_gradient(cmap, len(line))
        linegradient.reverse()
        arrow = CanvasObjects.build_arrow(line, arrow_length=6)
       # print arrow

        for i in range(0,len(line)-1):
            l = FC.Line((line[i],line[i+1]),LineColor=linegradient[i],LineWidth=2,InForeground=False)
            l.type = CanvasObjects.ShapeType.Link
            self.FloatCanvas.AddObject(l)

        # create the arrowhead object
        arrow_shape = FC.Polygon(arrow,FillColor='Blue',InForeground=True)

        # set the shape type so that we can identify it later
        arrow_shape.type = CanvasObjects.ShapeType.ArrowHead
        self.FloatCanvas.AddObject(arrow_shape)

        # bind the arrow to left click
        arrow_shape.Bind(FC.EVT_FC_LEFT_DOWN, self.ArrowClicked)
        arrow_shape.Bind(FC.EVT_FC_RIGHT_DOWN, self.LaunchContext)


        # store the link and rectangles in the self.links list
        for k,v in self.links.iteritems():
            if v == [R1,R2]:
                self.links.pop(k)
                break
        self.links[arrow_shape] = [R1,R2]


        self.Canvas.Canvas.Draw()

    def ObjectHit(self, object):
        print "Hit Object(CanvasController)", object.Name
        #self.FloatCanvas.Bind(FC.EVT_FC_RIGHT_DOWN( list, -1, self.RightClickCb ))
        cur = self.getCursor()

        if cur.Name == 'link':
            self.linkRects.append(object)
        # if cur.Name == 'link':
        #     if len(self.linkRects)  > 0:
        #         self.linkRects.append(object)
        #         self.createLine(self.linkRects[0], self.linkRects[1])
        #
        #         # reset linkrects object
        #         self.linkRects=[]
        #
        #         # change the mouse cursor
        #
        #         #self.Canvas.SetMode(self.Modes[0][1])
        #
        #     else:
        #         self.linkRects.append(object)

        # populate model view
        if cur.Name == 'default':
            # get the model view container
            mainGui = self.Canvas.GetTopLevelParent()
            mv = mainGui.Children[0].FindWindowByName('notebook').GetPage(1)

            #mv = self.Canvas.GetTopLevelParent().m_mgr.GetPane(n

            # get the model object from cmd
            obj_id = object.ID
            obj = self.cmd.get_model_by_id(obj_id)

            # format the model parameters for printing

            try:
                params = obj.get_config_params()
                if params is None:
                    params = {}
            except: params = {}

            text = ''

            for arg,dict in params.iteritems():
                title = arg

                try:
                    table = ''
                    for k,v in dict[0].iteritems():
                        table += '||%s||%s||\n' % (k, v)

                    text += '###%s  \n%s  \n'%(title,table)
                except: pass

            #text = '\n'.join([k for k in params.keys()])

            #text = '||a||b||\n||test||test||\n||test||test||'

            #md = "###Heading\n---\n```\nsome code\n```"
            html = markdown2.markdown(text, extras=["wiki-tables"])

            #css = "<style>h3 a{font-weight:100;color: gold;text-decoration: none;}</style>"
            css = "<style>tr:nth-child(even) " \
                    "{ background-color: #e6f1f5;} " \
                    "table {border-collapse: collapse;width:100%}" \
                    "table td, table th {border: 1px solid #e6f1f5;}" \
                    "h3 {color: #66A3E0}</style>"




            # set the model params as text
            try:
                mv.setText(css + html)

            except:
                pass



        if not self.Moving:
            self.Moving = True
            self.StartPoint = object.HitCoordsPixel

            BB = object.BoundingBox
            OutlinePoints = N.array(
            ( (BB[0, 0], BB[0, 1]), (BB[0, 0], BB[1, 1]), (BB[1, 0], BB[1, 1]), (BB[1, 0], BB[0, 1]),
            ))
            self.StartObject = self.FloatCanvas.WorldToPixel(OutlinePoints)
            self.MoveObject = None
            self.MovingObject = object

    def RedrawConfiguration(self):
        # clear lines from drawlist
        self.FloatCanvas._DrawList = [obj for obj in self.FloatCanvas._DrawList if obj.type != CanvasObjects.ShapeType.Link]
        #self.FloatCanvas._DrawList = [obj for obj in self.FloatCanvas._DrawList if type(obj) != FC.Line]

        # remove any arrowheads from the _ForeDrawList
        self.FloatCanvas._ForeDrawList = [obj for obj in self.FloatCanvas._ForeDrawList if obj.type != CanvasObjects.ShapeType.ArrowHead]
        #self.FloatCanvas._ForeDrawList = [obj for obj in self.FloatCanvas._ForeDrawList if type(obj) != FC.Polygon]

        # remove any models
        i = 0
        modelids = [model.ID for model in self.models]
        modellabels = [model.Name for model in self.models]
        self.FloatCanvas._ForeDrawList = [obj for obj in self.FloatCanvas._ForeDrawList
                                          if (obj.type == CanvasObjects.ShapeType.Model and obj.ID in modelids)
                                          or (obj.type == CanvasObjects.ShapeType.Label and obj.String in modellabels)]


        # redraw links
        for link in self.links.keys():
            r1,r2 = self.links[link]
            self.createLine(r1,r2)

        self.FloatCanvas.Draw(True)

    def OnLeftUp(self, event):
        if self.Moving:
            self.Moving = False
            if self.MoveObject is not None:
                dxy = event.GetPosition() - self.StartPoint
                (x,y) = self.FloatCanvas.ScalePixelToWorld(dxy)
                self.MovingObject.Move((x,y))
                self.MovingObject.Text.Move((x, y))


                # clear lines from drawlist
                self.FloatCanvas._DrawList = [obj for obj in self.FloatCanvas._DrawList if obj.type != CanvasObjects.ShapeType.Link]
                #self.FloatCanvas._DrawList = [obj for obj in self.FloatCanvas._DrawList if type(obj) != FC.Line]

                # remove any arrowheads from the _ForeDrawList
                self.FloatCanvas._ForeDrawList = [obj for obj in self.FloatCanvas._ForeDrawList if obj.type != CanvasObjects.ShapeType.ArrowHead]
                #self.FloatCanvas._ForeDrawList = [obj for obj in self.FloatCanvas._ForeDrawList if type(obj) != FC.Polygon]

                # redraw links
                for link in self.links.keys():
                    r1,r2 = self.links[link]
                    self.createLine(r1,r2)

            self.FloatCanvas.Draw(True)


        # count clicks
        cur = self.getCursor()
        if cur.Name == 'link':
            self.AddinkCursorClick()




        #if self.link

        # create link
        #if len(self.linkRects)  > 0:
        #         self.linkRects.append(object)
        #         self.createLine(self.linkRects[0], self.linkRects[1])
        #
        #         # reset linkrects object
        #         self.linkRects=[]
        #
        #         #

    def AddinkCursorClick(self):
        self.link_clicks += 1

        if self.link_clicks == 2:
            if len(self.linkRects) == 2:
                self.createLine(self.linkRects[0], self.linkRects[1])

            # reset
            self.link_clicks = 0
            self.linkRects=[]

            #change the mouse cursor


            self.FloatCanvas.SetMode(self.Canvas.GuiMouse)


            # e = e = wx._core.CommandEvent(10013)
            # e.Id = -2017
            # # self.Canvas.GuiMouse.OnLeftUp(e)
            # #self.Canvas.
            # self.Canvas.SetMode(e)

    def GetHitObject(self, event, HitEvent):
        if self.Canvas.Canvas.HitDict:
            # check if there are any objects in the dict for this event
            if self.Canvas.Canvas.HitDict[ HitEvent ]:
                xy = event.GetPosition()
                color = self.Canvas.Canvas.GetHitTestColor( xy )
                if color in self.Canvas.Canvas.HitDict[ HitEvent ]:
                    Object = self.Canvas.Canvas.HitDict[ HitEvent ][color]
                    #self.Canvas._CallHitCallback(Object, xy, HitEvent)
                    return Object
            return False

    def ArrowClicked(self,event):

        #if event

        #self.Log("The Link was Clicked")

        # get the models associated with the link
        polygons = self.links[event]

        # get r1 and r2
        r1 = polygons[0]
        r2 = polygons[1]

        # get output items from r1
        from_model = self.cmd.get_model_by_id(r1.ID)

        # get exchange items
        inputitems = from_model.get_output_exchange_items()
        # get output items from r1
        to_model = self.cmd.get_model_by_id(r2.ID)

        # get exchange items
        outputitems = to_model.get_input_exchange_items()



        # for item in eitems:
        #     print 'Type: ', item.get_type()
        #     print "Name: ", item.name()
        #     print "Variable: ", item.variable().VariableNameCV()
        #     print "Unit: ", item.unit().UnitName()
        #     print 10*'-'
        #
        #
        #
        # for item in eitems:
        #     print 'Type: ', item.get_type()
        #     print "Name: ", item.name()
        #     print "Variable: ", item.variable().VariableNameCV()
        #     print "Unit: ", item.unit().UnitName()
        #     print 10*'-'


        # print "The Link was clicked"
        linkstart = LinkStart(self.FloatCanvas, from_model, to_model, inputitems, outputitems, self.cmd)
        linkstart.Show()
        #linkwiz = LinkWizard.wizLink(self.FloatCanvas, inputitems, outputitems)

        # dlg = LinkBox()
        # dlg.ShowModal()
        # dlg.Destroy()
        #Example()

    def RightClickCb( self, event ):
        # record what was clicked
        #self.list_item_clicked = right_click_context = event.GetText()


        # get the link object
        # get the model id's from the link
        # get the model objects from the models id's
        menu = wx.Menu()
        for (id,title) in menu_title_by_id.items():
            menu.Append( id, title )
            wx.EVT_MENU( menu, id, self.MenuSelectionCb )

        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.frame.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def RemoveModel(self, model_obj):


        # remove the model from the canvas
        removed_model = self.models.pop(model_obj)

        updated_links = {}
        for k,v in self.links.iteritems():
            if model_obj not in v:
                updated_links[k] = v
        self.links = updated_links

        # remove the model from the cmd engine
        self.cmd.remove_model_by_id(model_obj.ID)

        # redraw the canvas
        self.RedrawConfiguration()

    def AddDatabaseConnection(self, title, desc, engine, address, name, user, pwd):

        # build the database connection
        connection = gui.create_database_connections_from_args(title, desc, engine, address, name, user, pwd)


        if type(connection) == dict and any(connection):
            # store the connection
            self.cmd.add_db_connection(connection)

            # notify that the connection was added successfully
            Publisher.sendMessage('connectionAddedStatus',value=True,connection_string=connection[connection.keys()[0]]['connection_string'])  # sends message to mainGui

            return True
        else:
            # notify that the connection was not added successfully
            Publisher.sendMessage('connectionAddedStatus',value=False,connection_string=connection) # sends message to mainGui

            return False

    def getDatabases(self):
        knownconnections = self.cmd.get_db_connections()
        Publisher.sendMessage('getKnownDatabases',value=knownconnections)  # sends message to mainGui

    def MenuSelectionCb( self, event ):
        # do something
        operation = menu_title_by_id[ event.GetId() ]
        #target    = self.list_item_clicked
        print '> Perform "%(operation)s" on "%(target)s."' % vars()

    def clear(self, link_obj=None, model_obj=None):

        # clear links and models in cmd
        self.cmd.clear_all()

        # clear links and model in gui
        self.links.clear()
        self.models.clear()

        self.RedrawConfiguration()

    def DetailView(self):
        # DCV.ShowDetails()
        pass

    def SaveSimulation(self, path):

        if len(self.models.keys()) == 0:
            print '> Nothing to save!'
            return

        # create an xml tree
        tree = et.Element('Simulation')

        links = []
        db_ids = []
        # add models to the xml tree
        for shape, modelid in self.models.iteritems():
            attributes = {}
            model = self.cmd.get_model_by_id(modelid)
            bbox = shape.BoundingBox
            attributes['x'] = str((bbox[0][0] + bbox[1][0]) / 2)
            attributes['y'] = str((bbox[0][1] + bbox[1][1]) / 2)
            attributes['name'] = model.get_name()
            attributes['id'] = model.get_id()

            if model.type() == datatypes.ModelTypes.FeedForward:
                attributes['mdl'] = model.params_path()
                et.SubElement(tree,'Model',attributes)

            elif model.type() == datatypes.ModelTypes.Data:
                attributes['databaseid'] = model.attrib()['databaseid']
                attributes['resultid'] = model.attrib()['resultid']
                et.SubElement(tree,'DataModel',attributes)

                # save this db id
                if model.attrib()['databaseid'] not in db_ids:
                    db_ids.append(model.attrib()['databaseid'])

            link = self.cmd.get_links_by_model(modelid)
            for l in link:
                if l not in links:
                    links.append(l)

        # add links to the xml tree
        for link in links:
            attributes = {}

            from_model, from_item = link[0]
            to_model, to_item = link[1]


            attributes['from_name'] = from_model.get_name()
            attributes['from_id'] = from_model.get_id()
            attributes['from_item'] = from_item.name()
            attributes['from_item_id'] = from_item.get_id()

            attributes['to_name'] = to_model.get_name()
            attributes['to_id'] = to_model.get_id()
            attributes['to_item'] = to_item.name()
            attributes['to_item_id'] = to_item.get_id()

            et.SubElement(tree,'Link',attributes)


        # save required databases
        for db_id in db_ids:
            attributes = {}

            connections = self.cmd.get_db_connections()

            db_conn = connections[db_id]['args']

            if db_conn:
                attributes['name'] = db_conn['name']
                attributes['desc'] = db_conn['desc']
                attributes['engine'] = db_conn['engine']
                attributes['address'] = db_conn['address']
                attributes['db'] = db_conn['db']
                attributes['user'] = db_conn['user']
                attributes['pwd'] = db_conn['pwd']
                attributes['databaseid'] = db_conn['id']
                attributes['connection_string'] = str(db_conn['connection_string'])
                et.SubElement(tree,'DbConnection',attributes)


        # format the xml nicely
        rough_string = et.tostring(tree, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        prettyxml = reparsed.toprettyxml(indent="  ")

        # save the xml doc
        with open(path,'w') as f:
            f.write(prettyxml)

    def loadsimulation(self, file):
        #TODO: Should be part of the cmd.
        tree = et.parse(file)

        # get the root
        root = tree.getroot()

        # make sure the required database connections are loaded
        connections = self.cmd.get_db_connections()
        conn_ids = {}
        for db_conn in root.iter('DbConnection'):

            database_exists = False
            for id, dic in connections.iteritems():
                if str(dic['args']['connection_string']) == db_conn.attrib['connection_string']:
                    #dic['args']['id'] = db_conn.attrib['id']
                    database_exists = True

                    # map the connection ids
                    conn_ids[db_conn.attrib['databaseid']] = dic['args']['id']
                    break

            # if database doesn't exist, then connect to it
            if not database_exists:
                connect = wx.MessageBox('This database connection does not currently exist.  Click OK to connect.', 'Info', wx.OK | wx.ICON_ERROR)


                if connect.ShowModal() != wx.OK:

                    # attempt to connect to the database
                    title=dic['args']['name'],
                    desc = dic['args']['desc'],
                    engine = dic['args']['engine'],
                    address = dic['args']['address'],
                    name = dic['args']['db'],
                    user = dic['args']['user'],
                    pwd = dic['args']['pwd']

                    if not self.AddDatabaseConnection(title,desc,engine,address,name,user, pwd):
                        wx.MessageBox('I was unable to connect to the database with the information provided :(', 'Info', wx.OK | wx.ICON_ERROR)
                        return

                    # map the connection id
                    conn_ids[db_conn.attrib['id']] = db_conn.attrib['id']

                else: return


        # loop through each model and load it
        for model in root.iter('Model'):

            # get the data type
            dtype = datatypes.ModelTypes.FeedForward

            # load the model
            #self.cmd.add_model(model.attrib['mdl'], id=model.attrib['id'],type=dtype)
            self.cmd.add_model(dtype,id=model.attrib['id'], attrib=model.attrib)

            # draw the box
            name = model.attrib['name']
            modelid = model.attrib['id']

            x = float(model.attrib['x'])
            y = float(model.attrib['y'])

            self.createBox(name=name, id=modelid, xCoord=x, yCoord=y)

        for data in root.iter('DataModel'):

            # get the data type
            dtype = datatypes.ModelTypes.Data

            resultid = data.attrib['resultid']
            databaseid = data.attrib['databaseid']
            mappedid = conn_ids[databaseid]

            #model = self.cmd.add_data_model(resultid,mappedid,id=data.attrib['id'],type=dtype)
            data.attrib['databaseid'] = mappedid
            model = self.cmd.add_model(dtype,id=data.attrib['id'], attrib=data.attrib)

            x = float(data.attrib['x'])
            y = float(data.attrib['y'])


            self.createBox(name=model.get_name(), id=model.get_id(), xCoord=x, yCoord=y, color='#FFFF99')

        for link in root.iter('Link'):

            R1 = None
            R2 = None
            for R, id in self.models.iteritems():
                if id == link.attrib['from_id']:
                    R1 = R
                elif id == link.attrib['to_id']:
                    R2 = R

            if R1 is None or R2 is None:
                raise Exception('Could not find Model identifer in loaded models')

            # add the link object
            self.cmd.add_link_by_name(  link.attrib['from_id'], link.attrib['from_item'],
                                link.attrib['to_id'], link.attrib['to_item'])

            # this draws the line
            self.createLine(R1,R2)



        self.FloatCanvas.Draw()
        #self.Canvas.Draw()


    def addModel(self, filepath, x, y):
        """
        Adds a model to the canvas using x,y.  This is useful if adding by file click/dialog
        :param filename:  filename / path
        :param x: x location
        :param y: y location
        :return: None
        """

        # controller = self
        # window = self.Canvas
        # cmd = self.cmd)

        x0 = self.Canvas.MinWidth / 2.
        y0 = self.Canvas.MinHeight / 2.

        originx, originy = self.Canvas.Canvas.PixelToWorld((0,0))
        x = x0 +originx
        y = originy - y0

        name, ext = os.path.splitext(filepath)

        if ext == '.mdl' or ext =='.sim':
            try:
                if ext == '.mdl':
                    # load the model
                    dtype = datatypes.ModelTypes.FeedForward
                    model = self.cmd.add_model(dtype,attrib={'mdl':filepath})
                    name = model.get_name()
                    modelid = model.get_id()
                    self.createBox(name=name, id=modelid, xCoord=x, yCoord=y)

                else:
                    # load the simulation
                    self.loadsimulation(filepath)

            except Exception, e:
                print '> Could not load the model. Please verify that the model file exists.'
                print '> %s' % e
        else:
            # # -- must be a data object --

            # get the current database connection dictionary
            session = self.getCurrentDbSession()

            # create odm2 instance
            inst = odm2_data.odm2(resultid=name, session=session)

            from coordinator import main
            # create a model instance
            thisModel = main.Model(id=inst.id(),
                                   name=inst.name(),
                                   instance=inst,
                                   desc=inst.description(),
                                   input_exchange_items= [],
                                   output_exchange_items=  [inst.outputs()],
                                   params=None)


            # save the result id
            att = {'resultid':name}

            # save the database connection
            dbs = self.cmd.get_db_connections()
            for id, dic in dbs.iteritems():
                if dic['session'] == self.getCurrentDbSession():
                    att['databaseid'] = id
                    thisModel.attrib(att)
                    break

            thisModel.type(datatypes.ModelTypes.Data)


            # save the model
            self.cmd.Models(thisModel)

            # draw a box for this model
            self.createBox(name=inst.name(), id=inst.id(), xCoord=x, yCoord=y, color='#FFFF99')
            self.Canvas.Canvas.Draw()

class FileDrop(wx.FileDropTarget):
    def __init__(self, controller, window, cmd):
        wx.FileDropTarget.__init__(self)
        self.controller = controller
        self.window = window
        self.cmd = cmd

    def OnDropFiles(self, x, y, filenames):
        #print "filename: {2} x: {0} y: {1}".format(x,y, filenames)

        #Canvas = NC.NavCanvas(self, -1, size=wx.DefaultSize).Canvas
        #Canvas.AddRectangle((110, 10), (100, 100), FillColor='Red')
        #print x,y
        originx, originy = self.window.Canvas.PixelToWorld((0,0))
        #ar = self.window.Canvas.ScreenPosition
        #x-= ar[0]
        x = x +originx
        y = originy - y
        #x, y = self.window.Canvas.WorldToPixel((nx,ny))
        #print x,y
        #x = y = 0

        link_objs = []

        # make sure the correct file type was dragged
        name, ext = os.path.splitext(filenames[0])
        if ext == '.mdl' or ext =='.sim':

            models = None
            try:
                if ext == '.mdl':

                    dtype = datatypes.ModelTypes.FeedForward

                    # load the model
                    #self.cmd.add_model(model.attrib['mdl'], id=model.attrib['id'],type=dtype)
                    model = self.cmd.add_model(dtype,attrib={'mdl':filenames[0]})

                    # load the model (returns model instance
                    #model = self.cmd.add_model(filenames[0],type=dtype)

                    name = model.get_name()
                    modelid = model.get_id()

                    self.controller.createBox(name=name, id=modelid, xCoord=x, yCoord=y)

                else:
                    # load the simulation
                    #models, links, link_objs = self.cmd.load_simulation(filenames[0])
                    self.controller.loadsimulation(filenames[0])

                    # array = N.zeros((3,3))
                    # index_order = [(1,1),(0,0),(2,2),(2,0),(2,2),(0,1),(1,0),(1,2),(2,1)]
                    # # draw boxes for each model
                    # offset = 0
                    # for model in list(models):
                    #     # get the name and id of the model
                    #     name = model.get_name()
                    #     modelid = model.get_id()
                    #
                    #     newx = random.randrange(-1,2)*offset + x
                    #     newy = random.randrange(-1,2)*offset + y
                    #
                    #     self.controller.createBox(name=name, id=modelid, xCoord=newx, yCoord=newy)
                    #     self.window.Canvas.Draw()
                    #     offset=200

                    # draw the link line

                    # for link in list(link_objs):
                    #
                    #     R1 = self.controller.models.keys()[self.controller.models.values().index(link[0])]
                    #     R2 = self.controller.models.keys()[self.controller.models.values().index(link[2])]
                    #     self.controller.createLine(R1,R2)

            except Exception, e:
                print '> Could not load the model. Please verify that the model file exists.'
                print '> %s' % e

        else:
            # # -- must be a data object --
            #
            #
            # # get info about the data series
            # from ODM2.Core.services import readCore
            # from ODM2.Results.services import readResults
            # from shapely import wkb
            # import stdlib, uuid
            #
            # # get the session
            # session = self.controller.getCurrentDbSession()
            #
            # # get result object and result timeseries
            # core = readCore(session)
            # obj = core.getResultByID(resultID=int(name))
            # readres = readResults(session)
            # results = readres.getTimeSeriesValuesByResultId(resultId=int(name))
            #
            # # separate the date and value pairs in the timeseries
            # dates = [date.ValueDateTime for date in results]
            # values = [val.DataValue for val in results]
            #
            # # basic exchange item info
            # id = uuid.uuid4().hex[:8]
            # name = obj.VariableObj.VariableCode
            # desc = obj.VariableObj.VariableDefinition
            # #unit = obj.UnitObj.UnitsName
            # #vari = obj.VariableObj.VariableNameCV
            # type = stdlib.ExchangeItemType.Output
            # start = min(dates)
            # end = max(dates)
            #
            # # build datavalue object
            # data = stdlib.DataValues(timeseries=zip(dates,values))
            #
            # # build geometry object
            # # todo: this assumes single geometry! fix
            # shape = wkb.loads(str(obj.FeatureActionObj.SamplingFeatureObj.FeatureGeometry.data))
            # geometry = stdlib.Geometry(geom=shape,srs=None,elev=None,datavalues=data)
            #
            # # build variable
            # variable = stdlib.Variable()
            # variable.VariableDefinition(obj.VariableObj.VariableDefinition)
            # variable.VariableNameCV(obj.VariableObj.VariableNameCV)
            #
            # # build unit
            # unit = stdlib.Unit()
            # unit.UnitAbbreviation(obj.UnitObj.UnitsAbbreviation)
            # unit.UnitName(obj.UnitObj.UnitsName)
            # unit.UnitTypeCV(obj.UnitObj.UnitsTypeCV)
            #
            # # build exchange item object
            # item = stdlib.ExchangeItem(id=id, name=name, desc=desc, geometry=[geometry], unit=unit, variable=variable,type=type )



            # create an instance of data wrapper
            #dwrapper_inst = odm2_data.odm2(resultid=name, session=self.controller.getCurrentDbSession())


            # generate a unique model id
            #id = uuid.uuid4().hex[:8]

            # get the current database connection dictionary
            session = self.controller.getCurrentDbSession()

            # create odm2 instance
            inst = odm2_data.odm2(resultid=name, session=session)

            oei = inst.outputs().values()

            from coordinator import main
            # create a model instance
            thisModel = main.Model(id=inst.id(),
                                   name=inst.name(),
                                   instance=inst,
                                   desc=inst.description(),
                                   input_exchange_items= [],
                                   output_exchange_items=  oei,
                                   params=None)


            # save the result id
            att = {'resultid':name}

            # save the database connection
            dbs = self.cmd.get_db_connections()
            for id, dic in dbs.iteritems():
                if dic['session'] == self.controller.getCurrentDbSession():
                    att['databaseid'] = id
                    thisModel.attrib(att)
                    break

            thisModel.type(datatypes.ModelTypes.Data)


            # save the model
            self.cmd.Models(thisModel)

            #self.cmd.__models[name] = thisModel


            # draw a box for this model
            self.controller.createBox(name=inst.name(), id=inst.id(), xCoord=x, yCoord=y, color='#FFFF99')
            self.window.Canvas.Draw()


    def getObj(self,resultID):

        session = self.getDbSession()

        core = readCore(session)
        obj = core.getResultByID(resultID=int(resultID))

        session.close()

        return obj

    def getData(self,resultID):


        session = self.getDbSession()
        readres = readResults(session)
        results = readres.getTimeSeriesValuesByResultId(resultId=int(resultID))

        core = readCore(session)
        obj = core.getResultByID(resultID=int(resultID))

        dates = []
        values = []
        for val in results:
            dates.append(val.ValueDateTime)
            values.append(val.DataValue)

        session.close()

        return dates,values,obj

menu_titles = [ "Open",
                "Properties",
                "Rename",
                "Delete" ]

menu_title_by_id = {}
for title in menu_titles:
    menu_title_by_id[ wx.NewId() ] = title