"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all its widgets.
WelcomeDialog - configures the welcome dialog and all its widgets.
RunSimulationPanel - configures the running simulation panel and all its widgets.
SettingsDialog - configures the settings dialog and all its widgets.
HelpDialog - configures the help dialog and all its widgets.
SignalTracesPanel - configures the signal traces panel and all its widgets.
SwitchesPanel - configures the switches panel and all its widgets.
"""
import os
from io import StringIO
from contextlib import redirect_stdout
from collections import defaultdict
from pathlib import Path

import wx
import wx.lib.scrolledpanel as wxscrolledpanel
import wx.lib.buttons as wxbuttons
from wx import GetTranslation as _

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from canvas import MyGLCanvas


class Gui(wx.Frame):
    """Configure the main GUI window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    path: path to the logic description file (LDF).
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    first_init: bool to indicate first initialisation.
    locale: language settings.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_quit_button(self, event): Event handler for when the user clicks the QUIT button.

    extract_ldf_title(self): Returns the name of the logic description file supplied from the file path.
    """

    def __init__(self, path, names, devices, network, monitors, first_init=True, locale=None):
        """Initialise widgets and layout."""
        super().__init__(parent=None, size=(1030, 700))

        # Create instance variables for Gui class
        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.first_init = first_init

        # Extract the title of the LDF
        self.ldf_title = self.extract_ldf_title()

        # Confirm first initialisation of the GUI and set the language of the GUI
        if self.first_init:
            self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        else:
            self.locale = locale
        
        # Add the translation catalog
        self.locale.AddCatalogLookupPathPrefix("locales")
        self.locale.AddCatalog("translate")

        # Configure the title of the GUI frame window
        team_name = _("GF2 P2 Team 7 Logic Simulator GUI: ")
        self.SetTitle(team_name + self.ldf_title)

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        menuBar.Append(fileMenu, _("&File"))
        self.SetMenuBar(menuBar)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)

        # Configure sizers for layout of Frame
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create data panel and add to Frame
        data_panel = wx.Panel(self)
        vbox.Add(data_panel, 8, wx.EXPAND)
        data_panel.SetSizer(hbox)

        # Instantiate SignalTracesPanel widget and add to Frame
        self.signal_traces_panel = SignalTracesPanel(
            data_panel, names, devices, network, monitors)
        hbox.Add(self.signal_traces_panel, 2, wx.EXPAND, 0)

        # Instantiate RunSimulationPanel widget and add to Frame
        self.simulation_panel = RunSimulationPanel(
            self, self.signal_traces_panel, names, devices, network, monitors)
        vbox.Add(self.simulation_panel, 1, wx.EXPAND)

        # Instantiate SwitchesPanel widget and add to Frame
        self.switches_panel = SwitchesPanel(
            data_panel, self.simulation_panel, names, devices, network, monitors)
        hbox.Add(self.switches_panel, 1, wx.EXPAND, 0)

        # Configure minimum allowable size of Frame
        self.SetSizeHints(1150 + self.switches_panel.text_width, 700)

        self.SetSizer(vbox)

        # Confirm first initialisation of the Gui and then show welcome dialog
        if self.first_init:
            welcome_dialog = WelcomeDialog(self)

            welcome_dialog.CenterOnScreen()

            welcome_dialog.ShowModal()

            welcome_dialog.Destroy()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(_("Logic Simulator\nCreated by Josephine Cowley (jhmdc2), Tom Hill (th621), Khalid Omar (ko366)\n2023"),
                          _("About Logsim"), wx.ICON_INFORMATION | wx.OK)

    def on_quit_button(self, event):
        """Handle the event when the user presses the QUIT button."""
        self.Close()

    def extract_ldf_title(self):
        """Extract the name of the LDF file supplied from the file path."""
        ldf_title = self.path.split(os.sep)[-1]

        return ldf_title


class WelcomeDialog(wx.Dialog):
    """Configure the welcome dialog and all the widgets.

    This class provides a welcome dialog for the Logic Simulator that appears only at first initialisation of the GUI and enables the
    user to receive help on how to get started, confirm and continue with the pre-loaded logic description file or upload a new logic description file.

    Parameters
    ----------
    parent: parent of the dialog window.
    title (optional): title of the dialog window.
    id (optional): id of the dialog window. 
    size (optional): size of the dialog window.
    style (optional): style of the dialog window. 

    Public methods
    --------------
    on_help_button(self, event): Event handler when the user clicks the help (tutorial) button.

    open_help_dialog(self): Opens the help dialog window containing the Logic Simulator tutorial.

    on_upload_new_file(self, event): Event handler when the user clicks the upload new file button.

    on_continue_button(self, event): Event handler when the user clicks the continue button.
    """
    def __init__(self, parent, title=_("GF2 P2 Team 7 Logic Simulator GUI"), id=wx.ID_ANY, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        """Initialise widgets and layout."""
        super(WelcomeDialog, self).__init__(parent, title=_(title), id=id, size=size, style=style)

        # Create instance variables for the WelcomeDialog class
        self.parent = parent

        # Configure sizer for layout of the Dialog box
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create and set the sizers for the panels in the Dialog box
        top_panel = wx.Panel(self)
        top_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        top_panel.SetSizer(top_panel_vbox)

        middle_panel = wx.Panel(self)
        middle_panel_fgs = wx.FlexGridSizer(cols=2, rows=2, vgap=4, hgap=50)
        middle_panel.SetSizer(middle_panel_fgs)

        bottom_panel = wx.Panel(self)
        bottom_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        bottom_panel.SetSizer(bottom_panel_hbox)

        # Create and add widgets to the top panel of the Dialog box
        welcome_text = wx.StaticText(top_panel, wx.ID_ANY, _("Welcome to our Logic Simulator!\n"), style=wx.ALIGN_CENTER)
        welcome_font = wx.Font(18, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        welcome_text.SetFont(welcome_font)
        top_panel_vbox.Add(welcome_text, 0, wx.ALIGN_CENTER)

        # Create and add widgets to the middle panel of the Dialog box
        help_prompt_text = wx.StaticText(middle_panel, wx.ID_ANY, _("Need some help?"))
        middle_panel_font = wx.Font(10, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        help_prompt_text.SetFont(middle_panel_font)
        middle_panel_fgs.Add(help_prompt_text, 0, wx.ALIGN_LEFT)

        help_button = wx.Button(middle_panel, wx.ID_ANY, label=_("Tutorial"))
        help_button.Bind(wx.EVT_BUTTON, self.on_help_button, help_button)
        help_button.SetToolTip(_("Click here to learn how to use our Logic Simulator"))
        middle_panel_fgs.Add(help_button, 1, flag=wx.EXPAND)

        preloaded_ldf_text = wx.StaticText(middle_panel, wx.ID_ANY, _("Pre-loaded\nLogic Description File: "))
        preloaded_ldf_text.SetFont(middle_panel_font)
        middle_panel_fgs.Add(preloaded_ldf_text, 0, wx.ALIGN_LEFT)

        preloaded_ldf_title = self.parent.ldf_title
        preloaded_ldf_title_text = wx.StaticText(middle_panel, wx.ID_ANY, preloaded_ldf_title)
        middle_panel_fgs.Add(preloaded_ldf_title_text, 0, wx.BOTTOM)

        # Create and add widgets to the bottom panel of the Dialog box
        upload_new_file_button = wx.Button(bottom_panel, wx.ID_ANY, label=_("Upload new file"))
        upload_new_file_button.Bind(wx.EVT_BUTTON, self.on_upload_new_file, upload_new_file_button)
        upload_new_file_button.SetToolTip(_("Upload a new Logic Description File"))
        bottom_panel_hbox.Add(upload_new_file_button, 1, flag=wx.EXPAND)

        continue_button = wx.Button(bottom_panel, wx.ID_ANY, label=_("Continue"))
        continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button, continue_button)
        continue_button.SetToolTip(_("Continue with preloaded logic description file"))
        bottom_panel_hbox.Add(continue_button, 1, flag=wx.EXPAND)

        # Add the panels to the Dialog box
        vbox.Add(top_panel, 1, flag=wx.EXPAND, border=10)
        vbox.Add(middle_panel, 2, flag=wx.EXPAND, border=10)
        vbox.Add(bottom_panel, 1, flag=wx.EXPAND, border=10)

        self.SetSizer(vbox)
        vbox.Fit(self)
    
    def on_help_button(self, event):
        """Handle the event when the user clicks the help (tutorial) button."""
        self.open_help_dialog()

    def open_help_dialog(self):
        """Open a help dialog window."""
        help_dialog = HelpDialog(self)

        help_dialog.CenterOnScreen()

        help_dialog.ShowModal()

        help_dialog.Destroy()

    def on_upload_new_file(self, event):
        """Handle the event when the user clicks the upload new file button."""
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Text file (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.FD_OPEN |
            wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
            wx.FD_PREVIEW
        )

        file_path = None

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            file_path = dlg.GetPath()

        if file_path is not None:  # confirm a file has been selected from upload file dialog
            # Create new instance variables for the Gui class
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(file_path, names)
            parser = Parser(names, devices, network, monitors, scanner)

            # Capture any potential printed terminal outputs in case any parsing errors occur
            captured_print = StringIO()
            with redirect_stdout(captured_print):
                # Parse the network
                parsing_result = parser.parse_network()

            # Store the potential printed terminal outputs
            output = captured_print.getvalue()

            # If parsing was successful (i.e., no errors in LDF file)
            if parsing_result:
                new_Gui = Gui(file_path,
                              names,
                              devices,
                              network,
                              monitors,
                              first_init=False,
                              locale=self.parent.locale)
                new_Gui.Show()
                self.Close()
                self.parent.Close()
            else:
                dlg = wx.MessageDialog(self, output,
                                       _("An error occurred."),
                                       wx.OK | wx.ICON_INFORMATION
                                       )
                dlg.ShowModal()
                dlg.Destroy()

        dlg.Destroy()
    
    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        self.Close()


class RunSimulationPanel(wx.Panel):
    """Configure the running simulation panel and all the widgets.

    This class provides the simulation panel for the Gui which contains the functionality for running the logic circuit network supplied in the LDF, 
    clearing the signal traces, resetting the GUI and qutting the GUI. It also allows the user to upload new logic description files, change the language
    settings of the GUI and access help on the use of the Logic Simulator.

    Parameters
    ----------
    parent: parent of the dialog window.
    signal_traces_panel: instance of the SignalTraces() class.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    id (optional): id of the dialog window. 
    size (optional): size of the dialog window.

    Public methods
    --------------
    on_run_button(self, event): Event handler when the user clicks the RUN/CONTINUE button.

    on_clear_button(self, event): Event handler when the user clicks the CLEAR button.

    on_reset_button(self, event): Event handler when the user clicks the RESET button.

    run_network(self, cycles): Run the logic circuit network for the specified number of cycles.
                               Returns True if executing the network was successful.
                               Returns False if executing the network was unsuccessful.

    update_canvas(self): Updates the canvas with the data generated by running the network for the specified number of cycles.

    on_spin(self, event): Event handler when the user clicks the spin button controls.
                          Returns None.

    on_upload_button(self, event): Event handler when the user clicks the UPLOAD button.

    on_settings_button(self, event): Event handler when the user clicks the SETTINGS button.

    on_help_button(self, event): Event handler when the user clicks the HELP button.

    open_help_dialog(self): Opens the help dialog window containing the Logic Simulator tutorial.
    """
    def __init__(self, parent, signal_traces_panel, names, devices, network, monitors, id=wx.ID_ANY, size=wx.DefaultSize):
        """Initialise widgets and layout."""
        super(RunSimulationPanel, self).__init__(
            parent, id, size=size, style=wx.SIMPLE_BORDER)

        # Create instance variables for the RunSimulationPanel class
        self.parent = parent
        self.signal_traces_panel = signal_traces_panel
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.path = parent.path

        # Configure sizers for layout of RunSimulationPanel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create, set sizer and add overall cycles + left buttons panel
        self.cycles_and_left_buttons_panel = wx.Panel(self)
        self.cycles_and_left_buttons_panel.SetSizer(vbox)
        hbox.Add(self.cycles_and_left_buttons_panel, 1, flag=wx.ALIGN_LEFT)

        # Create, set sizer and add top padding panel of cycles + left buttons panel
        self.cycles_and_left_buttons_panel_top_padding = wx.Panel(self.cycles_and_left_buttons_panel)
        cycles_and_left_buttons_panel_top_padding_vbox = wx.BoxSizer(wx.VERTICAL)
        self.cycles_and_left_buttons_panel_top_padding.SetSizer(cycles_and_left_buttons_panel_top_padding_vbox)
        vbox.Add(self.cycles_and_left_buttons_panel_top_padding, 1, flag=wx.EXPAND)

        # Create and add centre padding of cycles + left buttons panel
        self.cycles_and_left_buttons_panel_centre_padding = wx.Panel(self.cycles_and_left_buttons_panel)
        vbox.Add(self.cycles_and_left_buttons_panel_centre_padding, 1, flag=wx.EXPAND)

        # Create, set sizer and add bottom padding of cycles + left buttons panel
        self.cycles_and_left_buttons_panel_bottom_padding = wx.Panel(self.cycles_and_left_buttons_panel)
        cycles_and_left_buttons_panel_bottom_padding_vbox = wx.BoxSizer(wx.VERTICAL)
        self.cycles_and_left_buttons_panel_bottom_padding.SetSizer(cycles_and_left_buttons_panel_bottom_padding_vbox)
        vbox.Add(self.cycles_and_left_buttons_panel_bottom_padding, 2, flag=wx.EXPAND)

        # Create, configure, set and add cycles panel to overall cycles + left buttons panel
        self.cycles_panel = wx.Panel(self.cycles_and_left_buttons_panel_top_padding)
        cycles_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.cycles_panel.SetSizer(cycles_hbox)
        cycles_and_left_buttons_panel_top_padding_vbox.Add(self.cycles_panel, 1, flag=wx.TOP)

        # Create and add number of cycles text to cycles panel
        str = _("NO. CYCLES")
        text = wx.StaticText(self.cycles_panel, wx.ID_ANY,
                             str, style=wx.ALIGN_LEFT)
        font = wx.Font(15, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        cycles_hbox.Add(text, 0, flag=wx.TOP | wx.LEFT)
        cycles_spin_control = wx.SpinCtrl(self.cycles_panel, -1, "", (30, 50))
        cycles_spin_control.SetRange(1, 100)
        cycles_spin_control.SetValue(5)
        self.cycles_spin_control = cycles_spin_control
        self.Bind(wx.EVT_SPINCTRL, self.on_spin, self.cycles_spin_control)
        cycles_hbox.Add(self.cycles_spin_control, 0, flag=wx.LEFT, border=10)

        # Create, configure, set and add left buttons panel to overall cycles + left buttons panel
        self.left_buttons_panel = wx.Panel(self.cycles_and_left_buttons_panel_bottom_padding)
        left_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.left_buttons_panel.SetSizer(left_buttons_panel_hbox)
        cycles_and_left_buttons_panel_bottom_padding_vbox.Add(self.left_buttons_panel, 1, flag=wx.BOTTOM)

        # Create, bind running simulation event to and add the "RUN" button to the RUN button panel in left buttons panel
        self.run_button_panel = wx.Panel(self.left_buttons_panel)
        run_buttons_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.run_button_panel.SetSizer(run_buttons_panel_vbox)
        left_buttons_panel_hbox.Add(self.run_button_panel, flag=wx.ALIGN_BOTTOM, border=0)

        # Create, bind running simulation event to and add the "RUN" button
        self.run_button = wxbuttons.GenButton(
            self.run_button_panel, wx.ID_ANY, _("RUN"), name="run button")
        self.Bind(wx.EVT_BUTTON, self.on_run_button, self.run_button)
        self.run_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.run_button.SetBezelWidth(5)
        self.run_button.SetMinSize(wx.DefaultSize)
        self.run_button.SetBackgroundColour(wx.Colour(4, 84, 14))
        self.run_button.SetForegroundColour(wx.WHITE)
        self.run_button.SetToolTip(_("Begin running the simulation"))
        run_buttons_panel_vbox.Add(
            self.run_button, 1, flag=wx.ALIGN_BOTTOM, border=0)
        
        # Create, bind clearing signal traces event to and add the "CLEAR" button
        self.clear_button = wxbuttons.GenButton(
            self.left_buttons_panel, wx.ID_ANY, _("CLEAR"), name="clear button")
        self.Bind(wx.EVT_BUTTON, self.on_clear_button, self.clear_button)
        self.clear_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.clear_button.SetBezelWidth(5)
        self.clear_button.SetMinSize(wx.DefaultSize)
        self.clear_button.SetBackgroundColour(wx.Colour(0, 0, 205))
        self.clear_button.SetForegroundColour(wx.WHITE)
        self.clear_button.SetToolTip(_("Clear all signal traces"))
        left_buttons_panel_hbox.Add(
            self.clear_button, 1, flag=wx.ALIGN_BOTTOM, border=0)
        
        # Create, bind resetting signal traces event to and add the "RESET" button
        self.reset_button = wxbuttons.GenButton(
            self.left_buttons_panel, wx.ID_ANY, _("RESET"), name="reset button")
        self.Bind(wx.EVT_BUTTON, self.on_reset_button, self.reset_button)
        self.reset_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.reset_button.SetBezelWidth(5)
        self.reset_button.SetMinSize(wx.DefaultSize)
        self.reset_button.SetBackgroundColour(wx.Colour(205, 102, 29))
        self.reset_button.SetForegroundColour(wx.WHITE)
        self.reset_button.SetToolTip(_("Reset the simulation from initialisation"))
        left_buttons_panel_hbox.Add(
            self.reset_button, 1, flag=wx.ALIGN_BOTTOM, border=0)

        # Create, set sizer and add centre panel
        self.centre_panel = wx.Panel(self)
        centre_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.centre_panel.SetSizer(centre_panel_vbox)
        hbox.Add(self.centre_panel, 2, flag=wx.RIGHT|wx.EXPAND, border=10)

        # Create and add top padding of centre panel
        self.centre_panel_top_padding = wx.Panel(self.centre_panel)
        centre_panel_vbox.Add(self.centre_panel_top_padding, 1, flag=wx.EXPAND)

        # Create, set sizer and add bottom padding of centre panel
        self.centre_panel_bottom_padding = wx.Panel(self.centre_panel)
        centre_panel_bottom_padding_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.centre_panel_bottom_padding.SetSizer(centre_panel_bottom_padding_hbox)
        centre_panel_vbox.Add(self.centre_panel_bottom_padding, 1, flag=wx.EXPAND)

        # Create and add left panel to bottom padding of centre panel
        self.centre_panel_bottom_padding_left = wx.Panel(self.centre_panel_bottom_padding)
        centre_panel_bottom_padding_hbox.Add(self.centre_panel_bottom_padding_left, 1, flag=wx.EXPAND)

        # Create and add right panel to bottom padding of centre panel
        self.centre_panel_bottom_padding_right = wx.Panel(self.centre_panel_bottom_padding)
        centre_panel_bottom_padding_right_vbox = wx.BoxSizer(wx.VERTICAL)
        self.centre_panel_bottom_padding_right.SetSizer(centre_panel_bottom_padding_right_vbox)
        centre_panel_bottom_padding_hbox.Add(self.centre_panel_bottom_padding_right, 2, flag=wx.EXPAND)

        # Create, bind quitting event to and add the "QUIT" button
        self.quit_button = wxbuttons.GenButton(
            self.centre_panel_bottom_padding_right, wx.ID_ANY, _("QUIT"), name="quit button")
        self.Bind(wx.EVT_BUTTON, parent.on_quit_button, self.quit_button)
        self.quit_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.quit_button.SetBezelWidth(5)
        self.quit_button.SetMinSize(wx.DefaultSize)
        self.quit_button.SetBackgroundColour(wx.Colour(139, 26, 26))
        self.quit_button.SetForegroundColour(wx.WHITE)
        self.quit_button.SetToolTip(_("Quit the simulation"))
        centre_panel_bottom_padding_right_vbox.Add(
            self.quit_button, 1, flag=wx.ALIGN_RIGHT, border=5)

        # Create, set sizer and add right buttons panel
        self.right_buttons_panel = wx.Panel(
            self, name="right buttons panel")
        right_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.right_buttons_panel.SetSizer(
            right_buttons_panel_hbox)
        hbox.Add(self.right_buttons_panel, 1, flag=wx.EXPAND)

        # Create and set sizer of upload button panel
        self.upload_button_panel = wx.Panel(
            self.right_buttons_panel, name="upload button panel")
        upload_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.upload_button_panel.SetSizer(upload_button_panel_vbox)

        # Create, bind uploading new LDF file event to and add the "UPLOAD" button
        self.upload_button = wx.Button(
            self.upload_button_panel, wx.ID_ANY, _("UPLOAD"))
        self.Bind(wx.EVT_BUTTON, self.on_upload_button, self.upload_button)
        self.upload_button.SetToolTip(_("Upload logic description file"))
        upload_button_panel_vbox.Add(
            self.upload_button, 1, flag=wx.ALIGN_CENTER)
        
        # Create and set sizer of settings button panel
        self.settings_button_panel = wx.Panel(
            self.right_buttons_panel, name="settings button panel")
        settings_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.settings_button_panel.SetSizer(settings_button_panel_vbox)

        # Create, bind opening settings event to and add the "SETTINGS" button
        self.settings_button = wx.Button(
            self.settings_button_panel, wx.ID_ANY, _("SETTINGS"))
        self.Bind(wx.EVT_BUTTON, self.on_settings_button, self.settings_button)
        self.settings_button.SetToolTip(_("Change system settings"))
        settings_button_panel_vbox.Add(
            self.settings_button, 1, flag=wx.ALIGN_CENTER)

        # Create and set sizer of help button panel
        self.help_button_panel = wx.Panel(
            self.right_buttons_panel, name="help button panel")
        help_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.help_button_panel.SetSizer(help_button_panel_vbox)

        # Create, bind opening help dialog box event to and add the "HELP" button
        self.help_button = wx.Button(self.help_button_panel, wx.ID_ANY, _("HELP"))
        self.Bind(wx.EVT_BUTTON, self.on_help_button, self.help_button)
        self.help_button.SetToolTip(_("Help on running logic simulation"))
        help_button_panel_vbox.Add(self.help_button, 1, flag=wx.ALIGN_CENTER)

        # Add the (upload button, settings button, help button) panels
        right_buttons_panel_hbox.Add(
            self.upload_button_panel, 1, flag=wx.CENTER)
        right_buttons_panel_hbox.Add(self.settings_button_panel, 1, flag=wx.CENTER)
        right_buttons_panel_hbox.Add(
            self.help_button_panel, 1, flag=wx.CENTER)

        # Set sizer of RunSimulationPanel
        self.SetSizer(hbox)

    def on_run_button(self, event):
        """Handle the event when the user clicks the RUN/CONTINUE button."""
        run_button_pressed = event.GetEventObject()
        run_button_pressed.SetLabel(_("CONTINUE"))
        run_button_pressed.SetBackgroundColour(wx.Colour(181, 150, 27))
        run_button_pressed.SetToolTip(_("Continue running the simulation"))
        self.GetSizer().Layout()

        no_of_cycles = self.cycles_spin_control.GetValue()

        self.run_network(no_of_cycles)
        self.update_canvas()

    def on_clear_button(self, event):
        """Handle the event when the user clicks the CLEAR button."""
        self.parent.signal_traces_panel.canvas.clear_traces()


    def on_reset_button(self, event):
        """Handle the event when the user clicks the RESET button."""
        # Recreate the same instance variables as the current Gui class
        file_path = self.parent.path
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)#
        parser.parse_network()

        new_Gui = Gui(file_path,
                      names,
                      devices,
                      network,
                      monitors,
                      first_init=False,
                      locale=self.parent.locale)
        new_Gui.Show()
        self.parent.Close()

    def run_network(self, cycles):
        """Run the logic network for the specificed number of cycles.
        
        Return True if executing the network was successful.
        Return False if executing the network was unsuccessful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print(_("Error! Network oscillating."))
                return False
        self.monitors.display_signals()
        return True

    def update_canvas(self):
        """Update the canvas with the data generated from executing the network for a specified number of cycles."""
        self.signal_traces_panel.canvas.update_arguments(
            self.devices, self.monitors)

    def on_spin(self, event):
        """Handle the event when the user clicks the spin button controls.
        
        Return None.
        """
        # Spin button control only stores the number of cycles
        # Requires no event handling itself
        pass

    def on_upload_button(self, event):
        """Handle the event when the user clicks the upload button."""
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Text file (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.FD_OPEN |
            wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
            wx.FD_PREVIEW
        )

        file_path = None

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            file_path = dlg.GetPath()

        if file_path is not None:  # confirm a file has been selected from upload file dialog
            # Create new instance variables for the Gui class
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(file_path, names)
            parser = Parser(names, devices, network, monitors, scanner)

            # Capture any potential printed terminal outputs in case any parsing errors occur
            captured_print = StringIO()
            captured_print = StringIO()
            with redirect_stdout(captured_print):
                parsing_result = parser.parse_network()

            # Store the potential printed terminal outputs
            output = captured_print.getvalue()

            # If parsing was successful (i.e., no errors in LDF file)
            if parsing_result:
                new_Gui = Gui(file_path,
                              names,
                              devices,
                              network,
                              monitors,
                              first_init=False,
                              locale=self.parent.locale)
                new_Gui.Show()
                self.parent.Close()
            else:
                dlg = wx.MessageDialog(self, output,
                                       _("An error occurred."),
                                       wx.OK | wx.ICON_INFORMATION
                                       )
                dlg.ShowModal()
                dlg.Destroy()

    def on_settings_button(self, event):
        """Handle the event when the user clicks the SETTINGS button."""
        self.settings_dialog = SettingsDialog(self)

        self.settings_dialog.CenterOnScreen()

        self.settings_dialog.ShowModal()

        self.settings_dialog.Destroy()

    def on_help_button(self, event):
        """Handle the event when the user clicks the HELP button."""
        self.open_help_dialog()

    def open_help_dialog(self):
        """Open a help dialog window."""
        help_dialog = HelpDialog(self)

        help_dialog.CenterOnScreen()

        help_dialog.ShowModal()

        help_dialog.Destroy()


