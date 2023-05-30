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

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

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
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
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
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


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
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        '''# Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)'''

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)

        # Configure sizers for layout of Frame
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create data panel and add to Frame
        data_panel = wx.Panel(self)
        vbox.Add(data_panel, 8, wx.EXPAND)
        data_panel.SetSizer(hbox)

        # Instantiate SwitchesPanel widget and add to Frame
        switches_panel = SwitchesPanel(data_panel)
        hbox.Add(switches_panel, 1, wx.EXPAND, 0)

        # Instantiate SignalTracesPanel widget and add to Frame
        signal_traces_panel = SignalTracesPanel(data_panel)
        hbox.Add(signal_traces_panel, 3, wx.EXPAND, 0)

        # Instantiate RunSimulationPanel widget and add to Frame
        simulation_panel = RunSimulationPanel(self)
        vbox.Add(simulation_panel, 1, wx.EXPAND)

        self.SetSizeHints(200, 200)
        self.SetSizer(vbox)


    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)


class RunSimulationPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize):
        super(RunSimulationPanel, self).__init__(parent, id, size=size, style=wx.SIMPLE_BORDER)

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
        # Create and add spin text widget to cycles panel
        self.spin_text = wx.TextCtrl(self.cycles_panel, wx.ID_ANY, "1", pos=wx.DefaultPosition, size=(60, -1))
        spin = wx.SpinButton(self.cycles_panel, wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SP_VERTICAL)
        spin.SetRange(1, 100)
        spin.SetValue(1)
        self.Bind(wx.EVT_SPIN, self.on_spin, spin)
        cycles_hbox.Add(self.spin_text, 0, flag=wx.LEFT, border=10)
        cycles_hbox.Add(spin, 0, flag=wx.LEFT, border=10)

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

        # Create and set sizer of overall centre panel
        self.centre_panel = wx.Panel(self)
        centre_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.centre_panel, 2, flag=wx.EXPAND)

        
        # Create and set sizer of upload and help buttons panel
        self.upload_and_help_buttons_panel = wx.Panel(self, name="upload and help buttons panel")
        upload_and_help_buttons_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.upload_and_help_buttons_panel.SetSizer(upload_and_help_buttons_panel_hbox)

        # Create and set sizer of upload button panel
        self.upload_button_panel = wx.Panel(self.upload_and_help_buttons_panel, name="upload button panel")
        upload_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.upload_button_panel.SetSizer(upload_button_panel_vbox)

        # Create, bind upload logic description file event to and add the "UPLOAD" button
        self.upload_button = wx.Button(self.upload_button_panel, wx.ID_ANY, "UPLOAD")
        self.Bind(wx.EVT_BUTTON, self.on_upload_button, self.upload_button)
        self.upload_button.SetToolTip("Upload logic description file")
        upload_button_panel_vbox.Add(self.upload_button, 1, flag=wx.ALIGN_CENTER)

        # Create and set sizer of help button panel
        self.help_button_panel = wx.Panel(self.upload_and_help_buttons_panel, name="help button panel")
        help_button_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.help_button_panel.SetSizer(help_button_panel_vbox)

        # Create, bind help popup window [TO BE IMPLEMENTED] event to and add the "HELP" button
        self.help_button = wx.Button(self.help_button_panel, wx.ID_ANY, "HELP")
        self.help_button.SetToolTip("Help on running logic simulation")
        help_button_panel_vbox.Add(self.help_button, 1, flag=wx.ALIGN_CENTER)

        # Add (upload button panel) + (help button panel) to (upload and help buttons panel)
        upload_and_help_buttons_panel_hbox.Add(self.upload_button_panel, 1, flag=wx.EXPAND)
        upload_and_help_buttons_panel_hbox.Add(self.help_button_panel, 1, flag=wx.EXPAND)

        # Add (upload and help buttons panel) to RunSimulationPanel
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

    def on_quit_button(self, event):
        """Handle the event when the user clicks the quit button."""
        quit_button_pressed = event.GetEventObject()
        text = "QUIT button pressed"
        print(text)
        quit_button_pressed.SetBackgroundColour(wx.Colour(148, 148, 148))

    def on_spin(self, event):
        self.spin_text.SetValue(str(event.GetPosition()))

    def on_upload_button(self, event):
        """Handle the event when the user clicks the upload button."""
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Text file (*.txt)|*.txt|",
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
    def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize):
        super(SignalTrace, self).__init__(parent, id, size=size)

        size = self.GetClientSize()

        # Useful variables for ScrolledWindow
        self.lines = []
        self.maxWidth  = size.width * 2
        self.maxHeight = size.height
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        # Set settings for ScrolledWindow
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20,20)


