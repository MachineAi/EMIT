import wx
from gui.views.SimulationsPlotView import SimulationsPlotView
from matplotlib.collections import PolyCollection
from utilities import geometry


class SimulationsPlotCtrl(SimulationsPlotView):
    def __init__(self, parent, columns=None):
        SimulationsPlotView.__init__(self, parent)

        if columns:
            self.table.set_columns(columns)

        self.data = {}  # Dictionary to hold the data respective to the row ID
        self.geometries = {}  # Holds the geometries respective to the row ID
        self.start_date_object = wx.DateTime_Now() - 1 * wx.DateSpan_Day()  # Default date is yesterday
        self.end_date_object = wx.DateTime_Now()  # Default date is today

        self.start_date_picker.SetValue(self.start_date_object)
        self.end_date_picker.SetValue(self.end_date_object)

        # Adding room for the x axis labels to be visible
        self.temporal_plot.add_padding_to_plot(bottom=0.15)
        self.spatial_plot.add_padding_to_plot(bottom=0.15)

        # Highlighting variables
        self.start_highlight_x = None
        self.end_highlight_x = None
        self.__highlighted_region = None  # Set to None after redrawing to prevent errors

        # Bindings
        self.plot_button.Bind(wx.EVT_BUTTON, self.on_plot)
        self.table.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_row_selected)
        self.start_date_picker.Bind(wx.EVT_DATE_CHANGED, self.on_start_date_change)
        self.end_date_picker.Bind(wx.EVT_DATE_CHANGED, self.on_end_date_change)
        self.spatial_plot.plot.mpl_connect("button_press_event", self.on_mouse_pressed)
        self.spatial_plot.plot.mpl_connect("button_release_event", self.on_mouse_release)

    def get_selected_id(self):
        """
        :return: the ID type(Int) of the selected row or -1 if no row is selected
        """
        row = self.table.get_selected_row()
        if row:
            return int(row[0])
        return -1

    def _plot_point(self, string_points, color):
        """
        To prevent errors, this method should only be called by plot_spatial()
        :param string_points:
        :param color: Hexadecimal example: #FFFFFF
        :return:
        """
        points = string_points.split(" ")
        x_value = float(points[0].strip("(").strip(")"))
        y_value = float(points[1].strip("(").strip(")"))

        self.spatial_plot.axes.scatter(x_value, y_value, color=color)

    def _plot_polygon(self, string_points, color):
        """
        To prevent errors, this method should only be called by plot_spatial()
        :param string_points:
        :param color: Hexadecimal example: #FFFFFF
        :return:
        """
        data = []
        for index in string_points[1:-1].split(","):  # Parse the string into tuples with float values
            value = index.strip("(").strip(")")
            space_position = value.find(" ")
            x_value = float(value[:space_position])
            y_value = float(value[space_position + 1:])
            data.append((x_value, y_value))
        p_coll = PolyCollection([data], closed=True, facecolors=color, alpha=0.5, edgecolors=None, linewidths=(2,))
        self.spatial_plot.axes.add_collection(p_coll, autolim=True)

    def plot_spatial(self, ID, title):
        """
        Plots the spatial of the selected row
        :param ID: type(Int). Must match a row the selected row's ID
        :return:
        """
        self.spatial_plot.clear_plot()
        color = "#0DACFF"
        # geometries = self.geometries[ID][0]  # Returns a string
        # geometry_object = geometry.fromWKT(geometries)  # Convert the string to a wkt object
        # if "POLYGON" in geometries:
        #     self._plot_polygon(geometry_object, color)
        # elif "POINT" in geometries:
        #     self._plot_point(geometry_object, color)
        # else:
        #     raise Exception("plot_spatial() failed. Geometries must be POLYGON OR POINT")

        geometries = self.geometries[ID][0]
        geometries = geometry.fromWKT(geometries)
        self.spatial_plot.plot_geometry(geometries, color, title)



        self.spatial_plot.rotate_x_axis_label()
        self.spatial_plot.set_title(str(title))
        self.spatial_plot.axes.set_ylabel("Some Y label")
        self.spatial_plot.axes.set_xlabel("Some X label")
        self.spatial_plot.axes.grid(True)
        self.spatial_plot.axes.margins(0.1)
        self.spatial_plot.redraw()

    ##########################
    # EVENTS
    ##########################

    def on_end_date_change(self, event):
        """
        Prevents the end date from being set to before the start date and
        prevent the end date from being set to a day after today
        :param event:
        :return:
        """
        if self.start_date_picker.GetValue() > self.end_date_picker.GetValue():  # Prevent start date to overlap end
            self.end_date_picker.SetValue(self.end_date_object)
        elif self.end_date_picker.GetValue() > wx.DateTime_Now():
            self.end_date_picker.SetValue(self.end_date_object)  # Prevent end date to be set to after today
        else:
            self.end_date_object = self.end_date_picker.GetValue()

    def on_mouse_release(self, event):
        """
        Highlights a region
        :param event: MouseEvent. See Matplotlib event handling for more information
        :return:
        """
        if event.button == 1:  # Accept only mouse left clicks
            self.end_highlight_x = event.xdata

            # Highlight. # Returns a Polygon instance
            self.__highlighted_region = self.spatial_plot.axes.axvspan(xmin=self.start_highlight_x,
                                                                       xmax=self.end_highlight_x,
                                                                       color="red", alpha=0.5)
            self.spatial_plot.redraw()

    def on_mouse_pressed(self, event):
        """
        Set self.__highlighted_region to None after redrawing to prevent errors
        Sets the start position for highlighting
        :param event: MouseEvent. See Matplotlib event handling for more information
        :return:
        """
        if event.button == 1:  # Accept only mouse left releases
            self.start_highlight_x = event.xdata
            if self.__highlighted_region:
                self.__highlighted_region.remove()  # Remove previous highlighted region

    def on_row_selected(self, event):
        """
        Set the date pickers to match the start and end date of the row selected dates
        :param event:
        :return:
        """
        self.__highlighted_region = None
        date = wx.DateTime()
        start_date_string = self.table.get_selected_row()[3]
        if date.ParseFormat(start_date_string, "%Y-%m-%d %H:%M:%S") == -1:
            raise Exception("start_date_string is not in the right format")
        self.start_date_picker.SetValue(date)
        self.start_date_object = date

        end_date_string = self.table.get_selected_row()[4]
        if str(end_date_string) == "None":
            self.end_date_picker.SetValue(wx.DateTime_Now())
        elif date.ParseFormat(end_date_string, "%Y-%m-%d %H:%M:%S") == -1:
            raise Exception("end_date_string is not in the right format")
        else:
            self.end_date_picker.SetValue(date)
            self.end_date_object = date

        #  Plot Spatial
        self.plot_spatial(self.get_selected_id(), self.table.get_selected_row()[1])

    def on_plot(self, event):
        """
        Grabs the data related to the selected row. self.data must be set otherwise it will not plot
        :param event:
        :return: True if plot was successful, False if plot failed
        """
        ID = self.get_selected_id()

        if ID == -1:
            return False  # No selected row

        if not len(self.data) or ID not in self.data:
            return False  # self.data has not been set or set incorrectly

        date_time_objects, value = self.data[ID]

        data = []
        for i in range(len(date_time_objects)):
            data.append((date_time_objects[i], value[i]))

        name = self.table.get_selected_row()[1]
        units = self.table.get_selected_row()[2]
        self.temporal_plot.clear_plot()
        self.temporal_plot.rotate_x_axis_label()
        self.temporal_plot.plot_dates(data, name, None, units)

        return True

    def on_start_date_change(self, event):
        """
        Prevents the start date from being set to after the end date
        :param event:
        :return:
        """
        if self.start_date_picker.GetValue() > self.end_date_picker.GetValue():
            self.start_date_picker.SetValue(self.start_date_object)
        else:
            self.start_date_object = self.start_date_picker.GetValue()
