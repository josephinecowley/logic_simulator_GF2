import os

import wx
import wx.glcanvas as wxcanvas
import wx.lib.scrolledpanel as wxscrolledpanel
import wx.lib.buttons as wxbuttons
import wx.lib.agw.aquabutton as wxaquabutton
from OpenGL import GL, GLUT

wildcard = "Python source (*.py)|*.py|"     \
           "Compiled Python (*.pyc)|*.pyc|" \
           "SPAM files (*.spam)|*.spam|"    \
           "Egg file (*.egg)|*.egg|"        \
           "All files (*.*)|*.*"


class MyGLCanvas(wxcanvas.GLCanvas):
    def __init__(self, parent, id, pos, size):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1, pos=pos, size=size,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

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
        GL.glColor3f(1.0, 0.0, 0.0)  # signal trace is blue
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
    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1000, 700))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)

        # Configure sizers for layout of Frame
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        data_panel = wx.Panel(self)
        vbox.Add(data_panel, 8, wx.EXPAND)
        data_panel.SetSizer(hbox)

        # Instantiate SwitchesPanel widget and add to Frame
        switches_panel = SwitchesPanel(data_panel)
        hbox.Add(switches_panel, 1, wx.EXPAND, 0)

        # Instantiate SignalTracesPanel widget and add to Frame
        signal_traces_panel = SignalTracesPanel(data_panel)
        hbox.Add(signal_traces_panel, 3, wx.EXPAND, 0)

        simulation_panel = RunSimulationPanel(self)
        vbox.Add(simulation_panel, 1, wx.EXPAND)

        self.SetSizeHints(200, 200)
        self.SetSizer(vbox)
       
    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)

class RunSimulationPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize):
        super(RunSimulationPanel, self).__init__(parent, id, size=size, style=wx.SIMPLE_BORDER)

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
        
        # Create number of cycles text to cycles panel
        str = "No. Cycles"
        text = wx.StaticText(self.cycles_panel, wx.ID_ANY, str, style=wx.ALIGN_LEFT)
        font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        cycles_hbox.Add(text, 0, flag=wx.TOP|wx.LEFT)
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

        
        self.centre_panel = wx.Panel(self)
        #centre_panel.SetBackgroundColour("GREEN") # layout identifier colour for visualisation purposes
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
            wildcard=wildcard,
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

        #self.SetBackgroundColour("PURPLE") # layout identifier colour for visualisation purposes

        # Set settings for ScrolledWindow
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20,20)


