
__author__ = 'Mario'

import wx
import random
import math
import math
#from GUIControl import GUIBase
import textwrap as tw
ver = 'local'

import sys
sys.path.append("..")
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
        self.links = []
        self.models = {}

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
        #self.FloatCanvas.Bind(FC.EVT_RIGHT_DOWN, self.onRightDown)
        self.FloatCanvas.Bind(FC.EVT_LEFT_DOWN, self.onLeftDown)

    def initSubscribers(self):
        Publisher.subscribe(self.createBox, "createBox")
        Publisher.subscribe(self.setCursor, "setCursor")

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

    def onRightDown(self, event):
        self.Canvas.ClearAll()
        self.Canvas.Draw()

    def onLeftDown(self, event):
        pass

    def setCursor(self, value=None):
        #print "Cursor was set to value ", dir(value), value.GetHandle()
        self._Cursor=value

    def getCursor(self):
        return self._Cursor

    def createBox(self, xCoord, yCoord, id=None, name=None):

        if name:
            w, h = 180, 120
            WH = (w/2, h/2)
            x,y = xCoord, yCoord
            FontSize = 14
            #filename = os.path.basename(filepath)

            R = self.FloatCanvas.AddRectangle((x,y), (w,h), LineWidth = 2, FillColor = "BLUE")
            R.HitFill = True
            R.ID = id
            R.Name = name
            R.wh = (w,h)
            R.xy = (x,y)

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

            #print wrappedtext, 'R:', dir(R)
            label = self.FloatCanvas.AddText("\n".join(wrappedtext), (x+1, y+h/2),
                                        Color = "White",  Size = FontSize,
                                        Weight=wx.BOLD, Style=wx.ITALIC)


            R.Text = label
            #print dir(label), label
            #R.Bind(FC.EVT_FC_LEFT_UP, self.OnLeftUp )

            R.Bind(FC.EVT_FC_LEFT_DOWN, self.ObjectHit)
            R.Bind(FC.EVT_FC_RIGHT_DOWN, self.RightClickCb )
            #self.Canvas.Bind(FC.EVT_FC_LEFT_DOWN, self.ObjectHit, id=R.ID)

            self.models[R]=id

            self.FloatCanvas.Draw()

        else:
            print "Nothing Selected"

    def createLine(self, R1, R2):
        #print "creating link", R1, R2
        x1,y1  = (R1.BoundingBox[0] + (R1.wh[0]/2, R1.wh[1]/2))
        x2,y2  = (R2.BoundingBox[0] + (R2.wh[0]/2, R2.wh[1]/2))
        #length = (((x2 - x1)**2)+(y2 - y1)**2)**.5
        #dy = abs(y2 - y1)
        #dx = abs(x2 - x1)
        #angle = math.atan2(dx,dy) *180/math.pi

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


        for i in range(0,len(line)-1):
            self.FloatCanvas.AddObject(FC.Line((line[i],line[i+1]),LineColor=linegradient[i],LineWidth=2,InForeground=False))

        #line = CanvasObjects.get_inverse(line, arrow_length=6)
        #self.FloatCanvas.AddObject(FC.Point(start,Color='green',Diameter=10,InForeground= True))
        #self.FloatCanvas.AddObject(FC.Point(end,Color='blue',Diameter=10,InForeground=True))

        # import random
        # r = lambda: random.randint(0,255)
        # for i in range(0,len(line)-1):
        #     color = '#%02X%02X%02X' % (r(),r(),r())
        #     self.FloatCanvas.AddObject(FC.Line((line[i],line[i+1]),LineColor=color,LineWidth=2,InForeground=False))


        #self.FloatCanvas.AddObject(FC.Polygon(arrow,FillColor='Blue',InForeground=True))

        self.FloatCanvas.AddPolygon(arrow,FillColor='blue',InForeground=True)
        # for pt in arrow:
        #     self.FloatCanvas.AddObject(FC.Point(pt, Color="Red", Diameter= 5, InForeground=True))

        #self.Canvas.AddArrow((x1,y1), length, angle ,LineWidth = 5, LineColor = "Black", ArrowHeadAngle = 50)#, end = 'ARROW_POSITION_MIDDLE')
        #Arrow1 = self.Canvas.Canvas.AddArrow((x1,y1), length/2, angle ,LineWidth = 2, LineColor = "Black", ArrowHeadSize = 10, ArrowHeadAngle = 50)#, end = 'ARROW_POSITION_MIDDLE')
        # xm = x1 + dx/2
        # ym = y1 + dy/2
        #Arrow2 = self.Canvas.Canvas.AddArrow((xm,ym), length/2, angle ,LineWidth = 2, LineColor = "Black", ArrowHeadSize = 10, ArrowHeadAngle = 50)#, end = 'ARROW_POSITION_MIDDLE')
        # Arrow1.HitlineWidth = 6
        # Arrow2.HitlineWidth = 6
        #
        # Arrow1.Bind(FC.EVT_FC_LEFT_DOWN, self.ArrowClicked)
        # Arrow2.Bind(FC.EVT_FC_LEFT_DOWN, self.ArrowClicked)
        # Arrow1.Bind(FC.EVT_FC_RIGHT_DOWN, self.RightClickCb)
        # Arrow2.Bind(FC.EVT_FC_RIGHT_DOWN, self.RightClickCb)

        # g = self.Canvas.Canvas._DrawList
        # g.insert(0, g.pop())
        # g.insert(0, g.pop())
        # self.Canvas.Canvas._DrawList = g

        self.Canvas.Canvas.Draw()


    def ObjectHit(self, object):
        print "Hit Object(CanvasController)", object.Name
        #self.FloatCanvas.Bind(FC.EVT_FC_RIGHT_DOWN( list, -1, self.RightClickCb ))
        cur = self.getCursor()

        print object.Name

        if cur.Name == 'link':
            if len(self.linkRects)  > 0:
                self.linkRects.append(object)
                self.createLine(self.linkRects[0], self.linkRects[1])

                # save links
                self.links.append([self.linkRects[0], self.linkRects[1]])

                # reset linkrects object
                self.linkRects=[]

                # change the mouse cursor

                #self.Canvas.SetMode(self.Modes[0][1])

            else:
                self.linkRects.append(object)

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
            params = obj.get_config_params()


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
            mv.setText(css + html)



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


    def OnLeftUp(self, event):
        if self.Moving:
            self.Moving = False
            if self.MoveObject is not None:
                dxy = event.GetPosition() - self.StartPoint
                (x,y) = self.FloatCanvas.ScalePixelToWorld(dxy)
                self.MovingObject.Move((x,y))
                self.MovingObject.Text.Move((x, y))

                # remove links
                #self.FloatCanvas._DrawList = [obj for obj in self.FloatCanvas._DrawList if type(obj) != FC.Arrow]
                self.FloatCanvas._DrawList = [obj for obj in self.FloatCanvas._DrawList if type(obj) != FC.Line]

                # recalculate links
                #rects = [obj for obj in self.FloatCanvas._DrawList if type(obj) != FC.Rectangle]

                for link in self.links:
                    self.createLine(link[0], link[1])

                # using links[[r1,r2],[...]] we can iterate of the rectangles and redraw links


            self.FloatCanvas.Draw(True)



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
        #self.Log("The Link was Clicked")
        print "The Link was clicked"
        dlg = LinkBox()
        dlg.ShowModal()
        dlg.Destroy()
        #Example()

    def RightClickCb( self, event ):
        # record what was clicked
        #self.list_item_clicked = right_click_context = event.GetText()

        ### 2. Launcher creates wxMenu. ###
        menu = wx.Menu()
        for (id,title) in menu_title_by_id.items():
            ### 3. Launcher packs menu with Append. ###
            menu.Append( id, title )
            ### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
            wx.EVT_MENU( menu, id, self.MenuSelectionCb )

        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.frame.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak
    #
    def MenuSelectionCb( self, event ):
        # do something
        operation = menu_title_by_id[ event.GetId() ]
        #target    = self.list_item_clicked
        print 'Perform "%(operation)s" on "%(target)s."' % vars()


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


        # make sure the correct file type was dragged
        name, ext = os.path.splitext(filenames[0])
        if ext == '.mdl' or ext =='.sim':

            models = None
            try:
                if ext == '.mdl':
                    # load the model (returns model instance
                    models = [self.cmd.add_model(filenames[0])]

                else:
                    # load the simulation
                    models, links = self.cmd.load_simulation(filenames[0])

                # draw boxes for each model
                offset = 0
                for model in list(models):
                    # get the name and id of the model
                    name = model.get_name()
                    modelid = model.get_id()

                    newx = random.randrange(-1,2)*offset + x
                    newy = random.randrange(-1,2)*offset + y

                    self.controller.createBox(name=name, id=modelid, xCoord=newx, yCoord=newy)
                    self.window.Canvas.Draw()
                    offset=200
            except Exception, e:
                print 'Could not load the model :(. Hopefully this exception helps...'
                print e

        else:
            print 'I do not recognize this file type :('