class SettingsDialog(wx.Dialog):
    """Configure the settings dialog and all the widgets.

    This class provides a settings dialog for the Logic Simulator that enables the user to 
    change the language settings of the GUI.

    Parameters
    ----------
    parent: parent of the dialog window.
    title (optional): title of the dialog window.
    id (optional): id of the dialog window. 
    size (optional): size of the dialog window.
    style (optional): style of the dialog window. 

    Public methods
    --------------
    on_select_new_language(self, event): Event handler when the user selects a language from the dropdown menu.

    on_confirm_settings_button(self, event): Event handler when the user confirms the choice of selected language.
    """
    def __init__(self, parent, title=_("Configure Logic Simulator GUI settings"), id=wx.ID_ANY, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        """Initialise widgets and layout."""
        super(SettingsDialog, self).__init__(parent, title=_(title), id=id, size=size, style=style)

        # Create instance variables for the SettingsDialog class
        self.parent = parent

        # Configure sizer for layout of the Dialog box
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create and set the sizers for the panels in the Dialog box
        top_panel = wx.Panel(self)
        top_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        top_panel.SetSizer(top_panel_vbox)

        bottom_panel = wx.Panel(self)
        bottom_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        bottom_panel.SetSizer(bottom_panel_vbox)
 
        # Create and add widgets to the top panel of the Dialog box
        text = wx.StaticText(top_panel, wx.ID_ANY, _("GUI Settings"), style=wx.ALIGN_CENTER)
        font = wx.Font(18, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        top_panel_vbox.Add(text, 0, wx.ALIGN_CENTER)

        self.selected_language = None
        available_languages_list = ["English (GB)", "Español (ES)", "Ελληνικά (EL)"]
        select_language_combo_box = wx.ComboBox(top_panel, wx.ID_ANY, _("Select language"), (90, 50),
                                                    (160, -1), available_languages_list,
                                                    wx.CB_DROPDOWN
                                                    )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_new_langauge,
                  select_language_combo_box)
        top_panel_vbox.Add(
            select_language_combo_box, 0, flag=wx.ALIGN_LEFT|wx.TOP, border=30)
        
        confirm_settings_button = wx.Button(bottom_panel, wx.ID_ANY, label=_("CONFIRM SETTINGS"))
        confirm_settings_button.Bind(wx.EVT_BUTTON, self.on_confirm_settings_button, confirm_settings_button)
        confirm_settings_button.SetToolTip(_("Confirm settings changes"))
        bottom_panel_vbox.Add(confirm_settings_button, 0, flag=wx.CENTER|wx.BOTTOM)

        # Add the panels to the Dialog box
        vbox.Add(top_panel, 3, flag=wx.EXPAND)
        vbox.Add(bottom_panel, 1, flag=wx.EXPAND)

        self.SetSizer(vbox)

    def on_select_new_langauge(self, event):
        """Handle the event when the user selects a language from the dropdown menu."""
        select_language_combo_box = event.GetEventObject()
        self.selected_language = select_language_combo_box.GetValue()

        print(self.selected_language)
        if self.selected_language is not None:
            pass
    
    def on_confirm_settings_button(self, event):
        """Handle the event when the user confirms the choice of selected language"""
        if self.selected_language is not None: # confirm if a langauage has been selected
            if self.selected_language == "English (GB)":
                new_Gui = Gui(self.parent.path,
                                self.parent.names,
                                self.parent.devices,
                                self.parent.network,
                                self.parent.monitors,
                                first_init=False,
                                locale=wx.Locale(wx.LANGUAGE_ENGLISH))
                new_Gui.Show()
                self.parent.settings_dialog.Destroy()
                self.parent.parent.Close()
            
            elif self.selected_language == "Español (ES)":
                new_Gui = Gui(self.parent.path,
                                self.parent.names,
                                self.parent.devices,
                                self.parent.network,
                                self.parent.monitors,
                                first_init=False,
                                locale=wx.Locale(wx.LANGUAGE_SPANISH))
                new_Gui.Show()
                self.parent.settings_dialog.Destroy()
                self.parent.parent.Close()
            
            elif self.selected_language == "Ελληνικά (EL)":
                new_Gui = Gui(self.parent.path,
                                self.parent.names,
                                self.parent.devices,
                                self.parent.network,
                                self.parent.monitors,
                                first_init=False,
                                locale=wx.Locale(wx.LANGUAGE_GREEK))
                new_Gui.Show()
                self.parent.settings_dialog.Destroy()
                self.parent.parent.Close()


class HelpDialog(wx.Dialog):
    """Configure the help dialog and all the widgets.

    This class provides a help dialog for the Logic Simulator that provides a tutorial and how to get started with using the
    functionality provided by the GUI in running simulations of the supplied logic network and navigating the wider GUI.

    Parameters
    ----------
    parent: parent of the dialog window.
    title (optional): title of the dialog window.
    id (optional): id of the dialog window. 
    size (optional): size of the dialog window.
    style (optional): style of the dialog window. 

    Public methods
    --------------
    No public methods.
    """
    def __init__(self, parent, title=_("Tutorial on GF2 Team 7 Logic Simulator"), id=wx.ID_ANY, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        super(HelpDialog, self).__init__(parent, title=_(title), id=id, size=size, style=style)

        vbox = wx.BoxSizer(wx.VERTICAL)

        help_dialog_file_path = Path(__file__).with_name("help_dialog.txt")
        with open(help_dialog_file_path, "r", encoding="utf8") as help_dialog_file:
            help_dialog_text_list = help_dialog_file.readlines()
        translated_help_dialog_text_list = [_(i) for i in help_dialog_text_list]
        translated_help_dialog_text = "".join(translated_help_dialog_text_list)

        help_message = wx.StaticText(self, wx.ID_ANY, translated_help_dialog_text)
        vbox.Add(help_message, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)


class SignalTracesPanel(wx.Panel):
    """Configure the signal traces panel and all the widgets.

    This class provides the signal traces panel for the Gui which displays the signal traces that are generated as a
    result of executing the logic circuit network for a specified number of cycles. It also enables the user to add
    or delete monitors to the logic circuit to observe new signal traces and provides functionality to recenter the
    canvas on which signal traces are drawn.

    Parameters
    ----------
    parent: parent of the dialog window.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    on_select_new_monitor(self, event): Event handler when the user selects an as-of-yet unmonitored signal.

    on_select_zap_monitor(self, event): Event handler when the user selects a currently monitored signal.

    on_add_new_monitor(self, event): Event handler when the user clicks the add new monitor (+) button.

    on_zap_existing_monitor(self, event): Event handler when the user clicks the zap existing monitor (-) button.

    on_recentre_button(self, event): Event handler when the user clicks the "RECENTER" button.

    update_canvas(self): Updates the canvas with the newly added/deleted signals to monitor in the logic network.
    """
    def __init__(self, parent, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super(SignalTracesPanel, self).__init__(
            parent, size=wx.DefaultSize, style=wx.BORDER_SUNKEN)

        # Create instance variables for SignalTracesPanel
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        # Configure sizers for layout of SignalTracesPanel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create and set sizers for the signal traces panel
        self.signal_traces_panel = wx.Panel(self, name="signal traces panel")
        signal_traces_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.signal_traces_panel.SetSizer(signal_traces_panel_vbox)

        self.add_new_monitor_panel = wx.Panel(self, name="add new monitor panel")
        add_new_monitor_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel.SetSizer(add_new_monitor_panel_hbox)

        # Create and add left panel to add new monitor panel
        self.add_new_monitor_panel_left = wx.Panel(self.add_new_monitor_panel, name="add new monitor panel left")
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_left, 1, flag=wx.EXPAND)

        # Create and centre panel to add new monitor panel
        self.add_new_monitor_panel_centre = wx.Panel(
            self.add_new_monitor_panel, name="add new monitor panel centre")
        add_new_monitor_panel_centre_fgs = wx.FlexGridSizer(
            cols=3, rows=3, vgap=4, hgap=50)
        self.add_new_monitor_panel_centre.SetSizer(add_new_monitor_panel_centre_fgs)
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_centre, 5, flag=wx.EXPAND)

        # Create and add "Add new monitor" text to centre of add new monitor panel
        str = _("ADD NEW MONITOR")
        text = wx.StaticText(self.add_new_monitor_panel_centre, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial")
        text.SetFont(font)
        add_new_monitor_panel_centre_fgs.Add(text, 0, flag=wx.ALIGN_CENTER)

        # Get the ids and user-defined names of all monitored and (as-of-yet) unmonitored devices
        self.monitored_devices_names = self.monitors.get_signal_names()[0]
        self.monitored_devices_ids = self.names.lookup(
            self.monitored_devices_names)
        self.unmonitored_devices_names = self.monitors.get_signal_names()[1]
        self.unmonitored_devices_ids = self.names.lookup(
            self.unmonitored_devices_names)

        # Create and add the dropdown menu for the as-of-yet unmonitored devices, ready to be monitored
        self.selected_signal_to_monitor = None
        self.monitor_output_list = self.unmonitored_devices_names
        self.select_monitor_combo_box = wx.ComboBox(self.add_new_monitor_panel_centre, wx.ID_ANY, _("Select output"), (90, 50),
                                                    (160, -1), self.monitor_output_list,
                                                    wx.CB_DROPDOWN
                                                    )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_new_monitor,
                  self.select_monitor_combo_box)
        add_new_monitor_panel_centre_fgs.Add(
            self.select_monitor_combo_box, 0, flag=wx.ALIGN_CENTER | wx.LEFT, border=30)

        # Create and add the "Add a new monitor" button to show the newly monitored device's signal trace on SignalTraces panel
        self.add_new_monitor_button = wx.Button(
            self.add_new_monitor_panel_centre, wx.ID_ANY, label="+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_monitor_button,
                  self.add_new_monitor_button)
        self.add_new_monitor_button.SetToolTip(_("Add a monitor"))
        add_new_monitor_panel_centre_fgs.Add(
            self.add_new_monitor_button, 1, flag=wx.CENTER | wx.EXPAND)

        # Create and add "Zap a monitor" text to add new monitor panel
        str = _("DELETE MONITOR")
        text = wx.StaticText(self.add_new_monitor_panel_centre, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_centre_fgs.Add(text, 0, flag=wx.ALIGN_LEFT)

        # Create and add the dropdown menu for the currently monitored devices, ready to be zapped
        self.selected_signal_to_zap = None
        self.monitor_output_list = self.monitored_devices_names
        self.zap_monitor_combo_box = wx.ComboBox(self.add_new_monitor_panel_centre, wx.ID_ANY, _("Select output"), (90, 50),
                                                 (160, -1), self.monitor_output_list,
                                                 wx.CB_DROPDOWN
                                                 # | wx.TE_PROCESS_ENTER
                                                 # | wx.CB_SORT
                                                 )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_zap_monitor,
                  self.zap_monitor_combo_box)
        add_new_monitor_panel_centre_fgs.Add(
            self.zap_monitor_combo_box, 0, flag=wx.ALIGN_CENTER | wx.LEFT, border=30)

        # Create and add the "Zap an existing monitor" button to remove a currently monitored device's signal trace on SignalTraces panel
        self.zap_existing_monitor_button = wx.Button(
            self.add_new_monitor_panel_centre, wx.ID_ANY, label="-")
        self.Bind(wx.EVT_BUTTON, self.on_zap_existing_monitor,
                  self.zap_existing_monitor_button)
        self.zap_existing_monitor_button.SetToolTip(_("Delete an existing monitor"))
        add_new_monitor_panel_centre_fgs.Add(
            self.zap_existing_monitor_button, 1, flag=wx.CENTER | wx.EXPAND)
        
        # Create, set sizer and add right panel to add new monitor panel
        self.add_new_monitor_panel_right = wx.Panel(self.add_new_monitor_panel, name="add new monitor panel right")
        add_new_monitor_panel_right_vbox = wx.BoxSizer(wx.VERTICAL)
        self.add_new_monitor_panel_right.SetSizer(add_new_monitor_panel_right_vbox)
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_right, 1, flag=wx.ALL|wx.EXPAND, border=10)

        # Create, bind recentering canvas event and add the "RECENTER" button
        self.recentre_button = wxbuttons.GenButton(
            self.add_new_monitor_panel_right, wx.ID_ANY, _("RECENTER"), name="recentre button")
        self.Bind(wx.EVT_BUTTON, self.on_recentre_button, self.recentre_button)
        self.recentre_button.SetFont(wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.recentre_button.SetBezelWidth(5)
        self.recentre_button.SetMinSize(wx.DefaultSize)
        self.recentre_button.SetBackgroundColour(wx.Colour(85, 26, 139))
        self.recentre_button.SetForegroundColour(wx.WHITE)
        self.recentre_button.SetToolTip(_("Recenter the signal traces"))
        add_new_monitor_panel_right_vbox.Add(
            self.recentre_button, 1, flag=wx.EXPAND, border=5)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self.signal_traces_panel, devices, monitors)
        signal_traces_panel_vbox.Add(self.canvas, 1, wx.EXPAND)

        vbox.Add(self.signal_traces_panel, 4, flag=wx.EXPAND)
        vbox.Add(self.add_new_monitor_panel, 1, flag=wx.EXPAND)

        # Set sizer of SignalTracesPanel
        self.SetSizer(vbox)

    def on_select_new_monitor(self, event):
        """Handle the event when the user selects an as-of-yet unmonitored signal to monitor."""
        select_monitor_combo_box = event.GetEventObject()
        self.selected_signal_to_monitor = select_monitor_combo_box.GetValue()

    def on_select_zap_monitor(self, event):
        """Handle the event when the user selects a currently monitored signal to zap."""
        zap_monitor_combo_box = event.GetEventObject()
        self.selected_signal_to_zap = zap_monitor_combo_box.GetValue()

    def on_add_new_monitor_button(self, event):
        """Handle the event when the user clicks the add new signal button."""
        add_new_monitor_button_pressed = event.GetEventObject()
        text = f"{add_new_monitor_button_pressed.GetLabel()} button pressed."

        # confirm if a new signal to monitor has been selected from dropdown menu
        if self.selected_signal_to_monitor is not None:
            selected_signal_to_monitor_id = self.devices.get_signal_ids(
                self.selected_signal_to_monitor)
            self.monitors.make_monitor(*selected_signal_to_monitor_id)

            self.update_canvas()

            selected_signal_to_monitor_selection_index = self.select_monitor_combo_box.GetSelection()
            if selected_signal_to_monitor_selection_index != wx.NOT_FOUND:
                # remove the selected signal to monitor from add menu
                self.select_monitor_combo_box.Delete(
                    selected_signal_to_monitor_selection_index)

            # confirm if selected signal not already in zap menu
            if self.selected_signal_to_monitor not in self.zap_monitor_combo_box.GetItems():
                # add selected signal to monitor to zap menu
                self.zap_monitor_combo_box.Append(
                    self.selected_signal_to_monitor)
            else:
                pass

    def on_zap_existing_monitor(self, event):
        """Handle the event when the user clicks the zap existing monitor button."""
        zap_existing_monitor_button_pressed = event.GetEventObject()
        text = f"{zap_existing_monitor_button_pressed.GetLabel()} button pressed."

        # confirm if an existing monitored signal has been selected from dropdown menu
        if self.selected_signal_to_zap is not None:
            selected_signal_to_zap_id = self.devices.get_signal_ids(
                self.selected_signal_to_zap)
            self.monitors.remove_monitor(*selected_signal_to_zap_id)

            self.update_canvas()

            selected_signal_to_zap_selection_index = self.zap_monitor_combo_box.GetSelection()
            if selected_signal_to_zap_selection_index != wx.NOT_FOUND:
                # remove the currently monitored signal from zap menu
                self.zap_monitor_combo_box.Delete(
                    selected_signal_to_zap_selection_index)

            # confirm if selected signal not already in add menu
            if self.selected_signal_to_zap not in self.select_monitor_combo_box.GetItems():
                # add currently monitored signal to add menu
                self.select_monitor_combo_box.Append(
                    self.selected_signal_to_zap)
            else:
                pass

    def on_recentre_button(self, event):
        """Handle the event when the user clicks the RECENTER button."""
        self.canvas.recenter_canvas()

    def update_canvas(self):
        """Update the canvas with the newly added/deleted signals to monitor in the logic network."""
        self.canvas.update_arguments(self.devices, self.monitors)


