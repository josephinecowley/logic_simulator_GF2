"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import os

import wx
import wx.glcanvas as wxcanvas
import wx.lib.scrolledpanel as wxscrolledpanel
import wx.lib.buttons as wxbuttons
import wx.lib.agw.aquabutton as wxaquabutton
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Initialise trace objects
        self.traces = monitors.get_signals_for_GUI()
        self.y_spacing = 80

        self.devices = devices

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def draw_canvas(self):
        """Iterates through each trace and draws it on the canvas with an offset"""
        x_offset = 100
        y_offset = 420
        color_list = [
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (1.0, 0.0, 1.0),
            (0.0, 1.0, 1.0),
        ]
        for i, trace in enumerate(self.traces):
            signal = trace[1]
            label = trace[0]
            color = color_list[i % len(color_list)]
            self._draw_trace(signal, x_offset, y_offset, label, color)
            y_offset -= self.y_spacing

    def _draw_trace(self, signal, x_pos, y_pos, label, color=(0.0, 0.0, 1.0)):
        """Draws trace with axes and ticks"""

        # draw trace
        GL.glLineWidth(3.0)
        GL.glColor3f(*color)
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(signal)):
            x = (i * 20) + x_pos
            x_next = (i * 20) + x_pos + 20
            if signal[i] == 0:
                y = y_pos
            else:
                y = y_pos + 25
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # draw axis
        y_pos -= 10
        GL.glColor3f(0.0, 0.0, 0.0)  # black
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(x_pos, y_pos)
        GL.glVertex2f(x_pos, y_pos + 40)
        GL.glVertex2f(x_pos, y_pos)
        GL.glVertex2f(x_pos + (len(signal) * 20), y_pos)
        GL.glEnd()

        # draw axis ticks
        for i in range(len(signal) + 1):
            x = (i * 20) + x_pos
            GL.glColor3f(0.0, 0.0, 0.0)  # black
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(x_pos, y_pos)
            GL.glVertex2f(x_pos, y_pos - 4)
            GL.glEnd()
            self.render_text(str(i), x - 5, y_pos - 15)

        x_pos -= int(20 / 3 * len(label))
        self.render_text(label, x_pos, y_pos + 18)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw signal traces
        self.draw_canvas()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = " "
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = " "
        if event.ButtonUp():
            text = " "
        if event.Leaving():
            text = " "
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = " "
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = " "
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = " "
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_18

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def update_arguments(self, devices, monitors):
        # Update the devices and monitors with new arguments
        self.devices = devices
        self.monitors = monitors
        self.traces = self.monitors.get_signals_for_GUI()
        #print(f'THIRD: {self.traces}')

        # Trigger a redraw
        self.Refresh()


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
        signal_traces_panel = SignalTracesPanel(data_panel, names, devices, network, monitors)
        hbox.Add(signal_traces_panel, 3, wx.EXPAND, 0)

        # Instantiate RunSimulationPanel widget and add to Frame
        simulation_panel = RunSimulationPanel(self, signal_traces_panel, names, devices, network, monitors)
        vbox.Add(simulation_panel, 1, wx.EXPAND)

        # Instantiate SwitchesPanel widget and add to Frame
        switches_panel = SwitchesPanel(data_panel, simulation_panel, names, devices, network, monitors)
        hbox.Add(switches_panel, 1, wx.EXPAND, 0)


        self.SetSizeHints(200, 200)
        self.SetSizer(vbox)


    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Josephine Cowley (jhmdc2), Tom Hill (th621), Khalid Omar (ko366)\n2023",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)