class SignalTracesPanel(wx.Panel):
    def __init__(self, parent):
        super(SignalTracesPanel, self).__init__(parent, size=wx.DefaultSize, style=wx.SUNKEN_BORDER)

        # Configure sizers for layout of SwitchesPanel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Create and set sizer of signal traces panel
        self.signal_traces_panel = wx.Panel(self, name="signal traces panel")
        signal_traces_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.signal_traces_panel.SetSizer(signal_traces_panel_vbox)

        # Create and set sizer of add new monitor panel
        self.add_new_monitor_panel = wx.Panel(self, name="add new monitor panel")
        add_new_monitor_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel.SetSizer(add_new_monitor_panel_hbox)

        # Create LEFT panel for add new monitor panel
        self.add_new_monitor_panel_LEFT = wx.Panel(self.add_new_monitor_panel, name="add new monitor LEFT panel")
        # Add (LEFT panel for add new monitor panel) to (add_new_monitor_panel) 
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_LEFT, 1, flag=wx.EXPAND)

        # Create and configure sizer for CENTRAL panel of add new monitor panel
        self.add_new_monitor_panel_CENTRE = wx.Panel(self.add_new_monitor_panel, name="add new monitor CENTRE panel")
        add_new_monitor_panel_CENTRE_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel_CENTRE.SetSizer(add_new_monitor_panel_CENTRE_hbox)

        # Create and add guiding text for "Add new monitor" to CENTRE panel of add new monitor panel
        str = "Add new monitor"
        text = wx.StaticText(self.add_new_monitor_panel_CENTRE, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_CENTRE_hbox.Add(text, 0, flag=wx.ALIGN_CENTER)

        # Create and add the dropdown menu of available monitor lists to add new monitor panel
        self.monitor_output_list = ["deviceA", "deviceB", "switchC", "dtypeD", "deviceE"] # KO! PLACEHOLDER: needs to be configured
        self.combo_box = wx.ComboBox(self.add_new_monitor_panel_CENTRE, 500, "Select output", (90, 50),
                         (160, -1), self.monitor_output_list,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )
        add_new_monitor_panel_CENTRE_hbox.Add(self.combo_box, 0, flag=wx.ALIGN_CENTER|wx.LEFT, border=30)

        # Add (CENTRE panel for add new monitor panel) to (add_new_monitor_panel)
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_CENTRE, 3, flag=wx.EXPAND)

        # Create and configure sizer for RIGHT panel of add new monitor panel
        self.add_new_monitor_panel_RIGHT = wx.Panel(self.add_new_monitor_panel, name="add new monitor RIGHT panel")
        add_new_monitor_panel_RIGHT_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel_RIGHT.SetSizer(add_new_monitor_panel_RIGHT_hbox)

        # Create and add "ADD NEW MONITOR" button to RIGHT panel of add new monitor panel
        self.add_new_monitor_button = wx.Button(self.add_new_monitor_panel_RIGHT, wx.ID_ANY, label="+") # KO! PLACEHOLDER: needs to be configured
        self.add_new_monitor_button.SetToolTip("Add a new monitor")
        add_new_monitor_panel_RIGHT_hbox.Add(self.add_new_monitor_button, 1, flag=wx.EXPAND)

        # Add (RIGHT panel for add new monitor panel) to (add_new_monitor_panel)
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_RIGHT, 1, flag=wx.EXPAND)

        # Instantiate ScrolledPanel
        self.signal_traces_scrolled_panel = wxscrolledpanel.ScrolledPanel(self.signal_traces_panel, name="signal traces scrolled panel")

        # Configure sizer of ScrolledPanel
        signal_trace_size = (500, 200)
        self.num_of_signal_traces = 7
        fgs = wx.FlexGridSizer(cols=3, rows=self.num_of_signal_traces, vgap=4, hgap=50)
        
        # Create named and deletable signal trace plot for each initially monitor-specified (from LDF) and add to ScrolledPanel 
        for signal_trace_num in range(1, self.num_of_signal_traces + 1):
            str = f"device {signal_trace_num}"
            text = wx.StaticText(self.signal_traces_scrolled_panel, wx.ID_ANY, str) # create accompanying text KO! PLACEHOLDER: needs configuring
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            text.SetFont(font)

            signal_trace = SignalTrace(self.signal_traces_scrolled_panel, wx.ID_ANY, size=signal_trace_size) # create signal trace scrolled window
            signal_trace_canvas = MyGLCanvas(signal_trace, wx.ID_ANY, wx.DefaultPosition,  wx.Size(*signal_trace_size)) # draw canvas onto signal trace scrolled window

            delete_button = wxaquabutton.AquaButton(self.signal_traces_scrolled_panel, wx.ID_ANY, bitmap=None, label="DELETE") # create accompanying delete button
            delete_button.SetBackgroundColor(wx.Colour("BLUE"))
            delete_button.SetHoverColor(wx.Colour("RED"))
            delete_button.SetFocusColour(wx.Colour("BLUE"))

            fgs.Add(text, 0, flag=wx.ALIGN_CENTER|wx.LEFT, border=10)
            fgs.Add(signal_trace, 0, flag=wx.EXPAND, border=10) # add signal trace plot to ScrolledPanel
            fgs.Add(delete_button, 0, flag=wx.ALIGN_CENTER|wx.RIGHT, border=10)

        # Set sizer of ScrolledPanel
        self.signal_traces_scrolled_panel.SetSizer(fgs)
        self.signal_traces_scrolled_panel.SetAutoLayout(1)
        self.signal_traces_scrolled_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        # Add (signal traces scrolled panel) to (signal traces panel)
        signal_traces_panel_vbox.Add(self.signal_traces_scrolled_panel, 1, wx.EXPAND)

        # Add (signal traces panel) and (add new monitor panel) to SignalTracesPanel
        vbox.Add(self.signal_traces_panel, 4, flag=wx.EXPAND)
        vbox.Add(self.add_new_monitor_panel, 1, flag=wx.EXPAND)

        # Set sizer of SignalTracesPanel
        self.SetSizer(vbox)


