#!BPY

# """
# Name: 'Blender Assisted Design (BAD)'
# Blender: 243
# Group: 'Mesh'
# Tooltip: 'The CAD for Blender.'
# """

# Copyright (C) 2009 Mart Roosmaa <roosmaa@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Mart Roosmaa'
__version__ = '0.1'
__url__ = ('Project page, http://www.roosmaa.net/', )
__email__ = ('Mart Roosmaa, roosmaa:gmail*com', )
__bpydoc__ = """
This is a helper script to assist in percision modelling.
"""

from Blender import Draw, Scene, Mesh, Window, BGL
import BPyMessages
import bpy

from bad import *

GUI_EDGE_LENGTH = 1
_gui_edge_length = 1.0
_gui_edge_length_button = None

GUI_EDGE_ANGLE = 2
_gui_edge_angle = 45.0
_gui_edge_angle_button = None

GUI_EDGE_WELD = 3
_gui_edge_weld_button = None

def bad_script_call(func, *args):
	sce = bpy.data.scenes.active
	ob_act = sce.objects.active

	if not ob_act or ob_act.type != 'Mesh':
		BPyMessages.Error_NoMeshActive()
		return 
	
	is_editmode = Window.EditMode()
	if is_editmode: Window.EditMode(0)
	
	try:
		Window.WaitCursor(1)
		me = ob_act.getData(mesh=1)
		
		try:
			func(me, *args)
		except BadError, e:
			Draw.PupMenu("Error%%t|%s" % e)
	finally:
		# Restore editmode if it was enabled
		if is_editmode: Window.EditMode(1)
		Window.WaitCursor(0)

def bad_script_set_length(mesh, length):
		# Get selected edges:
		sel = mesh.edges.selected()
		
		# Force only 2 edge selection:
		if len(sel) != 1:
			raise BadError, 'Can only set the length of one edge'
		
		e1 = mesh.edges[sel[0]]
		bad_set_length(e1, length)

def bad_script_set_angle(mesh, angle):
		# Get selected edges:
		sel = []
		for e in mesh.edges:
			if e.sel:
				sel.append(e.index)
		
		# Force only 2 edge selection:
		if len(sel) != 2:
			raise BadError, 'Angle can be set for exactly 2 edges'
		
		e1 = mesh.edges[sel[0]]
		e2 = mesh.edges[sel[1]]
		
		bad_set_angle(e1, e2, angle)

def bad_script_weld(mesh):
		# Get selected edges:
		sel = []
		for e in mesh.edges:
			if e.sel:
				sel.append(e.index)
		
		# Force only 2 edge selection:
		if len(sel) != 2:
			raise BadError, 'Only 2 edges can be welded at a time'
		
		e1 = mesh.edges[sel[0]]
		e2 = mesh.edges[sel[1]]
		
		bad_weld_edges(mesh, e1, e2)

def bad_draw():
	global _gui_edge_length_button, _gui_edge_angle_button, _gui_edge_weld_button
	try:
		BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)
		BGL.glRasterPos2d(8, 40)
		Draw.Text('Blender Assisted Design', 'large')
		_gui_edge_length_button = Draw.Number('Edge length: ', GUI_EDGE_LENGTH, 8, 8, 200, 24, _gui_edge_length, 0.0, 1000.0, bad_set_length.__doc__)
		Draw.PushButton(
			'Set', 0,
			214, 8, 40, 24,
			bad_set_length.__doc__,
			lambda *a: bad_script_call(bad_script_set_length, float(_gui_edge_length))
		)
		
		_gui_edge_angle_button = Draw.Number('Edge angle: ', GUI_EDGE_ANGLE, 270, 8, 200, 24, _gui_edge_angle, 0.0, 180.0, bad_set_angle.__doc__)
		Draw.PushButton(
			'Set', 0,
			476, 8, 40, 24,
			bad_set_angle.__doc__,
			lambda *a: bad_script_call(bad_script_set_angle, float(_gui_edge_angle))
		)
		
		Draw.PushButton(
			'Weld', 0,
			534, 8, 50, 24,
			bad_weld_edges.__doc__,
			lambda *a: bad_script_call(bad_script_weld)
		)
	except Exception, e:
		print e
		Draw.Exit()

def bad_event(evt, val):
	pass

def bad_button_event(evt):
	if evt == GUI_EDGE_LENGTH:
		global _gui_edge_length
		_gui_edge_length = _gui_edge_length_button.val
	elif evt == GUI_EDGE_ANGLE:
		global _gui_edge_angle
		_gui_edge_angle = _gui_edge_angle_button.val

if __name__ == '__main__':
	from Blender import Text
	try:
		txt = Text.Get('BAD')
		txt.clear()
	except NameError:
		txt = Text.New('BAD')
		txt.fakeUser = True
	# Just in casee, overwrite the file
	txt.write("""\
# SPACEHANDLER.VIEW3D.EVENT

from bad.space import bad_space_handler
bad_space_handler()
""")
	Draw.Register(bad_draw, bad_event, bad_button_event)

