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
import sys
from contextlib import redirect_stdout

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

    def __init__(self, parent, devices, monitors, current_time=None):
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
        self.zoom = 1.0

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.Bind(wx.EVT_CHAR, self.on_key_press)

        # Initialise trace objects
        self.traces = monitors.get_signals_for_GUI()
        self.y_spacing = 80

        # Initialise instance attributes
        self.devices = devices
        self.monitors = monitors

        # self.current_time initialised as 0 and then takes future args for current_time
        if current_time is None:
            self.current_time = 0
        else:
            self.current_time = current_time

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

        # Adjust the translation values for panning and centering
        GL.glTranslated(self.pan_x , self.pan_y + size.height/2 - self.y_spacing * (len(self.traces) - 1) , 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def draw_canvas(self):
        """Iterates through each trace and draws it on the canvas with an offset"""
        x_offset = 150
        y_offset = 400
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
        for i, signal_value in enumerate(signal):
            x = (i * 20) + x_pos
            x_next = (i * 20) + x_pos + 20
            if signal_value == 0 or signal_value == 1:
                GL.glColor3f(*color)
                y = y_pos + (25 * signal_value)
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
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
            GL.glEnd()
            # Render sizes
            if self.zoom >= 1:
                self.render_text(str(i + self.current_time), x - 5, y_pos - 15, small=True)
            elif ((self.zoom < 1) and (i % 5 == 0)):
                self.render_text(str(i + self.current_time), x - 5, y_pos - 25, small=True)
        
        x_pos -= int(40 / 3 * len(label))
        self.render_text(label, x_pos, y_pos + 18)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw signal traces
        self.draw_canvas()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
    
    def on_key_press(self, event):
        """Handles key press events"""
        keycode = event.GetKeyCode()
        if keycode == ord("c"):
            self.recenter_canvas()
        event.Skip()  # Allow other key events to propagate

    def on_right_click(self, event):
        """Handles right click event"""
        self.clear_traces()

    def recenter_canvas(self):
        size = self.GetClientSize()
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1.0

        # Adjust the translation values for panning and centering
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x , self.pan_y + size.height/2 - self.y_spacing * (len(self.traces) - 1) , 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)
        
        self.Refresh()
    
    def clear_traces(self):
        """Updates current time and clears traces"""
        # update current_time 
        no_of_cycles = len(self.traces[0][1]) 
        self.current_time += no_of_cycles

        # clear monitor traces
        self.monitors.reset_monitors()
        self.update_arguments(self.devices, self.monitors)


    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        self.render()

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
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, small=False):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        if small:
            font = GLUT.GLUT_BITMAP_HELVETICA_12
        else:
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

        # Trigger a redraw
        self.Refresh()
