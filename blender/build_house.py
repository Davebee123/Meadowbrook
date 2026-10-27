"""House A: a two-storey detached house on a 3 × 4 lot (12 × 16 m), in the style of docs/style.md.

Run: <blender-venv>/bin/python blender/build_house.py
Writes assets/buildings/house_a.glb and blender/src/house_a.blend. Origin is the lot centre at ground level; the front
faces -Y in Blender (+Z in Godot). Plants are not part of this model: scenes/lots/house_a_lot.tscn places them.
"""
import math
from contextlib import contextmanager

import toy  # first: it loads bpy, which makes bmesh and mathutils importable
import bmesh
import bpy
from mathutils import Matrix

# The house block, metres. x across the front, y from the front wall back, z up.
W = 8.4
FRONT, BACK = -2.5, 4.5
DEPTH = BACK - FRONT
FLOOR = 0.3                  # ground floor level
STOREY = 3.0
UPPER = FLOOR + STOREY       # 3.3
EAVES = UPPER + STOREY       # 6.3
PITCH = math.radians(40)
OVERHANG, VERGE = 0.35, 0.25
RISE = DEPTH / 2 * math.tan(PITCH)
RIDGE = EAVES + RISE
MID_Y = (FRONT + BACK) / 2
DOOR_X = -1.6
LOT_X, LOT_FRONT, LOT_BACK = 6.0, -8.0, 8.0


@contextmanager
def placed(k, m):
	"""Builds parts under an arbitrary matrix (the kit's frames only translate and turn about Z)."""
	old = k.xf
	k.xf = old @ m
	try:
		yield
	finally:
		k.xf = old


def window(k, cx, sill, w, h, arched=False, room=0.8, box=False, rng=None):
	"""A window in the current wall frame (wall face at y=0, outside -Y): a cut into a warm-lit room, glass set
	back 0.15, a chunky charcoal frame with glazing bars, a sand surround and sill. arched: round head."""
	x0, x1 = cx - w / 2, cx + w / 2
	top = sill + h
	spring = top - w / 2 if arched else top
	k.cut("interior_glow", x0, x1, -0.05, room, sill, spring)
	if arched:
		cut_half_disc(k, cx, spring, w / 2, -0.05, room)
	# Room: a floor at the sill and a piece of furniture against the back, so the glow has something in it.
	k.box("interior_wood", x0, x1, 0.2, room, sill - 0.02, sill + 0.02, bevel=0)
	k.box("interior_wood", cx - w * 0.3, cx + w * 0.15, room - 0.25, room - 0.02, sill, sill + h * 0.35, bevel=0.02)
	k.box("trim_sand", x0, x0 + 0.12, 0.17, 0.22, sill, spring, bevel=0.02)  # curtain
	# Glass and frame.
	k.box("glass", x0, x1, 0.13, 0.15, sill, spring, bevel=0)
	f, d0, d1 = 0.08, 0.06, 0.14
	k.box("frame", x0, x1, d0, d1, sill, sill + f, bevel=0.02)
	k.box("frame", x0, x0 + f, d0, d1, sill, spring, bevel=0.02)
	k.box("frame", x1 - f, x1, d0, d1, sill, spring, bevel=0.02)
	k.box("frame", cx - 0.025, cx + 0.025, d0 + 0.01, d1, sill, spring, bevel=0.01)
	bar = sill + (spring - sill) * 0.55
	k.box("frame", x0, x1, d0 + 0.01, d1, bar - 0.025, bar + 0.025, bevel=0.01)
	if arched:
		k.box("glass", x0, x1, 0.13, 0.15, spring - 0.01, spring + 0.01, bevel=0)
		half_annulus(k, "glass", cx, spring, 0.0, w / 2, 0.13, 0.15)
		half_annulus(k, "frame", cx, spring, w / 2 - f, w / 2, d0, d1)
		half_annulus(k, "trim_sand", cx, spring, w / 2, w / 2 + 0.12, -0.04, 0.0)
	else:
		k.box("frame", x0, x1, d0, d1, top - f, top, bevel=0.02)
		k.box("trim_sand", x0 - 0.12, x1 + 0.12, -0.04, 0.0, top, top + 0.12)
	# Surround and sill.
	k.box("trim_sand", x0 - 0.12, x0, -0.04, 0.0, sill, spring)
	k.box("trim_sand", x1, x1 + 0.12, -0.04, 0.0, sill, spring)
	k.box("trim_sand", x0 - 0.2, x1 + 0.2, -0.08, 0.06, sill - 0.1, sill)
	if box:
		flower_box(k, cx, sill, w)


