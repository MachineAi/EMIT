from gui.views.TimeSeriesView import TimeSeriesView
from webservice import wateroneflow
import wx
import os
import json
import coordinator.engineAccessors as engineAccessors
from gui.controller.WofSitesCtrl import WofSitesCtrl
from odm2api.ODMconnection import dbconnection as dbconnection2
from gui.controller.AddConnectionCtrl import AddConnectionCtrl
import db.dbapi_v2 as db2
from utilities import db as dbUtilities


class TimeSeriesCtrl(TimeSeriesView):
    def __init__(self, parent):
        TimeSeriesView.__init__(self, parent)
        self.api = None

        self.databases = {}

        table_columns = ["ResultID", "FeatureCode", "Variable", "Unit", "Type", "Organization", "Date Created"]
        self.set_columns(table_columns)

        # Add the wof sites to the connection combo option
        self.wof_names = self.get_wof_connection_names()
        for key, value in self.wof_names.iteritems():
            self.append_to_connection_combo(key)

        self.alternate_row_color()
        self.connection_combo.Bind(wx.EVT_CHOICE, self.on_connection_combo)
        self.add_connection_button.Bind(wx.EVT_BUTTON, self.on_add_connection)
        self.refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh_table)
        self.Bind(wx.EVT_MENU, self.on_view_menu, self.view_menu)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_right_click)
        self.table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click)

    def convert_selected_row_into_object(self):
        item = self.get_selected_row()
        data = {
            "site_name": item[0],
            "network": item[1],
            "county": item[3],
            "state": item[4],
            "site_type": item[5],
            "site_code": item[2]
        }
        record_object = type("WOFRecord", (object,), data)
        return record_object

    def get_selected_database(self):
        """
        Returns an empty string when a wof site or --- is selected
        :return:
        """
        db = {}
        for key, value in engineAccessors.getDbConnections().iteritems():
            if self.connection_combo.GetStringSelection() == value["name"]:
                db = value
                break
        return db

    @staticmethod
    def get_wof_connection_names():
        currentdir = os.path.dirname(os.path.abspath(__file__))
        wof_json = os.path.abspath(os.path.join(currentdir, '../../data/wofsites.json'))
        with open(wof_json, "r") as f:
            try:
                data = json.load(f)
            except ValueError:
                print "Failed to parse WOF json"
                data = {}
        return data

    def load_connection_combo(self):
        connections = engineAccessors.getDbConnections()
        for key, value in connections.iteritems():
            self.append_to_connection_combo(connections[key]["name"])

    def load_SQL_database(self):
        table_columns = ["ResultID", "FeatureCode", "Variable", "Unit", "Type", "Organization", "Date Created"]
        self.set_columns(table_columns)
        db = self.get_selected_database()

        if db["args"]["engine"] == "sqlite":
            session_factory = dbconnection2.createConnection(engine=db["args"]["engine"], address=db["args"]["address"])
            session = db2.connect(session_factory)
            series = session.getAllSeries()
        elif db["args"]["engine"] == "postgresql":  # db is postresql
            session_factory = dbUtilities.build_session_from_connection_string(db["connection_string"])
            session = db2.connect(session_factory)
            series = session.getAllSeries()
        else:
            # Fails if db is not sqlite or postresql
            raise Exception("Failed to load database")

        if not series:
            self.empty_list_message.Show()
            return

        self.empty_list_message.Hide()
        data = self.series_to_table_data(series)

        self.set_table_content(data)

    @staticmethod
    def series_to_table_data(series):
        """
        Turns the results from the sql database to a format that can be loaded into the ListCtrl
        :param series:
        :return: rows: 2D list to be loaded into set_table_content()
        """
        rows = []
        for s in series:
            data = []
            variable = s.VariableObj
            unit = s.UnitsObj
            action = s.FeatureActionObj.ActionObj
            samplingfeature = s.FeatureActionObj.SamplingFeatureObj
            organization = s.FeatureActionObj.ActionObj.MethodObj.OrganizationObj

            data.append(str(getattr(s, "ResultID", "N/A")))
            data.append(str(getattr(variable, 'VariableCode', 'N/A')))
            data.append(str(getattr(unit, 'UnitsName', 'N/A')))
            data.append(str(getattr(action, 'BeginDateTime', 'N/A')))
            data.append(str(getattr(action, 'ActionTypeCV', 'N/A')))
            data.append(str(getattr(samplingfeature, 'SamplingFeatureCode', 'N/A')))
            data.append(str(getattr(organization, 'OrganizationName', 'N/A')))
            rows.append(data)
        return rows

    def _load_wof(self, name):
        """
        Loads everything necessary to show Logan River
        :return:
        """
        columns = ["Site Name", "Network", "County", "State", "Site Type", "Site Code"]
        self.set_columns(columns)
        value = self.wof_names[name]
        self.api = wateroneflow.WaterOneFlow(value['wsdl'], value['network'])
        data = self.api.get_sites_in_list()
        self.set_table_content(data)

    ###############################
    # EVENTS
    ###############################

    def on_add_connection(self, event):
        AddConnectionCtrl(self)

    def on_connection_combo(self, event):
        self.empty_list_message.Hide()
        selection = event.GetEventObject().GetStringSelection()
        if selection == "---":
            self.clear_content()
            return

        self.clear_table()
        if selection in self.wof_names:
            self._load_wof(selection)
            return

        self.load_SQL_database()

    def on_double_click(self, event):
        """
        Open the WofSiteCtrl
        :param event:
        :return:
        """
        if self.connection_combo.GetStringSelection() in self.wof_names:
            # WofSiteCtrl takes an object so need to convert row into object
            site_object = self.convert_selected_row_into_object()
            WofSitesCtrl(self, site_object, self.api)

    def on_right_click(self, event):
        self.PopupMenu(self.popup_menu)

    def on_refresh_table(self, event):
        """
        Refreshes both the table and the connection combo
        :param event:
        :return:
        """
        self.load_connection_combo()
        selection = self.connection_combo.GetStringSelection()
        if selection != "---":
            if selection in self.wof_names:
                self._load_wof(selection)
                return

            self.load_SQL_database()

    def on_view_menu(self, event):
        self.on_double_click(event)