class SwitchesPanel(wx.Panel):
    def __init__(self, parent):
        super(SwitchesPanel, self).__init__(parent, size=(300, 200))

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

        # Create switches panel for switch toggle buttons
        self.switches_panel = wx.Panel(self)
        vbox.Add(self.switches_panel, 7, wx.EXPAND)
        self.switches_panel.SetSizer(hbox)

        # Create switch buttons scrolled panel
        self.switch_buttons_scrolled_panel = wxscrolledpanel.ScrolledPanel(self.switches_panel, name="switch buttons scrolled panel")

        # Configure sizer of switch buttons scrolled panel
        self.num_of_switches = 30
        self.fgs = wx.FlexGridSizer(cols=1, rows=self.num_of_switches+10, vgap=4, hgap=4)

        for switch_num in range(1, self.num_of_switches + 1):
            switch = wx.ToggleButton(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"switch {switch_num}") # create switch toggle button object with appropriate label
            self.Bind(wx.EVT_TOGGLEBUTTON, self.on_switch_toggle_button, switch) # bind switch toggle button to its event
            fgs.Add(switch, 1, flag=wx.ALL, border=10) # add switch toggle buttons to ScrolledPanel

        # Set sizer of switch buttons scrolled panel
        self.switch_buttons_scrolled_panel.SetSizer(fgs)
        self.switch_buttons_scrolled_panel.SetAutoLayout(1)
        self.switch_buttons_scrolled_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        # Create and add left panel in switches panel layout
        self.left_panel = wx.Panel(self.switches_panel)
        hbox.Add(self.left_panel, 1, wx.EXPAND)

        # Add the ScrolledPanel widget to SwitchesPanel panel
        hbox.Add(self.switch_buttons_scrolled_panel, 2, wx.EXPAND)

        # Create and add right panel in switches panel layout
        self.right_panel = wx.Panel(self.switches_panel)
        hbox.Add(self.right_panel, 1, wx.EXPAND)

        # Set sizer of SwitchesPanel
        self.SetSizer(vbox)

    def on_switch_toggle_button(self, event):
        """Handle the event when the user clicks the toggle button for a switch."""
        switch_selected = event.GetEventObject()
        print(f'{switch_selected.GetLabel()} has been pressed.')


class LogicSimApp(wx.App):
    def OnInit(self):
        file_path = "logsim\logsim\example2_logic_description.txt"
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        print(parser.parse_network())
        #breakpoint()
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