def flower_box(k, cx, sill, w):
	"""A timber window box under the sill; its plants come from the lot scene (here: soil only)."""
	k.box("wood", cx - w / 2 - 0.05, cx + w / 2 + 0.05, -0.34, -0.1, sill - 0.36, sill - 0.12, bevel=0.03)
	k.box("soil", cx - w / 2, cx + w / 2, -0.3, -0.14, sill - 0.16, sill - 0.13, bevel=0)


def cut_half_disc(k, cx, z, r, y0, y1):
	"""Registers a half-cylinder hole (an arched head) for the next shell()."""
	bm = bmesh.new()
	bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=r, radius2=r, depth=y1 - y0,
		matrix=Matrix.Translation((cx, (y0 + y1) / 2, z)) @ Matrix.Rotation(math.radians(90), 4, "X"))
	bmesh.ops.transform(bm, matrix=k.xf, verts=bm.verts)
	me = bpy.data.meshes.new("cutter")
	bm.to_mesh(me)
	bm.free()
	k.cutters.append((me, "interior_glow"))


def half_annulus(k, mat, cx, z, r0, r1, y0, y1, segments=16):
	"""A half ring standing in the XZ plane (r0 = 0 gives a half disc), from y0 to y1."""
	bm = bmesh.new()
	rings = []
	for y in (y0, y1):
		outer = [bm.verts.new((cx + math.cos(a) * r1, y, z + math.sin(a) * r1))
			for a in (math.pi * i / segments for i in range(segments + 1))]
		inner = [bm.verts.new((cx + math.cos(a) * max(r0, 0.001), y, z + math.sin(a) * max(r0, 0.001)))
			for a in (math.pi * i / segments for i in range(segments + 1))]
		rings.append((outer, inner))
	(o0, i0), (o1, i1) = rings
	for i in range(segments):
		bm.faces.new((o0[i], o0[i + 1], i0[i + 1], i0[i]))
		bm.faces.new((o1[i], i1[i], i1[i + 1], o1[i + 1]))
		bm.faces.new((o0[i], o1[i], o1[i + 1], o0[i + 1]))
		bm.faces.new((i0[i], i0[i + 1], i1[i + 1], i1[i]))
	for a, b in ((0, segments), ):
		bm.faces.new((o0[a], i0[a], i1[a], o1[a]))
		bm.faces.new((o0[b], o1[b], i1[b], i0[b]))
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
	k._merge(bm, mat, smooth=True)


def front(k):
	with k.frame(0, FRONT, 0, 0):
		window(k, -3.25, FLOOR + 0.9, 0.9, 1.4)
		window(k, 1.9, FLOOR + 0.8, 2.0, 1.5)
		for x, box in ((-2.6, True), (2.6, True)):
			window(k, x, UPPER + 0.9, 1.0, 1.4, box=box)
		window(k, 0.0, UPPER + 0.85, 1.0, 1.55, arched=True)
		door(k, DOOR_X)


