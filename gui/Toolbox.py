__author__ = 'Mario'
import wx
import wx.gizmos as gizmos
from images import icons
from ContextMenu import TreeContextMenu
import ConfigParser
import os
from os.path import *
import fnmatch


class ToolboxPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1, style =
                                        wx.TR_DEFAULT_STYLE
                                        #| wx.TR_HAS_BUTTONS
                                        #| wx.TR_TWIST_BUTTONS
                                        #| wx.TR_ROW_LINES
                                        #| wx.TR_COLUMN_LINES
                                        #| wx.TR_NO_LINES
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                   )

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        mdlidx    = il.Add(icons.Earth_icon.GetBitmap())

        self.tree.SetImageList(il)
        self.il = il

        ini = join(dirname(abspath(__file__)), 'Resources/ToolboxPaths')
        config_params = {}
        cparser = ConfigParser.ConfigParser(None, multidict)
        cparser.read(ini)
        sections = cparser.sections()
        modelpaths = {}

        self.items = {}

        for s in sections:
            # get the section key (minus the random number)
            section = s.split('^')[0]

            # get the section options
            options = cparser.options(s)

            # save ini options as dictionary
            d = {}
            for option in options:
                d[option] = cparser.get(s,option)

            if section not in modelpaths:
                modelpaths[section] = [d]
            else:
                modelpaths[section].append(d)

        self.tree.AddColumn("File Categories")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 175)
        self.root = self.tree.AddRoot("Models")
        self.tree.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)
        self.tree.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Normal)

        for category, data in modelpaths.iteritems():
            txt =  category
            cat = self.tree.AppendItem(self.root, txt)
            self.tree.SetItemImage(cat, fldropenidx, which = wx.TreeItemIcon_Expanded)
            self.tree.SetItemImage(cat, fldropenidx, which = wx.TreeItemIcon_Normal)
            for d in data:
                path = d['path']
                apath = join(dirname(abspath(__file__)), path)
                matches = []
                for root, dirnames, filenames in os.walk(apath):
                    for filename in fnmatch.filter(filenames, '*.mdl'):
                        matches.append(os.path.join(root, filename))
                        fullpath = join(root, filename)

                        txt =  filename.split('.mdl')[0]
                        child = self.tree.AppendItem(cat, txt)

                        self.items[child] = fullpath

                        child.__setattr__('path',fullpath)
                        self.tree.SetItemImage(child, mdlidx, which = wx.TreeItemIcon_Expanded)
                        self.tree.SetItemImage(child, mdlidx, which = wx.TreeItemIcon_Normal)


        self.tree.Expand(self.root)

        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnContextMenu)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onDrag)
        # self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)

    def OnContextMenu(self, evt):
        self.tree.PopupMenu(TreeContextMenu(self,evt), evt.GetPosition())

    def OnActivate(self, evt):

        # item = self.tree.GetItemText(evt.GetItem())
        item = self.tree.GetSelection()

        for i in self.items.keys():
            if i == item:
                print self.items[i]
                break
        pass

    def onDrag(self, event):
        data = wx.FileDataObject()
        obj = event.GetEventObject()
        id = event.GetIndex()
        filename = obj.GetItem(id).GetText()
        dirname = self.tree.GetName
        #dirname = os.path.dirname(os.path.abspath(os.listdir(".")[0]))
        fullpath = str(os.path.join(dirname, filename))

        data.AddFile(fullpath)

        dropSource = wx.DropSource(obj)
        dropSource.SetData(data)
        result = dropSource.DoDragDrop()

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        # if item:
        #     self.log.write('Flags: %s, Col:%s, Text: %s' %
        #                    (flags, col, self.tree.GetItemText(item, col)))

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())


def runTest(frame, nb):
    win = ToolboxPanel(nb)
    return win

#----------------------------------------------------------------------



overview = """<html><body>
<h2><center>TreeListCtrl</center></h2>

The TreeListCtrl is essentially a wx.TreeCtrl with extra columns,
such that the look is similar to a wx.ListCtrl.

</body></html>
"""


if __name__ == '__main__':
    #raw_input("Press enter...")
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])

class multidict(dict):
    _unique = 0

    def __setitem__(self, key, val):
        if isinstance(val, dict):
            self._unique += 1
            key += '^'+str(self._unique)
        dict.__setitem__(self, key, val)