class GUILink():

    def __init__(self, Canvas=None):
        self.__init__(self, Canvas)
        self.Canvas = Canvas
        self.selected = []
        self.links = []

    def GetHitObject(self, event, HitEvent):
        if self.Canvas.HitDict:
            # check if there are any objects in the dict for this event
            if self.Canvas.HitDict[ HitEvent ]:
                xy = event.GetPosition()
                color = self.Canvas.GetHitTestColor( xy )
                if color in self.Canvas.HitDict[ HitEvent ]:
                    Object = self.Canvas.HitDict[ HitEvent ][color]
                    #self.Canvas._CallHitCallback(Object, xy, HitEvent)
                    return Object
            return False

## DONT CARE ABOUT THIS STUFF
class MovingObjectMixin:
    """
    Methods required for a Moving object

    """
    def GetOutlinePoints(self):
        """
        Returns a set of points with which to draw the outline when moving the
        object.

        Points are a NX2 array of (x,y) points in World coordinates.


        """
        BB = self.BoundingBox
        OutlinePoints = N.array(
            ( (BB[0, 0], BB[0, 1]), (BB[0, 0], BB[1, 1]), (BB[1, 0], BB[1, 1]), (BB[1, 0], BB[0, 1]),
            ))

        return OutlinePoints

class ConnectorObjectMixin:
    """
    Mixin class for DrawObjects that can be connected with lines

    Note that this version only works for Objects that have an "XY" attribute:
      that is, one that is derived from XHObjectMixin.

    """

    def GetConnectPoint(self):
        return self.XY