def door(k, cx):
	"""Sage panelled door with a glazed top, charcoal frame, canopy on brackets, two steps and a gooseneck lamp."""
	x0, x1, top = cx - 0.5, cx + 0.5, FLOOR + 2.2
	k.cut("interior_glow", x0 - 0.1, x1 + 0.1, -0.05, 0.15, FLOOR, top + 0.1)
	k.box("frame", x0 - 0.1, x0, -0.02, 0.15, FLOOR, top + 0.1, bevel=0.02)
	k.box("frame", x1, x1 + 0.1, -0.02, 0.15, FLOOR, top + 0.1, bevel=0.02)
	k.box("frame", x0 - 0.1, x1 + 0.1, -0.02, 0.15, top, top + 0.1, bevel=0.02)
	k.box("door_sage", x0, x1, 0.08, 0.15, FLOOR, top, bevel=0.02)
	for z0, z1 in ((FLOOR + 0.2, FLOOR + 0.95), (FLOOR + 1.1, FLOOR + 1.45)):
		k.box("door_sage", x0 + 0.12, x1 - 0.12, 0.04, 0.08, z0, z1, bevel=0.02)
	k.box("interior_glow", x0 + 0.15, x1 - 0.15, 0.06, 0.08, FLOOR + 1.6, top - 0.15, bevel=0)
	k.box("frame", x0 + 0.12, x1 - 0.12, 0.03, 0.07, FLOOR + 1.55, FLOOR + 1.6, bevel=0.01)
	k.sphere("brass", x1 - 0.12, 0.03, FLOOR + 1.05, 0.04)
	# Steps up to the floor level, and the trim around the door.
	k.box("trim_tan", x0 - 0.4, x1 + 0.4, -0.75, 0.0, 0.0, 0.15)
	k.box("trim_tan", x0 - 0.3, x1 + 0.3, -0.4, 0.0, 0.0, FLOOR)
	k.box("trim_sand", x0 - 0.22, x0 - 0.1, -0.04, 0.0, FLOOR, top + 0.1)
	k.box("trim_sand", x1 + 0.1, x1 + 0.22, -0.04, 0.0, FLOOR, top + 0.1)
	# Canopy: a chunky slab on two brackets.
	cz = top + 0.35
	k.box("trim_tan", x0 - 0.45, x1 + 0.45, -1.0, 0.0, cz, cz + 0.16)
	k.box("roof_slate", x0 - 0.4, x1 + 0.4, -0.95, -0.02, cz + 0.16, cz + 0.22, bevel=0.02)
	for x in (x0 - 0.3, x1 + 0.3):
		k.prism("trim_tan", [(0.0, cz), (-0.7, cz), (0.0, cz - 0.6)], x - 0.05, x + 0.05)
	gooseneck(k, x1 + 0.55, top - 0.2)


def gooseneck(k, x, z):
	"""A wall lamp like the reference's: a curved arm, a cone shade and a warm bulb."""
	pts = [(x, -0.02, z), (x, -0.18, z + 0.18), (x, -0.36, z + 0.22), (x, -0.48, z + 0.12)]
	for a, b in zip(pts, pts[1:]):
		k.rod("frame", a, b, 0.022)
		k.sphere("frame", *b, 0.024, subdiv=1)
	k.box("frame", x - 0.07, x + 0.07, -0.04, 0.0, z - 0.1, z + 0.1, bevel=0.015)
	sx, sy, sz = pts[-1]
	k.cylinder("frame", sx, sy, sz - 0.14, sz, 0.12, r_top=0.03, segments=16)
	k.sphere("lamp_glow", sx, sy, sz - 0.14, 0.05, subdiv=2)


def sides_and_back(k):
	for side in (1, -1):
		with k.frame(side * W / 2, MID_Y, 0, side * 90):
			window(k, 0.6 * side, FLOOR + 0.9, 0.9, 1.4)
			window(k, -1.4 * side, UPPER + 0.9, 0.9, 1.4)
	with k.frame(0, BACK, 0, 180):
		for x in (-2.2, 2.2):
			window(k, x, FLOOR + 0.9, 1.2, 1.4)
			window(k, x, UPPER + 0.9, 1.0, 1.4)


def bands(k):
	"""Plinth, belt course and the eaves band: chunky sand trims all round."""
	k.ring("trim_sand", -W / 2 - 0.04, W / 2 + 0.04, FRONT - 0.04, BACK + 0.04, 0.0, FLOOR, 0.1)
	k.ring("trim_sand", -W / 2 - 0.06, W / 2 + 0.06, FRONT - 0.06, BACK + 0.06, UPPER - 0.12, UPPER + 0.13, 0.12)
	k.ring("trim_sand", -W / 2 - 0.05, W / 2 + 0.05, FRONT - 0.05, BACK + 0.05, EAVES - 0.25, EAVES, 0.12)


