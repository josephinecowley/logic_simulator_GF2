import wx
import wx.glcanvas as wxcanvas
import wx.lib.scrolledpanel as wxscrolledpanel
from OpenGL import GL, GLUT

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
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)


        # Instantiate SwitchesPanel widget and add to Frame
        self.switches_panel = SwitchesPanel(self)
        main_sizer.Add(self.switches_panel, 1, wx.EXPAND, 0)

        # Instantiate SignalTracesPanel widget and add to Frame
        self.signal_traces_panel = SignalTracesPanel(self)
        main_sizer.Add(self.signal_traces_panel, 2, wx.EXPAND, 0)

        '''# Add MyGLCanvas(ScrolledCanvas) instance to Frame 
        main_sizer.Add(self.scrollable, 2,  wx.EXPAND, 5)'''

        self.SetSizeHints(200, 200)
        self.SetSizer(main_sizer)
       
    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)

 
    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Button pressed."
        self.canvas.render(text)

class SignalTrace(wx.ScrolledWindow):
    def __init_(self, parent):
        super(SignalTrace, self).__init__(parent)

        self.lines = []
        self.maxWidth  = 1000
        self.maxHeight = 1000
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        self.SetBackgroundColour("WHITE")

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20,20)

class SignalTracesPanel(wx.Panel):
    def __init__(self, parent):
        super(SignalTracesPanel, self).__init__(parent, size=(300, 200))

        # Configure sizers for layout of SwitchesPanel panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        signal_traces_scrolled_panel = wxscrolledpanel.ScrolledPanel(self, name="signal traces scrolled panel")

        signal_trace_size = (1000, 200)
        num_of_signal_traces = 7
        fgs = wx.FlexGridSizer(cols=1, rows=num_of_signal_traces, vgap=4, hgap=4)

        '''test_flag = True
        for signal_trace_num in range(1, num_of_signal_traces + 1):
            scrollable = wx.ScrolledCanvas(signal_traces_scrolled_panel, wx.ID_ANY)
            scrollable.SetSizeHints(800, 200)
            scrollable.SetVirtualSize(1000, 300)
            if test_flag:
                print(f'Virtual Size: {scrollable.GetVirtualSize()}')
                print(f'Actual Size: {scrollable.GetSize()}')
                test_flag = False
            #scrollable.SetVirtualSize(200, 200)
            scrollable.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_DEFAULT)
            scrollable.SetScrollbars(20, 20, 15, 10)
            signal_trace = MyGLCanvas(scrollable, wx.ID_ANY, wx.DefaultPosition,  wx.Size(*signal_trace_size))
            #print(scrollable.GetSize())
            fgs.Add(scrollable, 1, flag=wx.EXPAND, border=10)'''
        
        for signal_trace_num in range(1, num_of_signal_traces + 1):
            signal_trace = SignalTrace(signal_traces_scrolled_panel, wx.ID_ANY)
            signal_trace_canvas = MyGLCanvas(signal_trace, wx.ID_ANY, wx.DefaultPosition,  wx.Size(*signal_trace_size))
            fgs.Add(signal_trace, 1, flag=wx.EXPAND, border=10)

        signal_traces_scrolled_panel.SetSizer(fgs)
        signal_traces_scrolled_panel.SetAutoLayout(1)
        signal_traces_scrolled_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        vbox.Add(signal_traces_scrolled_panel, 1, wx.EXPAND)

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

        switches_panel = wx.Panel(self)
        #switches_panel.SetBackgroundColour(wx.Colour(255, 0, 0))
        vbox.Add(switches_panel, 1, wx.EXPAND)
        switches_panel.SetSizer(hbox)

        # Instantiate ScrolledPanel widget
        switch_buttons_scrolled_panel = wxscrolledpanel.ScrolledPanel(switches_panel, name="switch buttons scrolled panel")

        # Configure sizer of ScrolledPanel widget
        num_of_switches = 30
        fgs = wx.FlexGridSizer(cols=1, rows=num_of_switches, vgap=4, hgap=4)

        for switch_num in range(1, num_of_switches + 1):
            switch = wx.ToggleButton(parent=switch_buttons_scrolled_panel, id=wx.ID_ANY, label=f"switch {switch_num}") # create switch toggle button object with appropriate label
            self.Bind(wx.EVT_TOGGLEBUTTON, self.on_switch_toggle_button, switch) # bind switch toggle button to its event
            fgs.Add(switch, 1, flag=wx.ALL, border=10) # add switch toggle buttons to ScrolledPanel widget

        # Set sizer of ScrolledPanel widget
        switch_buttons_scrolled_panel.SetSizer(fgs)
        switch_buttons_scrolled_panel.SetAutoLayout(1)
        switch_buttons_scrolled_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20, scrollToTop=True, scrollIntoView=True)

        '''### Sizer Tutorial
        switches_panel = wx.Panel(self)
        switches_panel.SetBackgroundColour(wx.Colour(255, 0, 0))
        vbox.Add(switches_panel, 1, wx.EXPAND)
        switches_panel.SetSizer(hbox)

        left_panel = wx.Panel(switches_panel)
        left_panel.SetBackgroundColour(wx.Colour(0, 255, 0))
        hbox.Add(left_panel, 1, wx.ALL | wx.EXPAND, 0)

        right_panel = wx.Panel(switches_panel)
        right_panel.SetBackgroundColour(wx.Colour(0, 0, 255))
        hbox.Add(right_panel, 2, wx.ALL | wx.EXPAND, 0)
        ###'''

        # Create and add left panel in switches panel layout
        left_panel = wx.Panel(switches_panel)
        left_panel.SetBackgroundColour(wx.Colour(0, 255, 0)) # green for layout visualisation purposes
        hbox.Add(left_panel, 1, wx.EXPAND)

        # Add the ScrolledPanel widget to SwitchesPanel panel
        hbox.Add(switch_buttons_scrolled_panel, 2, wx.EXPAND)

        # Create and add right panel in switches panel layout
        right_panel = wx.Panel(switches_panel)
        right_panel.SetBackgroundColour(wx.Colour(0, 0, 255)) # blue for layout visualisation purposes
        hbox.Add(right_panel, 1, wx.EXPAND)

        # Set sizer of SwitchesPanel panel
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
