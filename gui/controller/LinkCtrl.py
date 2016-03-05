import collections
import uuid

import wx
import wx.grid as gridlib
import wx.lib.newevent as ne

import coordinator.engineAccessors as engine
from coordinator.emitLogging import elog
from gui.controller.SpatialPlotCtrl import SpatialPlotCtrl
from gui.views.LinkView import LinkView
from utilities import geometry

LinkUpdatedEvent, EVT_LINKUPDATED = ne.NewEvent()


class LinkCtrl(LinkView):

    odesc = ""
    idesc = ""

    def __init__(self, parent, outputs, inputs, swap=False):
        LinkView.__init__(self, parent, outputs, inputs)

        # self.l = None
        self.swap = swap

        # save parent (used in onplot)
        self.parent = parent

        # class link variables used to save link
        self.__selected_link = None

        self.__link_source_id = self.output_component['id']
        self.__link_target_id = self.input_component['id']
        self.__links = collections.OrderedDict()
        self.link_obj_hit = False

        self.OnStartUp(self.output_component, self.input_component)

        self.InitBindings()

        self.__checkbox_states = [None, None]

        #  holds the links that will be deleted when deleting->save and close
        self.links_to_delete = []


    def InitBindings(self):
        self.LinkNameListBox.Bind(wx.EVT_LISTBOX, self.OnChange)
        self.LinkNameListBox.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        self.ButtonNew.Bind(wx.EVT_BUTTON, self.OnSave)
        self.ButtonNew.Bind(wx.EVT_BUTTON, self.onNewButton)
        self.ButtonDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.ButtonSwap.Bind(wx.EVT_BUTTON, self.OnSwap)
        self.ButtonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.ButtonSave.Bind(wx.EVT_BUTTON, self.OnSave)
        self.ButtonPlot.Bind(wx.EVT_BUTTON, self.on_plot_geometries)
        self.Bind(EVT_LINKUPDATED, self.linkSelected)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.outputGrid.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OutputGridHover)
        self.inputGrid.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.InputGridHover)

        self.OutputComboBox.Bind(wx.EVT_COMBOBOX, self.on_select_output)
        self.InputComboBox.Bind(wx.EVT_COMBOBOX, self.on_select_input)
        self.ComboBoxTemporal.Bind(wx.EVT_COMBOBOX, self.on_select_temporal)
        self.ComboBoxSpatial.Bind(wx.EVT_COMBOBOX, self.on_select_spatial)

    def activateSwap(self):
        if self.swap == True:
            self.ButtonSwap.Enable()
        else:
            self.ButtonSwap.Disable()

    def activateControls(self, activate=True):

        # todo: this needs to be expanded to check if any forms have been changed

        if activate:
            self.ButtonSave.Enable()
            self.ComboBoxSpatial.Enable()
            self.ComboBoxTemporal.Enable()
            self.InputComboBox.Enable()
            self.OutputComboBox.Enable()
            self.ButtonPlot.Enable()
            self.activateSwap()
        else:
            self.ButtonSave.Disable()
            self.ComboBoxSpatial.Disable()
            self.ComboBoxTemporal.Disable()
            self.InputComboBox.Disable()
            self.OutputComboBox.Disable()
            self.ButtonPlot.Disable()
            self.ButtonSwap.Disable()

    def getInputModelText(self):
        if self.input_component['id'] == self.__selected_link.target_id:
            return self.input_component['name']
        else:
            return self.output_component['name']

    def getLinkByName(self, name):
        for l in self.__links.values():
            if l.name() == name:
                return l
        return None

    def GetModelFrom(self):
        if 'name' in self.output_component:
            return self.output_component['name']
        else:
            return None

    def GetModelTo(self):
        if 'name' in self.input_component:
            return self.input_component['name']
        else:
            return None

    def getOutputModelText(self):
        if self.output_component['id'] == self.__selected_link.source_id:
            return self.output_component['name']
        else:
            return self.input_component['name']

    def getSelectedLinkId(self):
        selection = self.LinkNameListBox.GetStringSelection()
        link_id = selection.split('|')[0].strip()
        return link_id

    def InputGridHover(self, e):
        self.InGridToolTip(e)

    def InGridToolTip(self, e):
        if e.GetRow() == 2 and e.GetCol() == 1:
            self.inputGrid.SetToolTip(wx.ToolTip(self.idesc))
        else:
            self.inputGrid.SetToolTip(wx.ToolTip(""))
        e.Skip()

    def linkSelected(self, event):

        # get the selected link object
        selected = self.LinkNameListBox.GetStringSelection()
        selected_id = selected.split('|')[0].strip()

        # make sure a link is selected
        if selected_id in self.__links.keys():

            # get the selected link object
            self.__selected_link = self.__links[selected_id]

            # activate controls
            self.activateControls(True)

            # populate the link metadata
            self.populate_output_metadata(self.__selected_link)
            self.populate_input_metadata(self.__selected_link)

            #  Setting the labels that indicate which metadata is input and output
            self.inputLabel.SetLabel("Input of: " + str(self.getInputModelText()))
            self.outputLabel.SetLabel("Output of: " + str(self.getOutputModelText()))

        else:
            # deactivate controls if nothing is selected
            self.activateControls(False)

    def OnCancel(self, event):

        if self.LinkNameListBox.Count > 0:
            dial = wx.MessageDialog(self, 'Are you sure that you want to close without saving?', 'Question',
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dial.ShowModal() == wx.ID_YES:
                self.Destroy()
        else:
            self.Destroy()

    def OnChange(self, event):
        link_name = self.LinkNameListBox.GetStringSelection()

        # get the selected link
        l = self.getLinkByName(link_name)

        # set the currently selected link
        self.__selected_link = l

        # update the combobox selections
        self.OutputComboBox.SetStringSelection(l.oei)
        self.InputComboBox.SetStringSelection(l.iei)

        if l.temporal_interpolation is not None:
            self.ComboBoxTemporal.SetStringSelection(l.temporal_interpolation)
        else:
            # set default value
            self.ComboBoxTemporal.SetSelection(0)

        if l.spatial_interpolation is not None:
            self.ComboBoxSpatial.SetStringSelection(l.spatial_interpolation)
        else:
            # set default value
            self.ComboBoxSpatial.SetSelection(0)

        # set the state of link_obj_hit
        self.link_obj_hit = True

        wx.PostEvent(self, LinkUpdatedEvent())

    def OnDelete(self, event):
        #  Links are placed in a queue that will be deleted permanently when clicking on save and close.

        if self.LinkNameListBox.GetSelection() < 0:
            elog.info("Please select a link to delete")
            return

        # get the link id
        linkid = self.getSelectedLinkId()

        self.links_to_delete.append(linkid)

        index = self.LinkNameListBox.GetSelection()
        self.LinkNameListBox.Delete(index)

    def OnLeftUp(self, event):

        if not self.link_obj_hit:
            link_name = self.__selected_link.name()

            selected_index = self.LinkNameListBox.Items.index(link_name)
            self.LinkNameListBox.SetSelection(selected_index)

        # reset the state of link_obj_hit
        self.link_obj_hit = False

    def onNewButton(self, event):

        # set the exchange item values to ---
        self.InputComboBox.SetSelection(0)
        self.OutputComboBox.SetSelection(0)

        # generate a unique name for this link
        oei = self.OutputComboBox.GetValue()
        iei = self.InputComboBox.GetValue()

        # create a link object and save it at the class level
        l = LinkInfo(oei, iei, self.__link_source_id, self.__link_target_id)
        self.__links[l.uid] = l

        # add the link name to the links list box
        self.refreshLinkNameBox()

        # set the currently selected link
        self.__selected_link = l

        # select the last value
        self.LinkNameListBox.SetSelection(self.LinkNameListBox.GetCount() - 1)

        self.OnChange(None)

        self.outputLabel.SetLabel("Output of " + self.GetModelFrom())
        self.inputLabel.SetLabel("Input of " + self.GetModelTo())

    def on_plot_geometries(self, event):
        from gui.controller.SpatialCtrl import SpatialCtrl

        frame = wx.Frame(self.parent, size=(625, 625), style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE)
        controller = SpatialCtrl(frame)

        # input exchange item -> iei
        iei = controller.get_input_exchange_item_by_id(self.__selected_link.target_id)
        igeom = controller.get_geometries(iei)

        # output exchange item -> oei
        oei = controller.get_output_exchange_item_by_id(self.__selected_link.source_id)
        ogeom = controller.get_geometries(oei)

        controller.set_data(target=igeom, source=ogeom)
        # controller.set_selection_data(target_name=self.__selected_link.iei, source_name=self.__selected_link.oei)
        if iei:
            controller.set_selection_data(target_name=iei[0]['name'])
        if oei:
            controller.set_selection_data(source_name=oei[0]['name'])
        controller.update_plot(self.__selected_link.oei)
        controller.update_plot(self.__selected_link.iei)
        controller.input_checkbox.SetValue(True)
        controller.output_checkbox.SetValue(True)

        title = self.getOutputModelText() + " --> " + self.getInputModelText()
        frame.SetTitle(title)

        if controller.output_exchange_item:
            controller.edit_grid("output", 1, 1, controller.source_name)
            controller.edit_grid("output", 2, 1, controller.output_exchange_item[0].GetGeometryName())
            controller.edit_grid("output", 3, 1, controller.output_exchange_item[0].GetCoordinateDimension())
            controller.edit_grid("output", 5, 1, controller.output_exchange_item[0].GetPointCount())

        if controller.input_exchange_item:
            controller.edit_grid("input", 1, 1, controller.target_name)
            controller.edit_grid("input", 2, 1, controller.input_exchange_item[0].GetGeometryName())
            controller.edit_grid("input", 3, 1, controller.input_exchange_item[0].GetCoordinateDimension())
            controller.edit_grid("input", 5, 1, controller.input_exchange_item[0].GetPointCount())

        frame.Show()


        # # title = self.getOutputModelText() + " --> " + self.getInputModelText()
        # plot_window = wx.Frame(self.parent, id=wx.ID_ANY, title=title, size=(625, 625),
        #                        style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        #
        # from osgeo import ogr
        # # create a spatial plot instance
        # plot_panel = SpatialPlotCtrl(plot_window)
        #
        # # get the source and target ids from the link object
        # source_model_id = self.__selected_link.source_id
        # target_model_id = self.__selected_link.target_id
        #
        # # get the output geometries
        # oei = engine.getOutputExchangeItems(source_model_id)
        # ogeoms = {}
        # for o in oei:
        #     name = o['name']
        #     geoms = [geometry.fromWKB(g['wkb']) for g in o['geom']]
        #     # geoms = [ogr.CreateGeometryFromWkb(g['wkb']) for g in o['geom']]
        #     ogeoms[name] = geoms
        #
        # # get the input geometries
        # igeoms = {}
        # iei = engine.getInputExchangeItems(target_model_id)
        # for i in iei:
        #     name = i['name']
        #     geoms = [geometry.fromWKB(g['wkb']) for g in i['geom']]
        #     # geoms = [ogr.CreateGeometryFromWkb(g['wkb']) for g in i['geom']]
        #     igeoms[name] = geoms
        #
        # # set input and output geometries
        # plot_panel.set_input_data(value=igeoms)
        # plot_panel.set_output_data(value=ogeoms)
        #
        # # add some selection
        # textLabel = wx.StaticText(plot_window, wx.ID_ANY, label='Toggle the Input and Output exchange element sets: ')
        # textLabel.SetFont( wx.Font( 14, 70, 90, 92, False, wx.EmptyString ) )
        # inputSelection = wx.CheckBox(plot_window, 998,label='Input Exchange Item: '+self.__selected_link.iei)
        # outputSelection = wx.CheckBox(plot_window, 999,label='Output Exchange Item: '+self.__selected_link.oei)
        # self.__checkbox_states = [self.__selected_link.iei, self.__selected_link.oei]  # initialize checkbox state
        #
        # def checked(event):
        #     chk = event.Checked()
        #
        #     # make changes if selection is false
        #     if event.Id == 998:
        #         if chk: self.__checkbox_states[0] = self.__selected_link.iei
        #         else:   self.__checkbox_states[0] = None
        #     if event.Id == 999:
        #         if chk: self.__checkbox_states[1] = self.__selected_link.oei
        #         else:   self.__checkbox_states[1] = None
        #
        #     # set the selected datasets in the controller
        #     plot_panel.set_selection_input(self.__checkbox_states[0])
        #     plot_panel.set_selection_output(self.__checkbox_states[1])
        #
        #     # update the plot
        #     plot_panel.updatePlot()
        #
        # # add some handlers
        # inputSelection.Bind(wx.EVT_CHECKBOX, checked)
        # outputSelection.Bind(wx.EVT_CHECKBOX, checked)
        #
        # # set the initial state of the input and output selectors
        # inputSelection.SetValue(True)
        # outputSelection.SetValue(True)
        #
        # plot_panel.set_selection_input(self.__selected_link.iei)
        # plot_panel.set_selection_output(self.__selected_link.oei)
        # plot_panel.updatePlot()  # update the plot to reflect the input/output selection
        #
        # # add controls to frame
        # mainSizer = wx.BoxSizer(wx.VERTICAL)
        # plotSizer = wx.BoxSizer(wx.VERTICAL)
        # SelectionSizer= wx.BoxSizer(wx.VERTICAL)
        #
        # # nest sizers to pad both the top and left borders
        # b = wx.BoxSizer(wx.VERTICAL)
        # b.Add(textLabel, flag=wx.LEFT, border=20 )
        # SelectionSizer.AddSizer(b, flag=wx.BOTTOM, border=10)
        # SelectionSizer.Add(inputSelection, flag=wx.LEFT, border=20)
        # SelectionSizer.Add(outputSelection, flag=wx.LEFT, border=20)
        # plotSizer.Add(plot_panel)
        #
        # # add elements back to mainSizer
        # mainSizer.Add(plotSizer)
        # mainSizer.Add(SelectionSizer)
        # plot_window.SetSizer(mainSizer)
        #
        # plot_window.Layout()
        # plot_window.Show()

    def on_select_output(self, event):
        """
        sets the metadata for the selected output exchange item and populates a tree view
        """

        # get selected value
        output_name = self.OutputComboBox.GetValue()

        # get the current link
        l = self.__selected_link

        # change the link name to reflect output -> input
        l.oei = output_name
        l.refresh('output')

        # update the name in the links list
        self.__links[l.uid] = l

        # refresh the link name box
        self.refreshLinkNameBox()

        # populate metadata
        self.populate_output_metadata(l)

    def on_select_input(self, event):
        """
        sets the metadata for the selected input exchange item and populates a tree view
        """

        # get selected value
        input_name = self.InputComboBox.GetValue()

        # get the current link
        l = self.__selected_link

        # change the link name to reflect output -> input
        l.iei = input_name
        l.refresh('input')

        # update the name in the links list
        self.__links[l.uid] = l

        # refresh the link name box
        self.refreshLinkNameBox()

        # populate metadata
        self.populate_input_metadata(l)

    def on_select_spatial(self, event):
        # get the current link---
        l = self.__selected_link

        spatial_value = self.ComboBoxSpatial.GetValue()
        if spatial_value == 'None Specified':
            l.spatial_interpolation = None
        else:
            l.spatial_interpolation = self.spatial_transformations[spatial_value]

    def on_select_temporal(self, event):
        # get the current link
        l = self.__selected_link

        temporal_value = self.ComboBoxTemporal.GetValue()
        if temporal_value == 'None Specified':
            l.temporal_interpolation = None
        else:
            l.temporal_interpolation = self.temporal_transformations[temporal_value]

    def OnStartUp(self, component1, component2):
        self.InputComboBox.SetItems(['---'] + self.InputComboBoxChoices())
        self.OutputComboBox.SetItems(['---'] + self.OutputComboBoxChoices())

        links = []
        x = engine.getLinksBtwnModels(component1['id'], component2['id'])
        y = engine.getLinksBtwnModels(component2['id'], component1['id'])
        if x:
            for l in x:
                links.append(l)
        if y:
            for l in y:
                links.append(l)

        if links:
            for l in links:
                link = LinkInfo(l['source_item'],
                                l['target_item'],
                                l['source_id'],
                                l['target_id'],
                                l['id'],
                                l['spatial_interpolation'],
                                l['temporal_interpolation'])

                self.__links[l['id']] = link

            # select the first value
            self.refreshLinkNameBox()
            self.LinkNameListBox.SetSelection(0)
            self.__selected_link = self.__links.keys()[0]
            self.OnChange(None)
        else:
            # if no links are found, need to deactivate controls
            self.activateControls(False)

        # initial selection for the comboboxes.  This will change (below) if links exist
        self.InputComboBox.SetSelection(0)
        self.OutputComboBox.SetSelection(0)

        # # set the selection to the first link
        # selected = self.LinkNameListBox.GetStringSelection()
        # selected_id = selected.split('|')[0].strip()
        # if selected != '':
        #     l = self.__links[selected_id]
        #     self.OutputComboBox.SetSelection(self.OutputComboBoxChoices().index(l.oei) + 1)
        #     self.InputComboBox.SetSelection(self.InputComboBoxChoices().index(l.iei) + 1)

    def OnSwap(self, event):
        try:
            selected = self.getSelectedLinkId()
            engine.removeLinkById(selected)
            self.__links.pop(selected)

        except Exception as e:
            elog.debug(e)
            elog.warning("Please select which link to swap")
            return

        #  Swapping components of models
        temp = self.output_component
        self.output_component = self.input_component
        self.input_component = temp

        self.__link_source_id = self.output_component['id']
        self.__link_target_id = self.input_component['id']

        self.InputComboBox.SetItems(['---'] + self.InputComboBoxChoices())
        self.OutputComboBox.SetItems(['---'] + self.OutputComboBoxChoices())
        self.InputComboBox.SetSelection(0)
        self.OutputComboBox.SetSelection(0)


        self.onNewButton(1)

    def OnSave(self, event):
        """
        Saves all link objects to the engine and then closes the link creation window
        """

        # Deleting the links that are in the delete queue
        for link_id in self.links_to_delete:
            engine.removeLinkById(link_id)
            if link_id in self.__links:
                self.__links.pop(link_id)

        warnings = []
        errors = []
        for l in self.__links.values():

            if l.iei == '---' or l.oei == '--':
                warnings.append(l)
            else:

                try:
                    kwargs = dict(source_id=l.source_id,
                                  source_item=l.oei,
                                  target_id=l.target_id,
                                  target_item=l.iei,
                                  spatial_interpolation=l.spatial_interpolation,
                                  temporal_interpolation=l.temporal_interpolation,
                                  uid=l.uid)

                    # remove the existing link, if there is one
                    engine.removeLinkById(l.uid)

                    # add a new link inside the engine
                    link_id = engine.addLink(**kwargs)

                    if link_id:
                        l.saved = True

                    wx.PostEvent(self, LinkUpdatedEvent())
                except:
                    elog.error('ERROR|Could not save link: %s' % l.name)
                    errors.append(l)

        if len(warnings) > 0:
            warning_links = '\n'.join(l.name() for l in warnings)
            warning = wx.MessageDialog(self,
                                       "Could not save the following links because they lacking either input or output items: \n\n " + warning_links + "\n\n Would you like to discard these partial link objects?",
                                       'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)

            if warning.ShowModal() == wx.ID_YES:
                self.Destroy()
            else:
                return

        self.Destroy()

    def OutGridToolTip(self, e):
        if e.GetRow() == 2 and e.GetCol() == 1:
            self.outputGrid.SetToolTip(wx.ToolTip(self.odesc))
        else:
            self.outputGrid.SetToolTip(wx.ToolTip(""))
        e.Skip()

    def OutputGridHover(self, e):
        self.OutGridToolTip(e)

    def populate_output_metadata(self, l):

        # get the link object
        outputs = l.output_metadata
        if l.oei in outputs:
            o = outputs[l.oei]

            self.outputGrid.SetCellValue(1, 1, o['variable'].VariableNameCV())
            self.outputGrid.SetCellValue(2, 1, o['variable'].VariableDefinition())
            self.odesc = o['variable'].VariableDefinition()

            self.outputGrid.SetCellValue(4, 1, o['unit'].UnitName())
            self.outputGrid.SetCellValue(5, 1, o['unit'].UnitTypeCV())
            self.outputGrid.SetCellValue(6, 1, o['unit'].UnitAbbreviation())
        else:
            self.outputGrid.SetCellValue(1, 1, "")
            self.outputGrid.SetCellValue(2, 1, "")
            self.odesc = ""

            self.outputGrid.SetCellValue(4, 1, "")
            self.outputGrid.SetCellValue(5, 1, "")
            self.outputGrid.SetCellValue(6, 1, "")


    def populate_input_metadata(self, l):

        # get the link object
        inputs = l.input_metadata
        if l.iei in inputs:
            i = inputs[l.iei]

            self.inputGrid.SetCellValue(1, 1, i['variable'].VariableNameCV())
            self.inputGrid.SetCellValue(2, 1, i['variable'].VariableDefinition())
            self.idesc = i['variable'].VariableDefinition()

            self.inputGrid.SetCellValue(4, 1, i['unit'].UnitName())
            self.inputGrid.SetCellValue(5, 1, i['unit'].UnitTypeCV())
            self.inputGrid.SetCellValue(6, 1, i['unit'].UnitAbbreviation())
        else:
            self.inputGrid.SetCellValue(1, 1, "")
            self.inputGrid.SetCellValue(2, 1, "")
            self.idesc = ""

            self.inputGrid.SetCellValue(4, 1, "")
            self.inputGrid.SetCellValue(5, 1, "")
            self.inputGrid.SetCellValue(6, 1, "")

    def refreshLinkNameBox(self):

        self.LinkNameListBox.Clear()
        for l in self.__links.values():
            self.LinkNameListBox.Append(l.name())


class LinkInfo:
    def __init__(self, oei, iei, source_id, target_id, uid=None, spatial_interpolation=None,
                 temporal_interpolation=None):


        self.uid = 'L' + uuid.uuid4().hex if uid is None else uid
        # self.name = self.generate_link_name(oei,iei,self.uid)
        self.oei = oei
        self.iei = iei
        self.source_id = source_id
        self.target_id = target_id
        self.spatial_interpolation = spatial_interpolation
        self.temporal_interpolation = temporal_interpolation

        self.saved = False

        self.output_metadata = {}
        self.input_metadata = {}

        self.get_input_and_output_metadata()

    def refresh(self, type):

        self.get_input_and_output_metadata(type)


    def name(self):
        iei_name = self.iei if self.iei != '---' else '?'
        oei_name = self.oei if self.oei != '---' else '?'

        if iei_name == '?' and oei_name == '?':
            return '%s' % self.uid
        else:
            return '%s | %s -> %s ' % (self.uid, oei_name, iei_name)

    def get_input_and_output_metadata(self, type=None):

        if type == 'output' or type is None:
            # get output information
            outputs = engine.getOutputExchangeItems(self.source_id, returnGeoms=False)
            if outputs is not None:
                for output in outputs:
                    self.output_metadata[output['name']] = output
        if type == 'input' or type is None:
            # get input information
            inputs = engine.getInputExchangeItems(self.target_id, returnGeoms=False)
            if inputs is not None:
                for input in inputs:
                    self.input_metadata[input['name']] = input