class RunSimulationPanel(wx.Panel):
    def __init__(self, parent, signal_traces_panel, names, devices, network, monitors, id=wx.ID_ANY, size=wx.DefaultSize):
        super(RunSimulationPanel, self).__init__(parent, id, size=size, style=wx.SIMPLE_BORDER)

        self.signal_traces_panel = signal_traces_panel
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        #self.SetBackgroundColour("RED") # layout identifier colour for visualisation purposes
        #print(self.GetLabel())

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

        # Create, configure, set and add left buttons panel to overall cycles + left buttons panel
        self.left_buttons_panel = wx.Panel(self.cycles_and_left_buttons_panel)
        left_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.left_buttons_panel.SetSizer(left_buttons_panel_hbox)
        vbox.Add(self.left_buttons_panel)
        
        # Create and add number of cycles text to cycles panel
        str = "No. Cycles"
        text = wx.StaticText(self.cycles_panel, wx.ID_ANY, str, style=wx.ALIGN_LEFT)
        font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        cycles_hbox.Add(text, 0, flag=wx.TOP|wx.LEFT)
        cycles_spin_control = wx.SpinCtrl(self.cycles_panel, -1, "", (30, 50))
        cycles_spin_control.SetRange(1,100)
        cycles_spin_control.SetValue(5)
        self.cycles_spin_control = cycles_spin_control
        self.Bind(wx.EVT_SPINCTRL, self.on_spin, self.cycles_spin_control)
        cycles_hbox.Add(self.cycles_spin_control, 0, flag=wx.LEFT, border=10)


        # Create, bind running simulation event to and add the "Run simulation" button
        self.run_button = wxbuttons.GenButton(self.left_buttons_panel, wx.ID_ANY, "RUN", name="run button")
        self.Bind(wx.EVT_BUTTON, self.on_run_button, self.run_button)
        self.run_button.SetFont(wx.Font(20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.run_button.SetBezelWidth(5)
        self.run_button.SetMinSize(wx.DefaultSize)
        self.run_button.SetBackgroundColour(wx.Colour(4, 84, 14))
        self.run_button.SetForegroundColour(wx.WHITE)
        self.run_button.SetToolTip("Begin running the simulation")
        left_buttons_panel_hbox.Add(self.run_button, 1, flag=wx.ALIGN_LEFT, border=5)

        # Create, bind quitting event to and add the "Quit simulation" button
        self.quit_button = wxbuttons.GenButton(self.left_buttons_panel, wx.ID_ANY, "QUIT", name="quit button")
        self.Bind(wx.EVT_BUTTON, self.on_quit_button, self.quit_button)
        self.quit_button.SetFont(wx.Font(20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        self.quit_button.SetBezelWidth(5)
        self.quit_button.SetMinSize(wx.DefaultSize)
        self.quit_button.SetBackgroundColour(wx.Colour(139, 26, 26))
        self.quit_button.SetForegroundColour(wx.WHITE)
        self.quit_button.SetToolTip("Quit the simulation")
        left_buttons_panel_hbox.Add(self.quit_button, 1, flag=wx.ALIGN_LEFT, border=5)

        # Create and add cycles + left buttons panel to RunSimulationPanel
        hbox.Add(self.cycles_and_left_buttons_panel, 1, flag=wx.ALIGN_LEFT)

        
        self.centre_panel = wx.Panel(self)
        #self.centre_panel.SetBackgroundColour("GREEN") # layout identifier colour for visualisation purposes
        centre_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.centre_panel, 2, flag=wx.EXPAND)

        
        self.upload_and_help_buttons_panel = wx.Panel(self, name="upload and help buttons panel")
        #upload_and_help_buttons_panel.SetBackgroundColour("CYAN") # layout identifier colour for visualisation purposes
        upload_and_help_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.upload_and_help_buttons_panel.SetSizer(upload_and_help_buttons_panel_hbox)

        self.upload_button_panel = wx.Panel(self.upload_and_help_buttons_panel, name="upload button panel")
        #upload_button_panel.SetBackgroundColour("RED") # layout identifier colour for visualisation purposes
        upload_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.upload_button_panel.SetSizer(upload_button_panel_vbox)

        self.upload_button = wx.Button(self.upload_button_panel, wx.ID_ANY, "UPLOAD")
        self.Bind(wx.EVT_BUTTON, self.on_upload_button, self.upload_button)
        self.upload_button.SetToolTip("Upload logic description file")
        upload_button_panel_vbox.Add(self.upload_button, 1, flag=wx.ALIGN_CENTER)


        self.help_button_panel = wx.Panel(self.upload_and_help_buttons_panel, name="help button panel")
        #help_button_panel.SetBackgroundColour("BLUE") # layout identifier colour for visualisation purposes
        help_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.help_button_panel.SetSizer(help_button_panel_vbox)

        self.help_button = wx.Button(self.help_button_panel, wx.ID_ANY, "HELP")
        self.help_button.SetToolTip("Help on running logic simulation")
        help_button_panel_vbox.Add(self.help_button, 1, flag=wx.ALIGN_CENTER)

        upload_and_help_buttons_panel_hbox.Add(self.upload_button_panel, 1, flag=wx.EXPAND)
        upload_and_help_buttons_panel_hbox.Add(self.help_button_panel, 1, flag=wx.EXPAND)

        hbox.Add(self.upload_and_help_buttons_panel, 1, flag=wx.EXPAND)
        
        # Set sizer of RunSimulationPanel
        self.SetSizer(hbox)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        run_button_pressed = event.GetEventObject()
        text = f"{run_button_pressed.GetLabel()} simulation button pressed."
        print(text)
        run_button_pressed.SetLabel("CONTINUE")
        run_button_pressed.SetBackgroundColour(wx.Colour(181, 150, 27))
        run_button_pressed.SetToolTip("Continue running the simulation")
        self.GetSizer().Layout()

        no_of_cycles = self.cycles_spin_control.GetValue()
        self.run_network(no_of_cycles)
        self.update_canvas()
        
    def run_network(self, cycles):
        #print(f'No of cycles: {cycles}')
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True
    
    def update_canvas(self):
        self.signal_traces_panel.canvas.update_arguments(self.devices, self.monitors)

    def on_quit_button(self, event):
        """Handle the event when the user clicks the quit button."""
        quit_button_pressed = event.GetEventObject()
        text = "QUIT button pressed"
        print(text)
        quit_button_pressed.SetBackgroundColour(wx.Colour(148, 148, 148))

    def on_spin(self, event):
        pass

    def on_upload_button(self, event):
        """Handle the event when the user clicks the upload button."""
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard = "Text file (*.txt)|*.txt|",
            style=wx.FD_OPEN | wx.FD_MULTIPLE |
                  wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
                  wx.FD_PREVIEW
            )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()

            print('You selected %d files:' % len(paths))

            for path in paths:
                print('           %s\n' % path)

        # Compare this with the debug above; did we change working dirs?
        print("CWD: %s\n" % os.getcwd())

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

class SignalTrace(wx.ScrolledWindow):
    def __init__(self, parent, names, devices, network, monitors, id=wx.ID_ANY, size=wx.DefaultSize):
        super(SignalTrace, self).__init__(parent, id, size=size)

        size = self.GetClientSize()

        # Useful variables for ScrolledWindow
        self.lines = []
        self.maxWidth  = size.width * 2
        self.maxHeight = size.height
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        #self.SetBackgroundColour("PURPLE") # layout identifier colour for visualisation purposes

        # Set settings for ScrolledWindow
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20,20)


class SignalTracesPanel(wx.Panel):
    def __init__(self, parent, names, devices, network, monitors):
        super(SignalTracesPanel, self).__init__(parent, size=wx.DefaultSize, style=wx.SUNKEN_BORDER)

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

        self.add_new_monitor_panel = wx.Panel(self, name="add new monitor panel")
        add_new_monitor_panel_fgs = wx.FlexGridSizer(cols=3, rows=3, vgap=4, hgap=50)
        self.add_new_monitor_panel.SetSizer(add_new_monitor_panel_fgs)

        # Create and add "Add new monitor" text to add new monitor panel
        str = "Add new monitor"
        text = wx.StaticText(self.add_new_monitor_panel, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_fgs.Add(text, 0, flag=wx.ALIGN_CENTER)

        # Get the ids and user-defined names of all monitored and (as-of-yet) unmonitored devices
        monitored_devices_names = self.monitors.get_signal_names()[0]
        monitored_devices_ids = self.names.lookup(monitored_devices_names)
        unmonitored_devices_names = self.monitors.get_signal_names()[1]
        unmonitored_devices_ids = self.names.lookup(unmonitored_devices_names)

        # Create and add the dropdown menu for the as-of-yet unmonitored devices, ready to be monitored
        self.selected_device_to_monitor = None
        self.monitor_output_list = unmonitored_devices_names
        self.select_monitor_combo_box = wx.ComboBox(self.add_new_monitor_panel, wx.ID_ANY, "Select output", (90, 50),
                         (160, -1), self.monitor_output_list,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_new_monitor, self.select_monitor_combo_box)
        add_new_monitor_panel_fgs.Add(self.select_monitor_combo_box, 0, flag=wx.ALIGN_CENTER|wx.LEFT, border=30)

        # Create and add the "Add a new monitor" button to show up on SignalTraces panel
        self.add_new_monitor_button = wx.Button(self.add_new_monitor_panel, wx.ID_ANY, label="+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_monitor_button, self.add_new_monitor_button)
        self.add_new_monitor_button.SetToolTip("Add a new monitor")
        add_new_monitor_panel_fgs.Add(self.add_new_monitor_button, 1, flag=wx.CENTER|wx.EXPAND)

        # Create and add "Zap a monitor" text to add new monitor panel
        str = "Zap a monitor"
        text = wx.StaticText(self.add_new_monitor_panel, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_fgs.Add(text, 0, flag=wx.ALIGN_CENTER)

        # Create and add the dropdown menu for the currently monitored devices, ready to be zapped
        self.selected_device_to_zap = None
        self.monitor_output_list = monitored_devices_names
        self.zap_monitor_combo_box = wx.ComboBox(self.add_new_monitor_panel, wx.ID_ANY, "Select output", (90, 50),
                         (160, -1), self.monitor_output_list,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_zap_monitor, self.zap_monitor_combo_box)
        add_new_monitor_panel_fgs.Add(self.zap_monitor_combo_box, 0, flag=wx.ALIGN_CENTER|wx.LEFT, border=30)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self.signal_traces_panel, devices, monitors)
        signal_traces_panel_vbox.Add(self.canvas, 1, wx.EXPAND)

        vbox.Add(self.signal_traces_panel, 4, flag=wx.EXPAND)
        vbox.Add(self.add_new_monitor_panel, 1, flag=wx.EXPAND)

        # Set sizer of SignalTracesPanel
        self.SetSizer(vbox)

    def on_select_new_monitor(self, event):
        select_monitor_combo_box = event.GetEventObject()
        self.selected_device_to_monitor = select_monitor_combo_box.GetValue()
        print(f'Selected device to monitor: {self.selected_device_to_monitor}')

    def on_select_zap_monitor(self, event):
        zap_monitor_combo_box = event.GetEventObject()
        self.selected_device_to_zap = zap_monitor_combo_box.GetValue()
        print(f'Selected device to zap: {self.selected_device_to_zap}')

    def on_add_new_monitor_button(self, event):
        """Handle the event when the user clicks the add new monitor button."""
        add_new_monitor_button_pressed = event.GetEventObject()
        text = f"{add_new_monitor_button_pressed.GetLabel()} button pressed."
        print(text)
        print(self.selected_device_to_monitor)
        if self.selected_device_to_monitor is not None:
            selected_device_to_monitor_id = self.names.query(self.selected_device_to_monitor)
            print(selected_device_to_monitor_id)
            self.monitors.make_monitor(selected_device_to_monitor_id, None) # KO! what is output_id??
        self.update_canvas()
        
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
        font = wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
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
        self.switch_buttons_scrolled_panel = wxscrolledpanel.ScrolledPanel(self.switches_panel, name="switch buttons scrolled panel")

        # Get the ids and user-defined names of all SWITCH-type devices
        switch_ids = devices.find_devices(device_kind=devices.SWITCH)
        switch_names = [names.get_name_string(i) for i in switch_ids]

        # Configure sizer of ScrolledPanel
        self.num_of_switches = len(switch_names)
        self.fgs = wx.FlexGridSizer(cols=1, rows=self.num_of_switches, vgap=4, hgap=4)

        for switch in switch_names:
            switch_id = self.names.query(switch)
            initial_switch_state = devices.get_device(switch_id).switch_state 
            switch_toggle_button = wx.ToggleButton(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"{switch}") # create switch toggle button object with appropriate label
            switch_toggle_button.SetValue(bool(initial_switch_state))
            self.Bind(wx.EVT_TOGGLEBUTTON, self.on_switch_toggle_button, switch_toggle_button) # bind switch toggle button to its event
            self.fgs.Add(switch_toggle_button, 1, flag=wx.ALL, border=10) # add switch toggle buttons to ScrolledPanel

        # Set sizer of ScrolledPanel
        self.switch_buttons_scrolled_panel.SetSizer(self.fgs)
        self.switch_buttons_scrolled_panel.SetAutoLayout(1)
        self.switch_buttons_scrolled_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        # Create and add left panel in switches panel layout
        self.left_panel = wx.Panel(self.switches_panel)
        self.test_button = wx.Button(self.left_panel, wx.ID_ANY, "Temp \nbutton \nlocation \nfor \nadd \nnew \ndevice", (50,50))
        self.Bind(wx.EVT_BUTTON, self.on_test_button, self.test_button)
        left_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.left_panel.SetSizer(left_panel_vbox)
        left_panel_vbox.Add(self.test_button, 1, flag=wx.EXPAND)
        #left_panel_vbox.Add(self.add_new_switch_button, 1, flag=wx.EXPAND)
        hbox.Add(self.left_panel, 1, wx.EXPAND)

        # Add the ScrolledPanel widget to SwitchesPanel panel
        hbox.Add(self.switch_buttons_scrolled_panel, 2, wx.EXPAND)

        # Create and add right panel in switches panel layout
        self.right_panel = wx.Panel(self.switches_panel)
        #right_panel.SetBackgroundColour("BLUE") # layout identifier colour for visualisation purposes
        hbox.Add(self.right_panel, 1, wx.EXPAND)

        self.add_switch_panel = wx.Panel(self)
        add_switch_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_switch_panel.SetSizer(add_switch_panel_hbox)

        self.add_switch_panel_left = wx.Panel(self.add_switch_panel)
        add_switch_panel_hbox.Add(self.add_switch_panel_left, 1, wx.EXPAND)

        self.add_switch_panel_centre = wx.Panel(self.add_switch_panel)
        add_switch_panel_centre_vbox = wx.BoxSizer(wx.VERTICAL)
        self.add_new_switch_button = wx.Button(self.add_switch_panel_centre, wx.ID_ANY, "Add new switch")
        self.add_new_switch_button.SetToolTip("Add a new switch")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_switch_button, self.add_new_switch_button)
        add_switch_panel_centre_vbox.Add(self.add_new_switch_button, 1, flag=wx.CENTER|wx.EXPAND)
        add_switch_panel_hbox.Add(self.add_switch_panel_centre, 2, wx.EXPAND)

        self.add_switch_panel_right = wx.Panel(self.add_switch_panel)
        add_switch_panel_hbox.Add(self.add_switch_panel_right, 1, wx.EXPAND)

        vbox.Add(self.add_switch_panel, 1, wx.EXPAND)

        # Set sizer of SwitchesPanel
        self.SetSizer(vbox)
    
    def on_test_button(self, event):
        AddDeviceDialog(self, "Add a new device", self, self.names, self.devices, self.network, self.monitors).ShowModal() 
        

    def on_switch_toggle_button(self, event):
        """Handle the event when the user clicks the toggle button for a switch."""
        switch_selected = event.GetEventObject()
        switch_id = self.names.query(switch_selected.GetLabel())
        switch_state = switch_selected.GetValue()
        if self.devices.set_switch(switch_id, int(switch_state)): # successfully switched the state of switch
            pass

    def on_add_new_switch_button(self, event):
        print("Add new switch button pressed")
        self.num_of_switches += 1
        new_switch = wx.ToggleButton(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"switch {self.num_of_switches}")
        self.fgs.SetRows(self.num_of_switches + 1)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_switch_toggle_button, new_switch)
        self.fgs.Add(new_switch, 1, flag=wx.ALL, border=10)
        self.switch_buttons_scrolled_panel.Refresh()
        self.switches_panel.Layout()

    def on_change_right_panel_colour(self, event):
        self.right_panel.SetBackgroundColour("GREEN")
        self.right_panel.Layout()
        self.right_panel.Refresh()
        self.right_panel.Update()


class AddDeviceDialog(wx.Dialog): 
    def __init__(self, parent, title, switches_panel, names, devices, network, monitors):
        super(AddDeviceDialog, self).__init__(parent, title=title, size=(250,150))

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
    
        switch_radio_button = wx.RadioButton(panel, wx.ID_ANY, "Switch", style=wx.RB_GROUP)
        add_new_switch_button = wx.Button(panel, wx.ID_ANY, "+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_switch_button, add_new_switch_button)
        switch_device_property_panel = wx.Panel(panel, size=(60, 20))
        switch_device_property_panel_fgs = wx.FlexGridSizer(cols=2)
        switch_device_property_panel.SetSizer(switch_device_property_panel_fgs)
        switch_states = [wx.RadioButton(switch_device_property_panel, wx.ID_ANY, "1"), 
                         wx.RadioButton(switch_device_property_panel, wx.ID_ANY, "0")]
        for switch_state in switch_states:
            switch_device_property_panel_fgs.Add(switch_state, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)
            self.Bind(wx.EVT_RADIOBUTTON, self.on_select_switch_device_property, switch_state)
        #switch_device_property_panel.SetBackgroundColour('RED')
    
        clock_radio_button = wx.RadioButton(panel, wx.ID_ANY, "Clock")
        add_new_clock_button = wx.Button(panel, wx.ID_ANY, "+")
        self.Bind(wx.EVT_BUTTON, self.on_add_new_clock_button, add_new_clock_button)
        clock_device_property_panel = wx.Panel(panel, size=(70, 20))
        clock_device_property_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        clock_device_property_panel.SetSizer(clock_device_property_panel_vbox)
        clock_device_property_txtctrl = wx.TextCtrl(clock_device_property_panel, wx.ID_ANY, "")
        clock_device_property_txtctrl.Bind(wx.EVT_TEXT, self.on_type_clock_device_property)
        clock_device_property_panel_vbox.Add(clock_device_property_txtctrl, 1, flag=wx.EXPAND)
        #clock_device_property_panel.SetBackgroundColour('GREEN')
    
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

        self.add_new_device_ctrls.append((switch_radio_button, switch_user_name, add_new_switch_button, switch_device_property_panel))
        self.add_new_device_ctrls.append((clock_radio_button, clock_user_name, add_new_clock_button, clock_device_property_panel))
        self.add_new_device_ctrls.append((gate_radio_button, gate_user_name, add_new_gate_button, gate_device_property_panel))

        for radio, text, add_button, device_property in self.add_new_device_ctrls:
            devices_grid.Add(radio, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)
            devices_grid.Add(text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)
            devices_grid.Add(device_property, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)
            devices_grid.Add(add_button, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)

        devices_sizer.Add(devices_grid, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        vbox.Add(devices_sizer, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        panel.SetSizer(vbox)
        vbox.Fit(panel)
        panel.Move((50,50))
        self.panel = panel
    
    def on_switch_name_entry(self, event):
        switch_user_name = event.GetString()
        print(switch_user_name)
        self.switch_user_name = switch_user_name

    def on_clock_name_entry(self, event):
        clock_user_name = event.GetString()
        print(clock_user_name)
        self.clock_user_name = clock_user_name

    def on_gate_name_entry(self, event):
        gate_user_name = event.GetString()
        print(gate_user_name)
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
                    print(f'Answer: {self.clock_device_property}')
                    #print(self.clock_device_property)
    
    def on_add_new_clock_button(self, event):
        if self.clock_user_name is not None: # confirm if user-defined device name has been entered
            valid_name = self.clock_user_name
            print(f'Clock name: {valid_name}')
            if self.names.query(valid_name) is None: # confirm if user-defined name is unique and not already defined
                print('Unique clock!')
                unique_device_id = self.names.lookup([valid_name])[0]
                if self.clock_device_property is not None: # confirm if a clock period (clock device property) has been written (correctly)
                    clock_period = self.clock_device_property
                    if self.devices.make_device(unique_device_id, self.devices.CLOCK, clock_period) == self.devices.NO_ERROR:
                        print(f'Clock half period: {self.devices.get_device(unique_device_id).clock_half_period}')
                        print(f'Clock counter: {self.devices.get_device(unique_device_id).clock_counter}')
    
    def on_add_new_switch_button(self, event):
        if self.switch_user_name is not None: # confirm if user-defined device name has been entered
            valid_name = self.switch_user_name
            old_switch_ids = self.devices.find_devices(device_kind=self.devices.SWITCH)
            old_switch_names = [self.names.get_name_string(i) for i in old_switch_ids]
            print(old_switch_names)
            print(f'Switch name: {valid_name}')
            if self.names.query(valid_name) is None: # confirm if user-defined name is unique and not already defined
                print('Unique switch!')
                unique_device_id = self.names.lookup([valid_name])[0]
                if self.switch_device_property is not None: # confirm if a switch state (switch device property) has been selected
                    switch_state = int(self.switch_device_property)
                    if self.devices.make_device(unique_device_id, self.devices.SWITCH, switch_state) == self.devices.NO_ERROR:
                        print(f'Switch state: {self.devices.get_device(unique_device_id).switch_state}')
                        self.update_switches_panel(valid_name)
                '''print(f'Error: {x}')
                new_switch_ids = self.devices.find_devices(device_kind=self.devices.SWITCH)
                new_switch_names = [self.names.get_name_string(i) for i in new_switch_ids]
                print(new_switch_names)'''
    
    def update_switches_panel(self, switch_name):
        self.switches_panel.num_of_switches += 1
        new_switch = wx.ToggleButton(parent=self.switches_panel.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"{switch_name}")
        new_switch_id = self.names.query(switch_name)
        new_switch_state = self.devices.get_device(new_switch_id).switch_state 
        new_switch.SetValue(bool(new_switch_state))
        self.switches_panel.fgs.SetRows(self.switches_panel.num_of_switches + 1)
        self.switches_panel.Bind(wx.EVT_TOGGLEBUTTON, self.switches_panel.on_switch_toggle_button, new_switch)
        self.switches_panel.fgs.Add(new_switch, 1, flag=wx.ALL, border=10)
        self.switches_panel.switch_buttons_scrolled_panel.Refresh()
        self.switches_panel.Layout()


class LogicSimApp(wx.App):
    def OnInit(self):
        file_path = "logsim\logsim\example2_logic_description.txt"
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
        #breakpoint()
        #print(parser.parse_network())
        self.frame = Gui("GF2 Team 7 Logic Simulator GUI",
                         file_path,
                         names,
                         devices,
                         network,
                         monitors)
        self.frame.Show()

        return True


# KO! For development purposes only - will delete once complete
if __name__ == '__main__':
    app = LogicSimApp()
    app.MainLoop()