class SignalTracesPanel(wx.Panel):
    def __init__(self, parent):
        super(SignalTracesPanel, self).__init__(parent, size=wx.DefaultSize, style=wx.SUNKEN_BORDER)

        # Configure sizers for layout of SwitchesPanel panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.signal_traces_panel = wx.Panel(self, name="signal traces panel")
        signal_traces_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.signal_traces_panel.SetSizer(signal_traces_panel_vbox)

        self.add_new_monitor_panel = wx.Panel(self, name="add new monitor panel")
        #add_new_monitor_panel.SetBackgroundColour(wx.Colour(0, 238, 238)) # layout identifier colour for visualisation purposes
        add_new_monitor_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel.SetSizer(add_new_monitor_panel_hbox)


        self.add_new_monitor_panel_LEFT = wx.Panel(self.add_new_monitor_panel, name="add new monitor LEFT panel")
        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_LEFT, 1, flag=wx.EXPAND)


        self.add_new_monitor_panel_CENTRE = wx.Panel(self.add_new_monitor_panel, name="add new monitor CENTRE panel")
        add_new_monitor_panel_CENTRE_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel_CENTRE.SetSizer(add_new_monitor_panel_CENTRE_hbox)

        str = "Add new monitor"
        text = wx.StaticText(self.add_new_monitor_panel_CENTRE, wx.ID_ANY, str)
        font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text.SetFont(font)
        add_new_monitor_panel_CENTRE_hbox.Add(text, 0, flag=wx.ALIGN_CENTER)

        self.monitor_output_list = ["deviceA", "deviceB", "switchC", "dtypeD", "deviceE"]
        self.combo_box = wx.ComboBox(self.add_new_monitor_panel_CENTRE, 500, "Select output", (90, 50),
                         (160, -1), self.monitor_output_list,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )
        add_new_monitor_panel_CENTRE_hbox.Add(self.combo_box, 0, flag=wx.ALIGN_CENTER|wx.LEFT, border=30)

        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_CENTRE, 3, flag=wx.EXPAND)


        self.add_new_monitor_panel_RIGHT = wx.Panel(self.add_new_monitor_panel, name="add new monitor RIGHT panel")
        add_new_monitor_panel_RIGHT_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.add_new_monitor_panel_RIGHT.SetSizer(add_new_monitor_panel_RIGHT_hbox)
        self.add_new_monitor_button = wx.Button(self.add_new_monitor_panel_RIGHT, wx.ID_ANY, label="+")
        self.add_new_monitor_button.SetToolTip("Add a new monitor")
        add_new_monitor_panel_RIGHT_hbox.Add(self.add_new_monitor_button, 1, flag=wx.EXPAND)

        add_new_monitor_panel_hbox.Add(self.add_new_monitor_panel_RIGHT, 1, flag=wx.EXPAND)

        # Instantiate ScrolledPanel
        self.signal_traces_scrolled_panel = wxscrolledpanel.ScrolledPanel(self.signal_traces_panel, name="signal traces scrolled panel")

        # Configure sizer of ScrolledPanel
        signal_trace_size = (500, 200)
        self.num_of_signal_traces = 7
        fgs = wx.FlexGridSizer(cols=3, rows=self.num_of_signal_traces, vgap=4, hgap=50)
        
        for signal_trace_num in range(1, self.num_of_signal_traces + 1):
            str = f"device {signal_trace_num}"
            text = wx.StaticText(self.signal_traces_scrolled_panel, wx.ID_ANY, str)
            font = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            text.SetFont(font)

            signal_trace = SignalTrace(self.signal_traces_scrolled_panel, wx.ID_ANY, size=signal_trace_size) # create signal trace scrolled window
            signal_trace_canvas = MyGLCanvas(signal_trace, wx.ID_ANY, wx.DefaultPosition,  wx.Size(*signal_trace_size)) # draw canvas onto signal trace scrolled window

            delete_button = wxaquabutton.AquaButton(self.signal_traces_scrolled_panel, wx.ID_ANY, bitmap=None, label="DELETE")
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

        signal_traces_panel_vbox.Add(self.signal_traces_scrolled_panel, 1, wx.EXPAND)

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

        # Create panel for switch toggle buttons
        self.switches_panel = wx.Panel(self)
        #switches_panel.SetBackgroundColour(wx.Colour(255, 0, 0))
        vbox.Add(self.switches_panel, 7, wx.EXPAND)
        self.switches_panel.SetSizer(hbox)

        # Instantiate ScrolledPanel
        self.switch_buttons_scrolled_panel = wxscrolledpanel.ScrolledPanel(self.switches_panel, name="switch buttons scrolled panel")

        # Configure sizer of ScrolledPanel
        self.num_of_switches = 30
        fgs = wx.FlexGridSizer(cols=1, rows=self.num_of_switches, vgap=4, hgap=4)

        for switch_num in range(1, self.num_of_switches + 1):
            switch = wx.ToggleButton(parent=self.switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"switch {switch_num}") # create switch toggle button object with appropriate label
            self.Bind(wx.EVT_TOGGLEBUTTON, self.on_switch_toggle_button, switch) # bind switch toggle button to its event
            fgs.Add(switch, 1, flag=wx.ALL, border=10) # add switch toggle buttons to ScrolledPanel

        # Set sizer of ScrolledPanel
        self.switch_buttons_scrolled_panel.SetSizer(fgs)
        self.switch_buttons_scrolled_panel.SetAutoLayout(1)
        self.switch_buttons_scrolled_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        # Create and add left panel in switches panel layout
        self.left_panel = wx.Panel(self.switches_panel)
        #left_panel.SetBackgroundColour("GREEN") # layout identifier colour for visualisation purposes
        hbox.Add(self.left_panel, 1, wx.EXPAND)

        # Add the ScrolledPanel widget to SwitchesPanel panel
        hbox.Add(self.switch_buttons_scrolled_panel, 2, wx.EXPAND)

        # Create and add right panel in switches panel layout
        self.right_panel = wx.Panel(self.switches_panel)
        #right_panel.SetBackgroundColour("BLUE") # layout identifier colour for visualisation purposes
        hbox.Add(self.right_panel, 1, wx.EXPAND)

        # Set sizer of SwitchesPanel
        self.SetSizer(vbox)

    def on_switch_toggle_button(self, event):
        """Handle the event when the user clicks the toggle button for a switch."""
        switch_selected = event.GetEventObject()
        print(f'{switch_selected.GetLabel()} has been pressed.')


class SimulationPanel(wx.Panel):
    def __init__(self, parent):
        super(SimulationPanel, self).__init__(parent)


class LogicSimApp(wx.App):
    def OnInit(self):
        self.frame = Gui("GF2 Team 7 Logic Simulator GUI")
        self.frame.Show()

        return True


if __name__ == '__main__':
    app = LogicSimApp()
    app.MainLoop()
