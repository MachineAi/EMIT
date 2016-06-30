import wx
import wx.lib.scrolledpanel


class NewSettingsView(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        # Create panels
        panel = wx.Panel(self)
        menu_panel = wx.Panel(panel, size=(100, -1))
        # self.details_panel = wx.Panel(panel)
        self.details_panel = wx.lib.scrolledpanel.ScrolledPanel(panel)
        lower_panel = wx.Panel(panel)

        ###########################
        # MENU PANEL
        ###########################

        # Create components
        self.console_button = wx.Button(menu_panel, label="Console", style=wx.BORDER_NONE)
        self.another_button = wx.Button(menu_panel, label="Another", style=wx.BORDER_NONE)
        self.console_button.SetForegroundColour(wx.LIGHT_GREY)
        self.another_button.SetForegroundColour(wx.LIGHT_GREY)

        # Create sizer and add components
        menu_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        menu_panel_sizer.Add(self.console_button, 0, wx.EXPAND | wx.ALL, 5)
        menu_panel_sizer.Add(self.another_button, 0, wx.EXPAND | wx.ALL, 5)
        menu_panel.SetSizer(menu_panel_sizer)

        menu_panel.SetBackgroundColour((33, 117, 155))

        ###########################
        # DETAILS PANEL
        ###########################

        self.details_panel.SetupScrolling()
        # Console controls
        self.__create_console_panel()

        # Another controls
        self.__create_another_panel()

        ###########################
        # LOWER PANEL
        ###########################

        # Create components
        self.save_button = wx.Button(lower_panel, label="Save")
        self.cancel_button = wx.Button(lower_panel, label="Cancel")

        # Create sizer and add components
        lower_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_panel_sizer.AddSpacer((0, 0), 1, wx.EXPAND, 2)
        lower_panel_sizer.Add(self.cancel_button, 0, wx.EXPAND | wx.ALL, 5)
        lower_panel_sizer.Add(self.save_button, 0, wx.EXPAND | wx.ALL, 5)

        lower_panel.SetSizer(lower_panel_sizer)

        ###########################
        # ORGANIZE FRAME
        ###########################

        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.main_sizer.Add(menu_panel, 0, wx.EXPAND | wx.ALL, 0)
        self.main_sizer.Add(self.details_panel, 1, wx.EXPAND | wx.LEFT, 5)

        self.frame_sizer.Add(self.main_sizer, 1, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 5)
        self.frame_sizer.Add(lower_panel, 0, wx.EXPAND | wx.ALL, 0)

        panel.SetSizer(self.frame_sizer)

        self.Show()

    def __create_console_panel(self):
        # self.console_panel = wx.Panel(self.details_panel)
        self.console_panel = wx.lib.scrolledpanel.ScrolledPanel(self.details_panel)
        self.info_text = wx.CheckBox(self.console_panel, label="Display info message")
        self.warning_text = wx.CheckBox(self.console_panel, label="Display warning message")
        self.critical_text = wx.CheckBox(self.console_panel, label="Display critical message")
        self.debug_text = wx.CheckBox(self.console_panel, label="Display debug message")
        self.error_checkbox = wx.CheckBox(self.console_panel, label="Display error message")

        static_box = wx.StaticBox(self.console_panel, label="Display Message")
        console_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        console_sizer.Add(self.info_text)
        console_sizer.Add(self.warning_text)
        console_sizer.Add(self.critical_text)
        console_sizer.Add(self.debug_text)
        console_sizer.Add(self.error_checkbox)
        self.console_panel.SetSizer(console_sizer)
        console_sizer.Fit(self.console_panel)

    def __create_another_panel(self):
        # self.another_panel = wx.Panel(self.details_panel)
        self.another_panel = wx.lib.scrolledpanel.ScrolledPanel(self.details_panel)
        self.another_text = wx.StaticText(self.another_panel, label="Another text")
        another_sizer = wx.BoxSizer(wx.VERTICAL)
        another_sizer.Add(self.another_text)
        self.another_panel.SetSizer(another_sizer)
        another_sizer.Fit(self.another_panel)
        self.another_panel.Hide()