class SwitchesPanel(wx.Panel):
    """Configure the switches panel and all the widgets.

    This class provides the switches panel for the Gui which displays the list of switches as provided in the supplied
    logic description file. It enables the user to use toggle buttons to change the state of the switches which are shown
    in the switch state indicators beside the respective switch toggle button.

    Parameters
    ----------
    parent: parent of the dialog window.
    simulation_panel: instance of the RunSimulationPanel() class.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    on_switch_slider_button(self, event): Event handler for when the user clicks the slider for a switch.
    """
    def __init__(self, parent, simulation_panel, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super(SwitchesPanel, self).__init__(parent, size=(300, 200))

        # Create instance variables for SwitchesPanel
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.simulation_panel = simulation_panel

        # Configure sizers for layout of SwitchesPanel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create and add the title to SwitchesPanel
        str = _("INPUTS")
        text = wx.StaticText(self, wx.ID_ANY, str, style=wx.ALIGN_CENTER)
        font = wx.Font(18, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        vbox.Add(text, 0, wx.EXPAND)

        # Create and add a separating line between switches title and switch toggle buttons
        static_line = wx.StaticLine(self, wx.ID_ANY)
        vbox.Add(static_line, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        # Create panel for switch toggle buttons
        self.switches_panel = wx.Panel(self)
        vbox.Add(self.switches_panel, 7, wx.EXPAND)
        self.switches_panel.SetSizer(hbox)

        # Instantiate ScrolledPanel
        self.switch_buttons_scrolled_panel = wxscrolledpanel.ScrolledPanel(
            self.switches_panel, name="switch buttons scrolled panel")

        # Get the ids and user-defined names of all SWITCH-type devices
        switch_ids = devices.find_devices(device_kind=devices.SWITCH)
        switch_names = [names.get_name_string(i) for i in switch_ids]

        # Configure sizer of ScrolledPanel
        self.num_of_switches = len(switch_names)
        self.fgs = wx.FlexGridSizer(
            cols=3, rows=self.num_of_switches, vgap=4, hgap=4)
        
        # Get the width of the ON text (language dependent)
        on_dc = wx.ScreenDC()
        on_dc.SetFont(font)
        on_text_width, on_text_height = on_dc.GetTextExtent(_("ON"))

        # Get the width of the OFF text (language dependent)
        off_dc = wx.ScreenDC()
        off_dc.SetFont(font)
        off_text_width, off_text_height = off_dc.GetTextExtent(_("OFF"))

        # Select the text width as the greater one between that of ON or OFF (langauge dependent)
        self.text_width = off_text_width if off_text_width > on_text_width else on_text_width  

        # Instantiate a default dictionary of lists for the switches dictionary
        self.switch_dict = defaultdict(list)
        for switch_name in switch_names:
            # Get the id and initial state of a switch
            switch_id = self.names.query(switch_name)
            initial_switch_state = devices.get_device(switch_id).switch_state
            
            # Create the text for a switch based on its name
            switch_name_text = wx.StaticText(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"{switch_name}", style=wx.ALIGN_LEFT)
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
            switch_name_text.SetFont(font)

            # Create the panel for the switch slider
            switch_slider_panel = wx.Panel(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, style=wx.BORDER_SUNKEN, size=(90, 30))
            switch_slider_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            switch_slider_panel.SetSizer(switch_slider_panel_sizer)

            # Create the button for the switch slider and assign its pointer as the same as the id of its respective panel
            switch_slider_button = wxbuttons.GenButton(parent=switch_slider_panel, id=wx.ID_ANY, label="", name="switch slider")
            switch_slider_id = switch_slider_panel.GetId()
        
            # Bind the switch slider sliding event to the switch slider button
            self.Bind(wx.EVT_BUTTON, self.on_switch_slider_button, switch_slider_button)
            switch_slider_button.SetBezelWidth(5)
            switch_slider_button.SetMinSize((45, 30))
            switch_slider_button.SetBackgroundColour(wx.Colour(112, 112, 112))
        
            # Assign the initial position of the switch slider depending on initial switch state
            if initial_switch_state == 1:
                switch_slider_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_RIGHT, border=5)
            elif initial_switch_state == 0:
                switch_slider_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_LEFT, border=5)         

            # Assign the switch indicator to either ON or OFF depending on initial switch state
            if initial_switch_state == 1:
                switch_state_indicator_panel = wx.Panel(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, style=wx.BORDER_RAISED, size=(50, 30))
                switch_state_indicator_panel.SetBackgroundColour(wx.Colour(4, 84, 14))
                switch_state_indicator_panel_sizer = wx.BoxSizer(wx.VERTICAL)
                switch_state_indicator_panel.SetSizer(switch_state_indicator_panel_sizer)

                text = wx.StaticText(switch_state_indicator_panel, wx.ID_ANY, _("ON"), style=wx.ALIGN_LEFT)
                text.SetForegroundColour(wx.WHITE)
                switch_state_indicator_panel.SetMinSize((self.text_width, 30))
                switch_state_indicator_panel.Refresh()
                switch_state_indicator_panel.Update()

                switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)
            elif initial_switch_state == 0:
                switch_state_indicator_panel = wx.Panel(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, style=wx.BORDER_RAISED, size=(50, 30))
                switch_state_indicator_panel.SetBackgroundColour(wx.Colour(139, 26, 26))
                switch_state_indicator_panel_sizer = wx.BoxSizer(wx.VERTICAL)
                switch_state_indicator_panel.SetSizer(switch_state_indicator_panel_sizer)

                text = wx.StaticText(switch_state_indicator_panel, wx.ID_ANY, _("OFF"), style=wx.ALIGN_LEFT)
                text.SetForegroundColour(wx.WHITE)
                switch_state_indicator_panel.SetMinSize((self.text_width, 30))
                switch_state_indicator_panel.Refresh()
                switch_state_indicator_panel.Update()

                switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)

            # Add all relevant switch information to the switches dictionary
            self.switch_dict[switch_slider_id].extend([switch_id, switch_name, initial_switch_state, switch_slider_panel, switch_slider_panel_sizer, switch_state_indicator_panel, switch_state_indicator_panel_sizer])

            # Add switch slider/toggle buttons to ScrolledPanel
            self.fgs.Add(switch_name_text, 0, flag=wx.ALL, border=12)
            self.fgs.Add(switch_slider_panel, 2, flag=wx.ALL, border=10)
            self.fgs.Add(switch_state_indicator_panel, 1, flag=wx.ALL, border=10)

        # Set sizer of ScrolledPanel
        self.switch_buttons_scrolled_panel.SetSizer(self.fgs)
        self.switch_buttons_scrolled_panel.SetAutoLayout(1)
        self.switch_buttons_scrolled_panel.SetupScrolling(
            scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)


        # Add the ScrolledPanel widget to SwitchesPanel
        hbox.Add(self.switch_buttons_scrolled_panel, 3, wx.EXPAND)

        self.add_switch_panel = wx.Panel(self)
        add_switch_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_switch_panel.SetSizer(add_switch_panel_hbox)

        self.add_switch_panel_centre = wx.Panel(self.add_switch_panel)
        add_switch_panel_hbox.Add(self.add_switch_panel_centre, 2, wx.EXPAND)

        vbox.Add(self.add_switch_panel, 1, wx.EXPAND)

        # Set sizer of SwitchesPanel
        self.SetSizer(vbox)

    def on_switch_slider_button(self, event):
        """Handle the event when the user clicks the slider for a switch."""
        # Collect all the information for a switch as supplied by the switches dictionary
        selected_switch_panel_id = event.GetEventObject().GetParent().GetId()
        selected_switch_id = self.switch_dict[selected_switch_panel_id][0]
        selected_switch_name = self.switch_dict[selected_switch_panel_id][1]
        selected_switch_state = self.switch_dict[selected_switch_panel_id][2]
        selected_switch_panel = self.switch_dict[selected_switch_panel_id][3]
        selected_switch_panel_sizer = self.switch_dict[selected_switch_panel_id][4]
        selected_switch_state_indicator_panel = self.switch_dict[selected_switch_panel_id][5]
        selected_switch_state_indicator_panel_sizer = self.switch_dict[selected_switch_panel_id][6]

        # Destroy the window holding the current switch slider
        # in preparation for re-adding switch slider to the other side,
        # part of the illusion of the switch slider "sliding" to the side 
        selected_switch_panel_window = selected_switch_panel_sizer.GetItem(0).GetWindow()
        selected_switch_panel_window.Destroy()

        # Destroy the window holding the current switch state indicator
        # in preparation for re-adding the switch state indicator with the new state of the switch
        selected_switch_state_indicator_panel_window = selected_switch_state_indicator_panel_sizer.GetItem(0).GetWindow()
        selected_switch_state_indicator_panel_window.Destroy()

        if selected_switch_state == 0: # switch is currently OFF
            # Change the state of the switch from 0FF --> ON
            selected_switch_state = 1 # switch is now ON
            self.devices.set_switch(selected_switch_id, selected_switch_state)
            self.switch_dict[selected_switch_panel_id][2] = selected_switch_state

            # Add switch slider button for the ON state
            # giving the illusion of the switch slider moving from left to right
            switch_slider_button = wxbuttons.GenButton(parent=selected_switch_panel, id=wx.ID_ANY, label="")
        
            self.Bind(wx.EVT_BUTTON, self.on_switch_slider_button, switch_slider_button)
            switch_slider_button.SetBezelWidth(5)
            switch_slider_button.SetMinSize((45, 30))
            switch_slider_button.SetBackgroundColour(wx.Colour(112, 112, 112))

            # Update the switch panel with the new switch slider position
            selected_switch_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_RIGHT, border=5)
            selected_switch_panel.GetSizer().Layout()
            selected_switch_panel.Refresh()
            selected_switch_panel.Update()

            # Add the switch state indicator for the ON state
            selected_switch_state_indicator_panel.SetBackgroundColour(wx.Colour(4, 84, 14))
            text = wx.StaticText(selected_switch_state_indicator_panel, wx.ID_ANY, _("ON"), style=wx.ALIGN_LEFT)
            text.SetForegroundColour(wx.WHITE)
            selected_switch_state_indicator_panel.SetMinSize((self.text_width, 30))

            # Update the switch state indicator with the ON state
            selected_switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)
            selected_switch_state_indicator_panel.GetSizer().Layout()
            selected_switch_state_indicator_panel.Refresh()
            selected_switch_state_indicator_panel.Update()


        elif selected_switch_state == 1: # switch is currently ON
            # Change the state of the switch from 0N --> OFF
            selected_switch_state = 0 # switch is now OFF
            self.devices.set_switch(selected_switch_id, selected_switch_state)
            self.switch_dict[selected_switch_panel_id][2] = selected_switch_state

            # Add switch slider button for the OFF state
            # giving the illusion of the switch slider moving from right to left
            switch_slider_button = wxbuttons.GenButton(parent=selected_switch_panel, id=wx.ID_ANY, label="")
        
            self.Bind(wx.EVT_BUTTON, self.on_switch_slider_button, switch_slider_button)
            switch_slider_button.SetBezelWidth(5)
            switch_slider_button.SetMinSize((45, 30))
            switch_slider_button.SetBackgroundColour(wx.Colour(112, 112, 112))

            # Update the switch panel with the new switch slider position
            selected_switch_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_LEFT, border=5)
            selected_switch_panel.GetSizer().Layout()
            selected_switch_panel.Refresh()
            selected_switch_panel.Update()

            # Add the switch state indicator for the OFF state
            selected_switch_state_indicator_panel.SetBackgroundColour(wx.Colour(139, 26, 26))
            text = wx.StaticText(selected_switch_state_indicator_panel, wx.ID_ANY, _("OFF"), style=wx.ALIGN_LEFT)
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
            text.SetForegroundColour(wx.WHITE)
            selected_switch_state_indicator_panel.SetMinSize((self.text_width, 30))

            # Update the switch state indicator with the OFF state
            selected_switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)
            selected_switch_state_indicator_panel.GetSizer().Layout()
            selected_switch_state_indicator_panel.Refresh()
            selected_switch_state_indicator_panel.Update()