def roof(k):
	"""Gable roof, ridge along x: stucco gables, rounded shingle courses, fascias, verges, ridge and chimney."""
	k.prism("stucco", [(FRONT, EAVES), (BACK, EAVES), (MID_Y, RIDGE)], -W / 2, W / 2)
	length = W + 2 * VERGE
	slope = (DEPTH / 2 + OVERHANG) / math.cos(PITCH)
	course = 0.3
	n = int(slope / course) + 1
	for side in (-1, 1):  # -1: front slope, falls toward -Y
		# Frame: origin at the ridge, v runs down the slope, w out of the roof.
		rot = Matrix.Rotation(-side * PITCH, 4, "X")
		base = Matrix.Translation((0, MID_Y, RIDGE + 0.06)) @ rot
		with placed(k, base):
			s = side
			k.box("roof_slate", -length / 2, length / 2, *sorted((0.0, s * slope)), -0.16, -0.04, bevel=0.03)
			# Courses: each strip hinges at its upper edge and lifts 4° at the lower one, so the rows step.
			for i in range(n):
				v0 = i * course
				v1 = min(course + 0.06, slope - v0)
				with placed(k, Matrix.Translation((0, s * v0, 0)) @ Matrix.Rotation(s * math.radians(4), 4, "X")):
					k.box("roof_slate", -length / 2, length / 2, *sorted((0.0, s * v1)), -0.04, 0.03, bevel=0.025)
			# Fascia board along the eaves.
			k.box("trim_tan", -length / 2, length / 2, *sorted((s * (slope - 0.06), s * (slope + 0.06))), -0.36,
				-0.02, bevel=0.03)
			# Verge boards along the gable rakes.
			for x in (-length / 2, length / 2 - 0.12):
				k.box("trim_tan", x, x + 0.12, *sorted((0.0, s * slope)), -0.3, 0.0, bevel=0.03)
	k.rod("roof_slate", (-length / 2, MID_Y, RIDGE + 0.08), (length / 2, MID_Y, RIDGE + 0.08), 0.13, segments=12)
	# Chimney on the back slope.
	cx, cy = 2.4, MID_Y + 1.5
	k.box("stucco", cx - 0.35, cx + 0.35, cy - 0.35, cy + 0.35, EAVES + 0.5, RIDGE + 1.0)
	k.box("trim_sand", cx - 0.45, cx + 0.45, cy - 0.45, cy + 0.45, RIDGE + 1.0, RIDGE + 1.15)
	k.cylinder("trim_tan", cx, cy, RIDGE + 1.15, RIDGE + 1.4, 0.12, segments=12)


def lot(k):
	"""Lawn, a paver path from the steps to the street, and timber-edged beds along the front."""
	k.box("lawn", -LOT_X, LOT_X, LOT_FRONT, LOT_BACK, 0.0, 0.03, bevel=0)
	step_front = FRONT - 0.75
	y = step_front - 0.05
	while y - 0.55 > LOT_FRONT:
		for x in (DOOR_X - 0.3, DOOR_X + 0.3):
			k.box("pavers", x - 0.27, x + 0.27, y - 0.55, y, 0.0, 0.07, bevel=0.025)
		y -= 0.6
	for x0, x1 in ((-W / 2 + 0.1, DOOR_X - 0.95), (DOOR_X + 0.95, W / 2 - 0.1)):
		k.ring("wood", x0, x1, FRONT - 1.0, FRONT - 0.1, 0.0, 0.16, 0.08)
		k.box("soil", x0 + 0.06, x1 - 0.06, FRONT - 0.94, FRONT - 0.16, 0.0, 0.12, bevel=0)


def collision():
	bm = bmesh.new()
	for p in ((-W / 2, W / 2, FRONT, BACK, 0, EAVES), (DOOR_X - 0.9, DOOR_X + 0.9, FRONT - 0.75, FRONT, 0, 0.15)):
		part = toy.Kit._box_bm(*p, 0)
		me = bpy.data.meshes.new("p")
		part.to_mesh(me)
		part.free()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
	me = bpy.data.meshes.new("house_a-colonly")
	bm.to_mesh(me)
	bm.free()
	bpy.context.scene.collection.objects.link(bpy.data.objects.new("house_a-colonly", me))


if __name__ == "__main__":
	k = toy.new_kit(bevel=0.05, segments=2)
	front(k)
	sides_and_back(k)
	k.shell("stucco", -W / 2, W / 2, FRONT, BACK, 0.0, EAVES)
	bands(k)
	roof(k)
	lot(k)
	collision()
	toy.export(k, "house_a", "buildings")
