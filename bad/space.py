#!/usr/bin/python

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

from Blender import Draw, Mesh, Window
import BPyMessages
import bpy

from bad import *

def bad_space_set_length():
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
		
		# Get selected edges:
		sel = me.edges.selected()
		
		# Force only 2 edge selection:
		if len(sel) != 1:
			Draw.PupMenu("Error%t|Can only set the length of one edge")
			return
		
		e1 = me.edges[sel[0]]
		
		length = Draw.Create(bad_get_length(e1))
		ret = Draw.PupBlock('Set length', (
			('Length: ', length, 0, 180, bad_set_length.__doc__), 
		))
		if ret == 1:
			try:
				bad_set_length(e1, float(repr(length)))
			except BadError, e:
				Draw.PupMenu("Error%%t|%s" % e)
	finally:
		# Restore editmode if it was enabled
		if is_editmode: Window.EditMode(1)
		Window.WaitCursor(0)

def bad_space_set_angle():
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
		
		# Get selected edges:
		sel = []
		for e in me.edges:
			if e.sel:
				sel.append(e.index)
		
		# Force only 2 edge selection:
		if len(sel) != 2:
			Draw.PupMenu("Error%t|Angle can be set for exactly 2 edges")
			return
		
		e1 = me.edges[sel[0]]
		e2 = me.edges[sel[1]]
		
		angle = Draw.Create(bad_get_angle(e1, e2))
		ret = Draw.PupBlock('Set the angle', (
			('Angle: ', angle, 0, 180, bad_set_angle.__doc__), 
		))
		if ret == 1:
			try:
				bad_set_angle(e1, e2, float(repr(angle)))
			except BadError, e:
				Draw.PupMenu("Error%%t|%s" % e)
	finally:
		# Restore editmode if it was enabled
		if is_editmode: Window.EditMode(1)
		Window.WaitCursor(0)

def bad_space_weld_edges():
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
		
		# Get selected edges:
		sel = []
		for e in me.edges:
			if e.sel:
				sel.append(e.index)
		
		# Force only 2 edge selection:
		if len(sel) != 2:
			Draw.PupMenu("Error%t|Only 2 edges can be welded at a time")
			return
		
		e1 = me.edges[sel[0]]
		e2 = me.edges[sel[1]]
		
		try:
			bad_weld_edges(me, e1, e2)
		except BadError, e:
			Draw.PupMenu("Error%%t|%s" % e)
	
	finally:
		# Restore editmode if it was enabled
		if is_editmode: Window.EditMode(1)
		Window.WaitCursor(0)

def bad_space_edges_menu():
	ret = Draw.PupMenu('BAD - Edges%t|Set length|Set angle|Weld')
	if ret == 1:
		bad_space_set_length()
	if ret == 2:
		bad_space_set_angle()
	elif ret == 3:
		bad_space_weld_edges()

def bad_space_handler():
	import Blender
	
	evt = Blender.event
	
	if evt == Draw.ZEROKEY:
		Blender.event = None
		bad_space_edges_menu()

if __name__ == '__main__':
	bad_space_edges_menu()

