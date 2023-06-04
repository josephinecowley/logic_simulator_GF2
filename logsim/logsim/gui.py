"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import os
from io import StringIO
from contextlib import redirect_stdout
from collections import defaultdict

import wx
import wx.lib.scrolledpanel as wxscrolledpanel
import wx.lib.buttons as wxbuttons

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from canvas import MyGLCanvas


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1000, 700))

        # Create instance variables for Gui class
        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
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
        hbox.Add(self.signal_traces_panel, 3, wx.EXPAND, 0)

        # Instantiate RunSimulationPanel widget and add to Frame
        self.simulation_panel = RunSimulationPanel(
            self, self.signal_traces_panel, names, devices, network, monitors)
        vbox.Add(self.simulation_panel, 1, wx.EXPAND)

        # Instantiate SwitchesPanel widget and add to Frame
        self.switches_panel = SwitchesPanel(
            data_panel, self.simulation_panel, names, devices, network, monitors)
        hbox.Add(self.switches_panel, 1, wx.EXPAND, 0)

        self.SetSizeHints(930, 500)
        self.SetSizer(vbox)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Josephine Cowley (jhmdc2), Tom Hill (th621), Khalid Omar (ko366)\n2023",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_quit_button(self, event):
        self.Close()


class RunSimulationPanel(wx.Panel):
    def __init__(self, parent, signal_traces_panel, names, devices, network, monitors, id=wx.ID_ANY, size=wx.DefaultSize):
        super(RunSimulationPanel, self).__init__(
            parent, id, size=size, style=wx.SIMPLE_BORDER)

        self.parent = parent
        self.signal_traces_panel = signal_traces_panel
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        # Configure sizers for layout of RunSimulationPanel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create and set sizer of overall cycles + left buttons panel
        self.cycles_and_left_buttons_panel = wx.Panel(self)
        self.cycles_and_left_buttons_panel.SetSizer(vbox)

        # Create, configure, set and add cycles panel to overall cycles + left buttons panel
        self.cycles_panel = wx.Panel(self.cycles_and_left_buttons_panel)
        cycles_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.cycles_panel.SetSizer(cycles_hbox)
        vbox.Add(self.cycles_panel)

        # Create and add number of cycles text to cycles panel
        str = "No. Cycles"
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
        self.left_buttons_panel = wx.Panel(self.cycles_and_left_buttons_panel)
        left_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.left_buttons_panel.SetSizer(left_buttons_panel_hbox)
        vbox.Add(self.left_buttons_panel)

        # Create, bind running simulation event to and add the "RUN" button to the RUN button panel in left buttons panel
        self.run_button_panel = wx.Panel(self.left_buttons_panel)
        run_buttons_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.run_button_panel.SetSizer(run_buttons_panel_vbox)
        left_buttons_panel_hbox.Add(self.run_button_panel)

        self.run_button = wxbuttons.GenButton(
            self.run_button_panel, wx.ID_ANY, "RUN", name="run button")
        self.Bind(wx.EVT_BUTTON, self.on_run_button, self.run_button)
        self.run_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.run_button.SetBezelWidth(5)
        self.run_button.SetMinSize(wx.DefaultSize)
        self.run_button.SetBackgroundColour(wx.Colour(4, 84, 14))
        self.run_button.SetForegroundColour(wx.WHITE)
        self.run_button.SetToolTip("Begin running the simulation")
        run_buttons_panel_vbox.Add(
            self.run_button, 1, flag=wx.ALIGN_LEFT, border=5)
        
        # Create, bind clearing signal traces event to and add the "CLEAR" button
        self.clear_button = wxbuttons.GenButton(
            self.left_buttons_panel, wx.ID_ANY, "CLEAR", name="clear button")
        self.Bind(wx.EVT_BUTTON, self.on_clear_button, self.clear_button)
        self.clear_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.clear_button.SetBezelWidth(5)
        self.clear_button.SetMinSize(wx.DefaultSize)
        self.clear_button.SetBackgroundColour(wx.Colour(0, 0, 205))
        self.clear_button.SetForegroundColour(wx.WHITE)
        self.clear_button.SetToolTip("Clear all signal traces")
        left_buttons_panel_hbox.Add(
            self.clear_button, 1, flag=wx.ALIGN_LEFT, border=5)
        
        # Create, bind resetting signal traces event to and add the "RESET" button
        self.reset_button = wxbuttons.GenButton(
            self.left_buttons_panel, wx.ID_ANY, "RESET", name="reset button")
        self.Bind(wx.EVT_BUTTON, self.on_reset_button, self.reset_button)
        self.reset_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.reset_button.SetBezelWidth(5)
        self.reset_button.SetMinSize(wx.DefaultSize)
        self.reset_button.SetBackgroundColour(wx.Colour(205, 102, 29))
        self.reset_button.SetForegroundColour(wx.WHITE)
        self.reset_button.SetToolTip("Reset the simulation from initialisation")
        left_buttons_panel_hbox.Add(
            self.reset_button, 1, flag=wx.ALIGN_LEFT, border=5)

        # Create and add cycles + left buttons panel to RunSimulationPanel
        hbox.Add(self.cycles_and_left_buttons_panel, 1, flag=wx.ALIGN_LEFT)

        self.centre_panel = wx.Panel(self)
        centre_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.centre_panel.SetSizer(centre_panel_vbox)
        hbox.Add(self.centre_panel, 2, flag=wx.EXPAND)

        self.centre_panel_top_padding = wx.Panel(self.centre_panel)
        centre_panel_vbox.Add(self.centre_panel_top_padding, 1, flag=wx.EXPAND)

        self.centre_panel_bottom_padding = wx.Panel(self.centre_panel)
        centre_panel_bottom_padding_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.centre_panel_bottom_padding.SetSizer(centre_panel_bottom_padding_hbox)
        centre_panel_vbox.Add(self.centre_panel_bottom_padding, 2, flag=wx.EXPAND)

        self.centre_panel_bottom_padding_left = wx.Panel(self.centre_panel_bottom_padding)
        centre_panel_bottom_padding_hbox.Add(self.centre_panel_bottom_padding_left, 1, flag=wx.EXPAND)

        self.centre_panel_bottom_padding_centre = wx.Panel(self.centre_panel_bottom_padding)
        centre_panel_bottom_padding_hbox.Add(self.centre_panel_bottom_padding_centre, 2, flag=wx.EXPAND)

        self.centre_panel_bottom_padding_right = wx.Panel(self.centre_panel_bottom_padding)
        centre_panel_bottom_padding_right_vbox = wx.BoxSizer(wx.VERTICAL)
        self.centre_panel_bottom_padding_right.SetSizer(centre_panel_bottom_padding_right_vbox)
        centre_panel_bottom_padding_hbox.Add(self.centre_panel_bottom_padding_right, 1, flag=wx.EXPAND)

        # Create, bind quitting event to and add the "Quit simulation" button
        self.quit_button = wxbuttons.GenButton(
            self.centre_panel_bottom_padding_right, wx.ID_ANY, "QUIT", name="quit button")
        self.Bind(wx.EVT_BUTTON, parent.on_quit_button, self.quit_button)
        self.quit_button.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.quit_button.SetBezelWidth(5)
        self.quit_button.SetMinSize(wx.DefaultSize)
        self.quit_button.SetBackgroundColour(wx.Colour(139, 26, 26))
        self.quit_button.SetForegroundColour(wx.WHITE)
        self.quit_button.SetToolTip("Quit the simulation")
        centre_panel_bottom_padding_right_vbox.Add(
            self.quit_button, 1, flag=wx.ALIGN_RIGHT, border=5)

        self.upload_and_help_buttons_panel = wx.Panel(
            self, name="upload and help buttons panel")
        upload_and_help_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.upload_and_help_buttons_panel.SetSizer(
            upload_and_help_buttons_panel_hbox)

        self.upload_button_panel = wx.Panel(
            self.upload_and_help_buttons_panel, name="upload button panel")
        #self.upload_and_help_buttons_panel.SetSizeHints(100, 100)
        upload_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.upload_button_panel.SetSizer(upload_button_panel_vbox)
        #self.upload_and_help_buttons_panel.SetSizerAndFit(upload_button_panel_vbox)

        self.upload_button = wx.Button(
            self.upload_button_panel, wx.ID_ANY, "UPLOAD")
        self.Bind(wx.EVT_BUTTON, self.on_upload_button, self.upload_button)
        self.upload_button.SetToolTip("Upload logic description file")
        upload_button_panel_vbox.Add(
            self.upload_button, 1, flag=wx.ALIGN_CENTER)

        self.help_button_panel = wx.Panel(
            self.upload_and_help_buttons_panel, name="help button panel")
        help_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.help_button_panel.SetSizer(help_button_panel_vbox)

        self.help_button = wx.Button(self.help_button_panel, wx.ID_ANY, "HELP")
        self.Bind(wx.EVT_BUTTON, self.on_help_button, self.help_button)
        self.help_button.SetToolTip("Help on running logic simulation")
        help_button_panel_vbox.Add(self.help_button, 1, flag=wx.ALIGN_CENTER)

        upload_and_help_buttons_panel_hbox.Add(
            self.upload_button_panel, 1, flag=wx.EXPAND)
        upload_and_help_buttons_panel_hbox.Add(
            self.help_button_panel, 1, flag=wx.EXPAND)

        hbox.Add(self.upload_and_help_buttons_panel, 1, flag=wx.EXPAND)

        # Set sizer of RunSimulationPanel
        self.SetSizer(hbox)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        run_button_pressed = event.GetEventObject()
        text = f"{run_button_pressed.GetLabel()} simulation button pressed."
        run_button_pressed.SetLabel("CONTINUE")
        run_button_pressed.SetBackgroundColour(wx.Colour(181, 150, 27))
        run_button_pressed.SetToolTip("Continue running the simulation")
        self.GetSizer().Layout()

        no_of_cycles = self.cycles_spin_control.GetValue()
        self.run_network(no_of_cycles)
        self.update_canvas()

    def on_clear_button(self, event):
        self.parent.signal_traces_panel.canvas.clear_traces()


    def on_reset_button(self, event):
        file_path = self.parent.path
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)#
        parser.parse_network()

        new_Gui = Gui("GF2 Team 7 Logic Simulator GUI",
                              file_path,
                              names,
                              devices,
                              network,
                              monitors)
        new_Gui.Show()
        self.parent.Close()

    def run_network(self, cycles):
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True

    def update_canvas(self):
        self.signal_traces_panel.canvas.update_arguments(
            self.devices, self.monitors)

    def on_spin(self, event):
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
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(file_path, names)
            parser = Parser(names, devices, network, monitors, scanner)

            captured_print = StringIO()
            with redirect_stdout(captured_print):
                parsing_result = parser.parse_network()

            output = captured_print.getvalue()

            if parsing_result:
                new_Gui = Gui("GF2 Team 7 Logic Simulator GUI",
                              file_path,
                              names,
                              devices,
                              network,
                              monitors)
                new_Gui.Show()
                self.parent.Close()
            else:
                dlg = wx.MessageDialog(self, output,
                                       "An error occurred.",
                                       wx.OK | wx.ICON_INFORMATION
                                       # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                       )
                dlg.ShowModal()
                dlg.Destroy()

        dlg.Destroy()

    def on_help_button(self, event):
        help_dialog_file_path = "logsim/logsim/help_dialog.txt"
        with open(help_dialog_file_path, "r", encoding="utf8") as help_dialog_file:
            help_dialog_text = "".join(help_dialog_file.readlines())
        dlg = wx.MessageDialog(self, help_dialog_text,
                               "Tutorial on GF2 Team 7 Logic Simulator",
                               wx.OK | wx.ICON_INFORMATION
                               # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()


class SignalTrace(wx.ScrolledWindow):
    def __init__(self, parent, names, devices, network, monitors, id=wx.ID_ANY, size=wx.DefaultSize):
        super(SignalTrace, self).__init__(parent, id, size=size)

        size = self.GetClientSize()

        # Useful variables for ScrolledWindow
        self.lines = []
        self.maxWidth = size.width * 2
        self.maxHeight = size.height
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        # Set settings for ScrolledWindow
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20, 20)


class SignalTracesPanel(wx.Panel):
    def __init__(self, parent, names, devices, network, monitors):
        super(SignalTracesPanel, self).__init__(
            parent, size=wx.DefaultSize, style=wx.BORDER_SUNKEN)

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        # Configure sizers for layout of SwitchesPanel panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.signal_traces_panel = wx.Panel(self, name="signal traces panel")
        signal_traces_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.signal_traces_panel.SetSizer(signal_traces_panel_vbox)

        self.add_new_monitor_panel = wx.Panel(
            self, name="add new monitor panel")
        add_new_monitor_panel_fgs = wx.FlexGridSizer(
            cols=3, rows=3, vgap=4, hgap=50)
        self.add_new_monitor_panel.SetSizer(add_new_monitor_panel_fgs)

        # Create and add "Add new monitor" text to add new monitor panel
        str = "Add new monitor"
        text = wx.StaticText(self.add_new_monitor_panel, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_fgs.Add(text, 0, flag=wx.ALIGN_CENTER)

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
        self.select_monitor_combo_box = wx.ComboBox(self.add_new_monitor_panel, wx.ID_ANY, "Select output", (90, 50),
                                                    (160, -1), self.monitor_output_list,
                                                    wx.CB_DROPDOWN
                                                    # | wx.TE_PROCESS_ENTER
                                                    # | wx.CB_SORT
                                                    )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_new_monitor,
                  self.select_monitor_combo_box)
        add_new_monitor_panel_fgs.Add(
            self.select_monitor_combo_box, 0, flag=wx.ALIGN_CENTER | wx.LEFT, border=30)

        # Create and add the "Add a new monitor" button to show the newly monitored device's signal trace on SignalTraces panel
        self.add_new_monitor_button = wx.Button(
            self.add_new_monitor_panel, wx.ID_ANY, label="+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_monitor_button,
                  self.add_new_monitor_button)
        self.add_new_monitor_button.SetToolTip("Add monitor")
        add_new_monitor_panel_fgs.Add(
            self.add_new_monitor_button, 1, flag=wx.CENTER | wx.EXPAND)

        # Create and add "Zap a monitor" text to add new monitor panel
        str = "Delete monitor"
        text = wx.StaticText(self.add_new_monitor_panel, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_fgs.Add(text, 0, flag=wx.ALIGN_CENTER)

        # Create and add the dropdown menu for the currently monitored devices, ready to be zapped
        self.selected_signal_to_zap = None
        self.monitor_output_list = self.monitored_devices_names
        self.zap_monitor_combo_box = wx.ComboBox(self.add_new_monitor_panel, wx.ID_ANY, "Select output", (90, 50),
                                                 (160, -1), self.monitor_output_list,
                                                 wx.CB_DROPDOWN
                                                 # | wx.TE_PROCESS_ENTER
                                                 # | wx.CB_SORT
                                                 )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_zap_monitor,
                  self.zap_monitor_combo_box)
        add_new_monitor_panel_fgs.Add(
            self.zap_monitor_combo_box, 0, flag=wx.ALIGN_CENTER | wx.LEFT, border=30)

        # Create and add the "Zap an existing monitor" button to remove a currently monitored device's signal trace on SignalTraces panel
        self.zap_existing_monitor_button = wx.Button(
            self.add_new_monitor_panel, wx.ID_ANY, label="-")
        self.Bind(wx.EVT_BUTTON, self.on_zap_existing_monitor,
                  self.zap_existing_monitor_button)
        self.zap_existing_monitor_button.SetToolTip("Zap an existing monitor")
        add_new_monitor_panel_fgs.Add(
            self.zap_existing_monitor_button, 1, flag=wx.CENTER | wx.EXPAND)

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

    def update_canvas(self):
        self.canvas.update_arguments(self.devices, self.monitors)


class SwitchesPanel(wx.Panel):
    def __init__(self, parent, simulation_panel, names, devices, network, monitors):
        super(SwitchesPanel, self).__init__(parent, size=(300, 200))

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        self.simulation_panel = simulation_panel

        # Configure sizers for layout of SwitchesPanel panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create and add the title to SwitchesPanel panel
        str = "INPUTS"
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

        self.switch_dict = defaultdict(list)
        for switch_name in switch_names:
            switch_id = self.names.query(switch_name)
            initial_switch_state = devices.get_device(switch_id).switch_state
            
            switch_name_text = wx.StaticText(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"{switch_name}", style=wx.ALIGN_LEFT)
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
            switch_name_text.SetFont(font)

            switch_slider_panel = wx.Panel(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, style=wx.BORDER_SUNKEN, size=(90, 30))
            switch_slider_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            switch_slider_panel.SetSizer(switch_slider_panel_sizer)

            switch_slider_button = wxbuttons.GenButton(parent=switch_slider_panel, id=wx.ID_ANY, label="", name="switch slider")
            switch_slider_id = switch_slider_panel.GetId()
        
            self.Bind(wx.EVT_BUTTON, self.on_switch_slider_button, switch_slider_button)
            switch_slider_button.SetBezelWidth(5)
            switch_slider_button.SetMinSize((45, 30))
            switch_slider_button.SetBackgroundColour(wx.Colour(112, 112, 112))
        
            if initial_switch_state == 1:
                switch_slider_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_RIGHT, border=5)
            elif initial_switch_state == 0:
                switch_slider_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_LEFT, border=5)

            switch_state_indicator_panel = wx.Panel(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, style=wx.BORDER_RAISED, size=(50, 30))
            switch_state_indicator_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            switch_state_indicator_panel.SetSizer(switch_state_indicator_panel_sizer)

            if initial_switch_state == 1:
                switch_state_indicator_panel.SetBackgroundColour(wx.Colour(4, 84, 14))
                text = wx.StaticText(switch_state_indicator_panel, wx.ID_ANY, "ON", style=wx.ALIGN_LEFT)
                font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
                text.SetFont(font)
                text.SetForegroundColour(wx.WHITE)
                switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)
            elif initial_switch_state == 0:
                switch_state_indicator_panel.SetBackgroundColour(wx.Colour(139, 26, 26))
                text = wx.StaticText(switch_state_indicator_panel, wx.ID_ANY, "OFF", style=wx.ALIGN_LEFT)
                font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
                text.SetFont(font)
                text.SetForegroundColour(wx.WHITE)
                switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)

            self.switch_dict[switch_slider_id].extend([switch_id, switch_name, initial_switch_state, switch_slider_panel, switch_slider_panel_sizer, switch_state_indicator_panel, switch_state_indicator_panel_sizer])

            # add switch toggle buttons to ScrolledPanel
            self.fgs.Add(switch_name_text, 0, flag=wx.ALL, border=12)
            self.fgs.Add(switch_slider_panel, 2, flag=wx.ALL, border=10)
            self.fgs.Add(switch_state_indicator_panel, 1, flag=wx.ALL, border=10)

        # Set sizer of ScrolledPanel
        self.switch_buttons_scrolled_panel.SetSizer(self.fgs)
        self.switch_buttons_scrolled_panel.SetAutoLayout(1)
        self.switch_buttons_scrolled_panel.SetupScrolling(
            scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        # Create and add left panel in switches panel layout
        self.left_panel = wx.Panel(self.switches_panel)
        # self.test_button = wx.Button(self.left_panel, wx.ID_ANY, "Temp \nbutton \nlocation \nfor \nadd \nnew \ndevice", (50,50))
        # self.Bind(wx.EVT_BUTTON, self.on_test_button, self.test_button)
        left_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.left_panel.SetSizer(left_panel_vbox)
        # left_panel_vbox.Add(self.test_button, 1, flag=wx.EXPAND)
        # left_panel_vbox.Add(self.add_new_switch_button, 1, flag=wx.EXPAND)
        #hbox.Add(self.left_panel, 1, wx.EXPAND)

        # Add the ScrolledPanel widget to SwitchesPanel panel
        hbox.Add(self.switch_buttons_scrolled_panel, 3, wx.EXPAND)

        # Create and add right panel in switches panel layout
        self.right_panel = wx.Panel(self.switches_panel)
        #hbox.Add(self.right_panel, 1, wx.EXPAND)

        self.add_switch_panel = wx.Panel(self)
        add_switch_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_switch_panel.SetSizer(add_switch_panel_hbox)

        self.add_switch_panel_left = wx.Panel(self.add_switch_panel)
        add_switch_panel_hbox.Add(self.add_switch_panel_left, 1, wx.EXPAND)

        self.add_switch_panel_centre = wx.Panel(self.add_switch_panel)
        add_switch_panel_centre_vbox = wx.BoxSizer(wx.VERTICAL)
        add_switch_panel_hbox.Add(self.add_switch_panel_centre, 2, wx.EXPAND)

        self.add_switch_panel_right = wx.Panel(self.add_switch_panel)
        add_switch_panel_hbox.Add(self.add_switch_panel_right, 1, wx.EXPAND)

        vbox.Add(self.add_switch_panel, 1, wx.EXPAND)

        # Set sizer of SwitchesPanel
        self.SetSizer(vbox)

    def on_test_button(self, event):
        AddDeviceDialog(self, "Add a new device", self, self.names,
                        self.devices, self.network, self.monitors).ShowModal()

    def on_switch_toggle_button(self, event):
        """Handle the event when the user clicks the toggle button for a switch."""
        switch_selected = event.GetEventObject()
        switch_id = self.names.query(switch_selected.GetLabel())
        switch_state = switch_selected.GetValue()
        # successfully switched the state of switch
        if self.devices.set_switch(switch_id, int(switch_state)):
            pass

    def on_switch_slider_button(self, event):
        selected_switch_panel_id = event.GetEventObject().GetParent().GetId()
        selected_switch_id = self.switch_dict[selected_switch_panel_id][0]
        selected_switch_name = self.switch_dict[selected_switch_panel_id][1]
        selected_switch_state = self.switch_dict[selected_switch_panel_id][2]
        selected_switch_panel = self.switch_dict[selected_switch_panel_id][3]
        selected_switch_panel_sizer = self.switch_dict[selected_switch_panel_id][4]
        selected_switch_state_indicator_panel = self.switch_dict[selected_switch_panel_id][5]
        selected_switch_state_indicator_panel_sizer = self.switch_dict[selected_switch_panel_id][6]

        print(f'original: {selected_switch_state}')

        selected_switch_panel_window = selected_switch_panel_sizer.GetItem(0).GetWindow()
        selected_switch_panel_window.Destroy()

        selected_switch_state_indicator_panel_window = selected_switch_state_indicator_panel_sizer.GetItem(0).GetWindow()
        selected_switch_state_indicator_panel_window.Destroy()

        if selected_switch_state == 0: # switch is currently OFF
            selected_switch_state = 1 # switch is now ON
            self.devices.set_switch(selected_switch_id, selected_switch_state)
            self.switch_dict[selected_switch_panel_id][2] = selected_switch_state

            switch_slider_button = wxbuttons.GenButton(parent=selected_switch_panel, id=wx.ID_ANY, label="")
        
            self.Bind(wx.EVT_BUTTON, self.on_switch_slider_button, switch_slider_button)
            switch_slider_button.SetBezelWidth(5)
            switch_slider_button.SetMinSize((45, 30))
            switch_slider_button.SetBackgroundColour(wx.Colour(112, 112, 112))

            selected_switch_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_RIGHT, border=5)
            selected_switch_panel.GetSizer().Layout()
            selected_switch_panel.Refresh()
            selected_switch_panel.Update()

            selected_switch_state_indicator_panel.SetBackgroundColour(wx.Colour(4, 84, 14))
            text = wx.StaticText(parent=selected_switch_state_indicator_panel, id=wx.ID_ANY, label="ON", style=wx.ALIGN_LEFT)
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
            text.SetFont(font)
            text.SetForegroundColour(wx.WHITE)

            selected_switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)
            selected_switch_state_indicator_panel.GetSizer().Layout()
            selected_switch_state_indicator_panel.Refresh()
            selected_switch_state_indicator_panel.Update()


        elif selected_switch_state == 1: # switch is currently ON
            selected_switch_state = 0 # switch is now OFF
            self.devices.set_switch(selected_switch_id, selected_switch_state)
            self.switch_dict[selected_switch_panel_id][2] = selected_switch_state

            switch_slider_button = wxbuttons.GenButton(parent=selected_switch_panel, id=wx.ID_ANY, label="")
        
            self.Bind(wx.EVT_BUTTON, self.on_switch_slider_button, switch_slider_button)
            switch_slider_button.SetBezelWidth(5)
            switch_slider_button.SetMinSize((45, 30))
            switch_slider_button.SetBackgroundColour(wx.Colour(112, 112, 112))

            selected_switch_panel_sizer.Add(switch_slider_button, 0, flag=wx.ALIGN_LEFT, border=5)
            selected_switch_panel.GetSizer().Layout()
            selected_switch_panel.Refresh()
            selected_switch_panel.Update()

            selected_switch_state_indicator_panel.SetBackgroundColour(wx.Colour(139, 26, 26))
            text = wx.StaticText(parent=selected_switch_state_indicator_panel, id=wx.ID_ANY, label="OFF", style=wx.ALIGN_LEFT)
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
            text.SetFont(font)
            text.SetForegroundColour(wx.WHITE)

            selected_switch_state_indicator_panel_sizer.Add(text, 0, flag=wx.CENTER)
            selected_switch_state_indicator_panel.GetSizer().Layout()
            selected_switch_state_indicator_panel.Refresh()
            selected_switch_state_indicator_panel.Update()


    def on_change_right_panel_colour(self, event):
        self.right_panel.SetBackgroundColour("GREEN")
        self.right_panel.Layout()
        self.right_panel.Refresh()
        self.right_panel.Update()


