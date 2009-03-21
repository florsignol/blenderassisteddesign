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

from Blender import Mesh
from Blender.Mathutils import Vector, LineIntersect, AngleBetweenVecs, CrossVecs, RotationMatrix, TranslationMatrix
from math import *

class BadError(Exception):
	pass

def bad_get_length(edge):
	"""
	Retrieve the length of an edge.
	"""
	
	ev = edge.v2.co-edge.v1.co
	return ev.length

def bad_set_length(edge, length):
	"""
	Set the length of an edge.
	"""
	
	ev = edge.v2.co-edge.v1.co # v1->v2
	n = ev.copy().normalize()
	inc = (length - ev.length) / 2
	
	edge.v1.co -= inc * n;
	edge.v2.co += inc * n;

def bad_get_angle(e1, e2):
	"""
	Retrieve the angle between two edges.
	"""
	# Be sure that e1 is the longer edge:
	if e2.length > e1.length:
		tmp = e1
		e1 = e2
		e2 = tmp
		del tmp
	
	ev1 = e1.v2.co-e1.v1.co
	ev2 = e2.v2.co-e2.v1.co
	
	# Calculate current angle
	angle = AngleBetweenVecs(ev1, ev2)
	
	if angle > 90.0:
		# Flip one edge vector to get the correct corners
		ev2.negate()
		cangle = AngleBetweenVecs(ev1, ev2)
	
	return angle

def bad_set_angle(e1, e2, angle):
	"""
	Reset the smaller angle between two edges, respect to the longer edge.
	"""
	
	# Be sure that e1 is the longer edge:
	if e2.length > e1.length:
		tmp = e1
		e1 = e2
		e2 = tmp
		del tmp
	
	ev1 = e1.v2.co-e1.v1.co
	ev2 = e2.v2.co-e2.v1.co
	
	# Calculate current angle
	cangle = AngleBetweenVecs(ev1, ev2)
	
	if cangle > 90.0:
		# Flip one edge vector to get the correct corners
		ev2.negate()
		cangle = AngleBetweenVecs(ev1, ev2)
	
	if cangle == angle:
		return
	
	# Get the intersection point:
	pr = LineIntersect(e1.v1.co, e1.v2.co, e2.v1.co, e2.v2.co)
	if pr is None:
		raise BadError, 'Edges do not intersect'
	(p, r) = pr
	if p != r:
		raise BadError, 'Edges do not intersect'
	del pr, r
	
	# Rotate the shorter edge around point P
	rot = TranslationMatrix(-p)
	rot *= RotationMatrix(angle-cangle, 4, 'r', CrossVecs(ev1, ev2))
	rot *= TranslationMatrix(p)
	e2.v1.co *= rot
	e2.v2.co *= rot
	
	rot *= TranslationMatrix(p + e2.v1.co)

def bad_weld_edges(me, e1, e2):
	"""
	Creates a vertex at the crossing point of two edges.
	"""
	intr = LineIntersect(e1.v1.co, e1.v2.co, e2.v1.co, e2.v2.co)
	if intr is None:
		raise BadError, 'Edges do not intersect'
	(p, r) = intr
	if p != r:
		raise BadError, 'Edges do not intersect'
	del intr, r
	
	def test_angles(v1, v2, r):
		a1 = AngleBetweenVecs(v1, r)
		a2 = AngleBetweenVecs(r, v2)
		a = AngleBetweenVecs(v1, v2)
		if a == 180:
			raise BadError, 'Edges overlap'
		if (a1 + a2) > a + 0.0005 or a - 0.0005 > (a1 + a2):
			raise BadError, 'Intersection not on the edge'
		if a1 == 0 or a2 == 0:
			raise BadError, 'Intersection at the end point of the edege'
	
	test_angles(e1.v1.co, e1.v2.co, p)
	test_angles(e2.v1.co, e2.v2.co, p)
	
	# Edges intersect at point p, weld them together:
	me.verts.extend(p)
	P = me.verts[-1]
	
	me.edges.extend(
		(e1.v1, P),
		(P, e1.v2),
		(e2.v1, P),
		(P, e2.v2)
	)
	
	# Remove old edges:
	me.edges.delete(e1, e2)