class MovingBitmap(FC.ScaledBitmap, MovingObjectMixin, ConnectorObjectMixin):
    """
    ScaledBitmap Object that can be moved
    """
    # # All we need to do is is inherit from:
    # #  ScaledBitmap, MovingObjectMixin and ConnectorObjectMixin
    pass


class MovingCircle(FC.Circle, MovingObjectMixin, ConnectorObjectMixin):
    """
    ScaledBitmap Object that can be moved
    """
    # # All we need to do is is inherit from:
    # #  Circle MovingObjectMixin and ConnectorObjectMixin
    pass


class MovingGroup(FC.Group, MovingObjectMixin, ConnectorObjectMixin):
    def GetConnectPoint(self):
        return self.BoundingBox.Center

    def CalcBoundingBox(self):
        self.BoundingBox = BBox.fromPoints((self.Object1.GetConnectPoint(), self.Object2.GetConnectPoint()))
        if self._Canvas:
            self._Canvas.BoundingBoxDirty = True


    def _Draw(self, dc, WorldToPixel, ScaleWorldToPixel, HTdc=None):
        Points = N.array((self.Object1.GetConnectPoint(), self.Object2.GetConnectPoint()))
        Points = WorldToPixel(Points)
        dc.SetPen(self.Pen)
        dc.DrawLines(Points)
        if HTdc and self.HitAble:
            HTdc.SetPen(self.HitPen)
            HTdc.DrawLines(Points)


class TriangleShape1(FC.Polygon, MovingObjectMixin):
    def __init__(self, XY, L):
        """
        An equilateral triangle object
        XY is the middle of the triangle
        L is the length of one side of the Triangle
        """

        XY = N.asarray(XY)
        XY.shape = (2,)

        Points = self.CompPoints(XY, L)

        FC.Polygon.__init__(self, Points, LineColor="Black", LineStyle="Solid", LineWidth=2, FillColor="Red",
                            FillStyle="Solid")

    # # Override the default OutlinePoints
    #def GetOutlinePoints(self):
        #return self.Points

    def CompPoints(self, XY, L):
        c = L / N.sqrt(3)

        Points = N.array(((0, c), ( L / 2.0, -c / 2.0), (-L / 2.0, -c / 2.0)), N.float_)

        Points += XY
        return Points

menu_titles = [ "Open",
                "Properties",
                "Rename",
                "Delete" ]

menu_title_by_id = {}
for title in menu_titles:
    menu_title_by_id[ wx.NewId() ] = title