class AddDeviceDialog(wx.Dialog):
    def __init__(self, parent, title, switches_panel, names, devices, network, monitors):
        super(AddDeviceDialog, self).__init__(
            parent, title=title, size=(250, 150))

        self.switches_panel = switches_panel
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        vbox = wx.BoxSizer(wx.VERTICAL)

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        panel = wx.Panel(self, wx.ID_ANY)

        # Configure sizer for devices panel
        vbox = wx.BoxSizer(wx.VERTICAL)

        devices_panel = wx.StaticBox(panel, wx.ID_ANY, "Select a device")
        devices_sizer = wx.StaticBoxSizer(devices_panel, wx.VERTICAL)
        devices_grid = wx.FlexGridSizer(cols=4)

        self.switch_user_name = None
        self.clock_user_name = None
        self.gate_user_name = None

        self.switch_device_property = None
        self.clock_device_property = None
        self.gate_device_property = None

        self.add_new_device_ctrls = []

        switch_radio_button = wx.RadioButton(
            panel, wx.ID_ANY, "Switch", style=wx.RB_GROUP)
        add_new_switch_button = wx.Button(panel, wx.ID_ANY, "+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_switch_button,
                  add_new_switch_button)
        switch_device_property_panel = wx.Panel(panel, size=(60, 20))
        switch_device_property_panel_fgs = wx.FlexGridSizer(cols=2)
        switch_device_property_panel.SetSizer(switch_device_property_panel_fgs)
        switch_states = [wx.RadioButton(switch_device_property_panel, wx.ID_ANY, "1"),
                         wx.RadioButton(switch_device_property_panel, wx.ID_ANY, "0")]
        for switch_state in switch_states:
            switch_device_property_panel_fgs.Add(
                switch_state, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
            self.Bind(wx.EVT_RADIOBUTTON,
                      self.on_select_switch_device_property, switch_state)

        clock_radio_button = wx.RadioButton(panel, wx.ID_ANY, "Clock")
        add_new_clock_button = wx.Button(panel, wx.ID_ANY, "+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_clock_button,
                  add_new_clock_button)
        clock_device_property_panel = wx.Panel(panel, size=(70, 20))
        clock_device_property_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        clock_device_property_panel.SetSizer(clock_device_property_panel_vbox)
        clock_device_property_txtctrl = wx.TextCtrl(
            clock_device_property_panel, wx.ID_ANY, "")
        clock_device_property_txtctrl.Bind(
            wx.EVT_TEXT, self.on_type_clock_device_property)
        clock_device_property_panel_vbox.Add(
            clock_device_property_txtctrl, 1, flag=wx.EXPAND)

        gate_radio_button = wx.RadioButton(panel, wx.ID_ANY, "Gate")
        add_new_gate_button = wx.Button(panel, wx.ID_ANY, "+")
        gate_device_property_panel = wx.Panel(panel, size=(60, 20))
        gate_device_property_panel.SetBackgroundColour('BLUE')

        switch_user_name = wx.TextCtrl(panel, wx.ID_ANY, "Switch name")
        wx.CallAfter(switch_user_name.SetInsertionPoint, 0)
        self.switch_user_name_txtctrl = switch_user_name
        switch_user_name.Bind(wx.EVT_TEXT, self.on_switch_name_entry)

        clock_user_name = wx.TextCtrl(panel, wx.ID_ANY, "Clock name")
        wx.CallAfter(clock_user_name.SetInsertionPoint, 0)
        self.clock_user_name_txtctrl = clock_user_name
        clock_user_name.Bind(wx.EVT_TEXT, self.on_clock_name_entry)

        gate_user_name = wx.TextCtrl(panel, wx.ID_ANY, "Gate name")
        wx.CallAfter(gate_user_name.SetInsertionPoint, 0)
        self.gate_user_name_txtctrl = gate_user_name
        gate_user_name.Bind(wx.EVT_TEXT, self.on_gate_name_entry)

        self.add_new_device_ctrls.append(
            (switch_radio_button, switch_user_name, add_new_switch_button, switch_device_property_panel))
        self.add_new_device_ctrls.append(
            (clock_radio_button, clock_user_name, add_new_clock_button, clock_device_property_panel))
        self.add_new_device_ctrls.append(
            (gate_radio_button, gate_user_name, add_new_gate_button, gate_device_property_panel))

        for radio, text, add_button, device_property in self.add_new_device_ctrls:
            devices_grid.Add(radio, 0, wx.ALIGN_CENTRE |
                             wx.LEFT | wx.RIGHT | wx.TOP, 5)
            devices_grid.Add(text, 0, wx.ALIGN_CENTRE |
                             wx.LEFT | wx.RIGHT | wx.TOP, 5)
            devices_grid.Add(device_property, 0, wx.ALIGN_CENTRE |
                             wx.LEFT | wx.RIGHT | wx.TOP, 5)
            devices_grid.Add(add_button, 0, wx.ALIGN_CENTRE |
                             wx.LEFT | wx.RIGHT | wx.TOP, 5)

        devices_sizer.Add(devices_grid, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        vbox.Add(devices_sizer, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        panel.SetSizer(vbox)
        vbox.Fit(panel)
        panel.Move((50, 50))
        self.panel = panel

    def on_switch_name_entry(self, event):
        switch_user_name = event.GetString()
        self.switch_user_name = switch_user_name

    def on_clock_name_entry(self, event):
        clock_user_name = event.GetString()
        self.clock_user_name = clock_user_name

    def on_gate_name_entry(self, event):
        gate_user_name = event.GetString()
        self.gate_user_name = gate_user_name

    def on_select_switch_device_property(self, event):
        switch_state_selected = event.GetEventObject().GetLabel()
        self.switch_device_property = switch_state_selected

    def on_type_clock_device_property(self, event):
        clock_period_typed = event.GetString()
        if clock_period_typed.isnumeric():
            if clock_period_typed.isdigit():
                if int(clock_period_typed) > 0:
                    self.clock_device_property = int(clock_period_typed)

    def on_add_new_clock_button(self, event):
        if self.clock_user_name is not None:  # confirm if user-defined device name has been entered
            valid_name = self.clock_user_name
            print(f'Clock name: {valid_name}')
            # confirm if user-defined name is unique and not already defined
            if self.names.query(valid_name) is None:
                print('Unique clock!')
                unique_device_id = self.names.lookup([valid_name])[0]
                # confirm if a clock period (clock device property) has been written (correctly)
                if self.clock_device_property is not None:
                    clock_period = self.clock_device_property
                    if self.devices.make_device(unique_device_id, self.devices.CLOCK, clock_period) == self.devices.NO_ERROR:
                        print(
                            f'Clock half period: {self.devices.get_device(unique_device_id).clock_half_period}')
                        print(
                            f'Clock counter: {self.devices.get_device(unique_device_id).clock_counter}')

    def on_add_new_switch_button(self, event):
        if self.switch_user_name is not None:  # confirm if user-defined device name has been entered
            valid_name = self.switch_user_name
            old_switch_ids = self.devices.find_devices(
                device_kind=self.devices.SWITCH)
            old_switch_names = [self.names.get_name_string(
                i) for i in old_switch_ids]
            print(old_switch_names)
            print(f'Switch name: {valid_name}')
            # confirm if user-defined name is unique and not already defined
            if self.names.query(valid_name) is None:
                print('Unique switch!')
                unique_device_id = self.names.lookup([valid_name])[0]
                # confirm if a switch state (switch device property) has been selected
                if self.switch_device_property is not None:
                    switch_state = int(self.switch_device_property)
                    if self.devices.make_device(unique_device_id, self.devices.SWITCH, switch_state) == self.devices.NO_ERROR:
                        print(
                            f'Switch state: {self.devices.get_device(unique_device_id).switch_state}')
                        self.update_switches_panel(valid_name)

    def update_switches_panel(self, switch_name):
        self.switches_panel.num_of_switches += 1
        new_switch = wx.ToggleButton(
            parent=self.switches_panel.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"{switch_name}")
        new_switch_id = self.names.query(switch_name)
        new_switch_state = self.devices.get_device(new_switch_id).switch_state
        new_switch.SetValue(bool(new_switch_state))
        self.switches_panel.fgs.SetRows(
            self.switches_panel.num_of_switches + 1)
        self.switches_panel.Bind(
            wx.EVT_TOGGLEBUTTON, self.switches_panel.on_switch_toggle_button, new_switch)
        self.switches_panel.fgs.Add(new_switch, 1, flag=wx.ALL, border=10)
        self.switches_panel.switch_buttons_scrolled_panel.Refresh()
        self.switches_panel.Layout()


class LogicSimApp(wx.App):
    def OnInit(self):
        file_path = "logsim\logsim\example2_logic_description.txt"
        with open(file_path) as f:
            print('success')
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
        self.frame = Gui(f"GF2 Team 7 Logic Simulator GUI: {file_path}",
                         file_path,
                         names,
                         devices,
                         network,
                         monitors)
        self.frame.Show()

        return True


# KO! For development purposes only - will delete once complete
if __name__ == "__main__":
    app = LogicSimApp()
    app.MainLoop()
