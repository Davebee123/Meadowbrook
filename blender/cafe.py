"""The café on its 3 × 3 lot (12 × 12 m), built to docs/style.md and exported to assets/buildings/cafe.glb.

Run: <blender-venv>/bin/python blender/cafe.py
Origin is the lot centre at ground level; the front faces -Y in Blender, which is +Z in Godot.
The building is 9 × 7 m at the back of the lot, two storeys, with a 4 m terrace in front.
"""
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Kit  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "buildings", "cafe.glb")

# Building block, metres.
W, FRONT, BACK = 9.0, -1.5, 5.5          # x from -W/2 to W/2; front and back faces in y
FLOOR = 0.15                             # ground floor level above the terrace
GROUND_STOREY, UPPER_STOREY = 4.0, 3.0
UPPER = FLOOR + GROUND_STOREY            # 4.15
ROOF = UPPER + UPPER_STOREY              # 7.15
PARAPET = ROOF + 0.8                     # 7.95
DEPTH = BACK - FRONT
MID_Y = (FRONT + BACK) / 2

# Shopfront, in the front wall's frame (wall face at y=0).
SHOP_X = 4.1                             # opening from -SHOP_X to SHOP_X
RISER_TOP = FLOOR + 0.5                  # 0.65
GLAZING_TOP = RISER_TOP + 2.6            # 3.25, the awning fixes here
FASCIA_TOP = GLAZING_TOP + 0.6           # 3.85
ROOM_DEPTH = 3.0                         # the café room behind the shopfront


def front_wall(k, rng):
	with k.frame(0, FRONT, 0, 0):
		# The café room: one cut through the ground floor; its faces take the warm interior plaster.
		k.cut("plaster_warm", -SHOP_X, SHOP_X, -0.05, ROOM_DEPTH, FLOOR, FASCIA_TOP - 0.05)
		# Pilasters either side of the door bay.
		for x0, x1 in ((-1.1, -0.75), (0.75, 1.1)):
			k.box("brick", x0, x1, -0.05, 0.3, 0.4, GLAZING_TOP)
		for x0, x1 in ((-SHOP_X, -1.1), (1.1, SHOP_X)):
			shop_window(k, x0, x1)
		door_bay(k)
		# Fascia with the sign, and its cap.
		k.box("frame_dark", -SHOP_X, SHOP_X, -0.08, 0.3, GLAZING_TOP, FASCIA_TOP)
		k.box("frame_dark", -SHOP_X - 0.1, SHOP_X + 0.1, -0.14, 0.3, FASCIA_TOP, FASCIA_TOP + 0.1)
		k.text("cream", "CAFÉ", 0.42, 0.024, 0.0, -0.09, GLAZING_TOP + 0.13)
		awning(k)
		for x in (-0.925, 0.925):
			k.lantern(x, -0.2, 2.65)
		# Upper floor: four windows, flower boxes on two.
		for i, x in enumerate((-3.375, -1.125, 1.125, 3.375)):
			k.window(x, UPPER + 0.9, 0.9, 1.4, glass="glass_lit" if i in (1, 3) else "glass_dark")
			if i in (0, 3):
				k.window_box(x, UPPER + 0.9, 1.0, rng)
		# Plinth, broken at the door; it runs in front of the pilasters, which stand on it.
		for x0, x1 in ((-W / 2 - 0.05, -0.75), (0.75, W / 2 + 0.05)):
			k.box("stone", x0, x1, -0.1, 0.2, 0.0, 0.4)
		k.box("stone", -0.75, 0.75, -0.4, 0.15, 0.0, FLOOR)  # door step


def shop_window(k, x0, x1):
	"""A shop window between x0 and x1: painted riser panel, glazing, frame, two mullions and a transom."""
	k.box("frame_dark", x0, x1, 0.0, 0.2, 0.4, RISER_TOP)
	k.box("frame_dark", x0 - 0.02, x1 + 0.02, -0.06, 0.2, RISER_TOP - 0.03, RISER_TOP + 0.03)
	k.box("glass_clear", x0, x1, 0.14, 0.16, RISER_TOP, GLAZING_TOP, bevel=0)
	f = 0.08
	k.box("frame_dark", x0, x0 + f, 0.04, 0.2, RISER_TOP, GLAZING_TOP)
	k.box("frame_dark", x1 - f, x1, 0.04, 0.2, RISER_TOP, GLAZING_TOP)
	k.box("frame_dark", x0, x1, 0.04, 0.2, GLAZING_TOP - f, GLAZING_TOP)
	transom = GLAZING_TOP - 0.6
	k.box("frame_dark", x0, x1, 0.06, 0.18, transom - 0.03, transom + 0.03)
	for t in (1 / 3, 2 / 3):
		x = x0 + (x1 - x0) * t
		k.box("frame_dark", x - 0.03, x + 0.03, 0.06, 0.18, RISER_TOP, GLAZING_TOP)


def door_bay(k):
	"""Glazed door 1.0 × 2.4 with sidelights and a transom light above."""
	top = FLOOR + 2.4
	k.box("glass_clear", -0.75, 0.75, 0.14, 0.16, FLOOR, GLAZING_TOP, bevel=0)
	f = 0.1
	for x0, x1 in ((-0.75, -0.75 + f), (-0.5 - f / 2, -0.5 + f / 2), (0.5 - f / 2, 0.5 + f / 2), (0.75 - f, 0.75)):
		k.box("frame_dark", x0, x1, 0.04, 0.2, FLOOR, GLAZING_TOP)
	k.box("frame_dark", -0.75, 0.75, 0.04, 0.2, top, top + f)
	k.box("frame_dark", -0.75, 0.75, 0.04, 0.2, GLAZING_TOP - f, GLAZING_TOP)
	# The door leaf: rails and a kick panel, glass between.
	k.box("frame_dark", -0.45, 0.45, 0.06, 0.12, FLOOR, FLOOR + 0.35)
	k.box("frame_dark", -0.45, 0.45, 0.06, 0.12, top - 0.1, top)
	k.box("frame_dark", -0.45, -0.37, 0.06, 0.12, FLOOR, top)
	k.box("frame_dark", 0.37, 0.45, 0.06, 0.12, FLOOR, top)
	k.cylinder("brass", 0.33, 0.03, FLOOR + 0.9, FLOOR + 1.3, 0.015, segments=8)
	k.box("frame_dark", -0.75, 0.75, 0.04, 0.2, FLOOR, FLOOR + 0.06)


def awning(k):
	"""Striped awning fixed under the fascia: 1.8 m deep, falling 20°, with side cheeks, valance and arms."""
	depth, fall = 1.8, math.radians(20)
	y_out = -0.08 - depth * math.cos(fall)
	z_out = GLAZING_TOP - depth * math.sin(fall)
	half = SHOP_X - 0.1
	t = 0.03
	k.prism("awning_charcoal", [(-0.08, GLAZING_TOP), (y_out, z_out), (y_out, z_out - t), (-0.08, GLAZING_TOP - t)],
		-half, half)
	k.box("awning_charcoal", -half, half, y_out - 0.02, y_out, z_out - 0.13, z_out, bevel=0)
	for x in (-half, half - 0.02):
		k.prism("awning_charcoal", [(-0.08, GLAZING_TOP), (y_out, z_out), (-0.08, z_out)], x, x + 0.02)
	for x in (-half + 0.3, half - 0.3):
		k.rod("metal", (x, -0.05, z_out - 0.25), (x, y_out + 0.05, z_out - 0.02), 0.015)


def side_and_back_walls(k):
	for side in (1, -1):
		# Side walls: local x runs from the front (-3.5) to the back (+3.5) on the right, mirrored on the left.
		with k.frame(side * W / 2, MID_Y, 0, side * 90):
			sx = -2.0 * side  # the side shop window opens into the café room
			k.window(sx, FLOOR + 0.8, 1.6, 2.0, glass="glass_clear", recess=0.15, cut_depth=0.6)
			for x in (-1.6, 1.6):
				k.window(x, UPPER + 0.9, 0.9, 1.4, glass="glass_lit" if x * side < 0 else "glass_dark")
			k.box("stone", -DEPTH / 2, DEPTH / 2, -0.05, 0.0, 0.0, 0.4)
	with k.frame(0, BACK, 0, 180):
		k.cut("brick", 1.95, 3.05, -0.05, 0.15, FLOOR, FLOOR + 2.1)
		k.box("wood", 2.0, 3.0, 0.1, 0.15, FLOOR, FLOOR + 2.1)
		k.box("stone", 1.8, 3.2, -0.35, 0.15, 0.0, FLOOR)
		k.window(-1.5, FLOOR + 0.9, 0.9, 1.4)
		for x in (-1.8, 1.8):
			k.window(x, UPPER + 0.9, 0.9, 1.4)
		k.lantern(2.5, -0.15, 2.55)
		k.box("stone", -W / 2, W / 2, -0.05, 0.0, 0.0, 0.4)


def roof(k):
	k.cut("brick", -W / 2 + 0.25, W / 2 - 0.25, FRONT + 0.25, BACK - 0.25, ROOF, PARAPET + 0.1)
	k.box("roof_flat", -W / 2 + 0.25, W / 2 - 0.25, FRONT + 0.25, BACK - 0.25, ROOF, ROOF + 0.03, bevel=0)
	# String course between the floors, cornice and coping.
	k.ring("stone", -W / 2 - 0.04, W / 2 + 0.04, FRONT - 0.04, BACK + 0.04, UPPER - 0.05, UPPER + 0.1, 0.06)
	k.ring("stone", -W / 2 - 0.25, W / 2 + 0.25, FRONT - 0.25, BACK + 0.25, PARAPET - 0.4, PARAPET - 0.15, 0.3)
	k.ring("stone", -W / 2 - 0.03, W / 2 + 0.03, FRONT - 0.03, BACK + 0.03, PARAPET, PARAPET + 0.08, 0.31)
	# Rooftop units, a hatch and a vent.
	for x, y in ((2.2, 3.6), (-1.6, 4.2)):
		k.box("metal_light", x - 0.55, x + 0.55, y - 0.4, y + 0.4, ROOF, ROOF + 0.75)
		k.box("metal", x - 0.45, x + 0.45, y - 0.42, y - 0.4, ROOF + 0.1, ROOF + 0.6, bevel=0)
		k.cylinder("metal", x, y, ROOF + 0.75, ROOF + 0.8, 0.3)
	k.box("metal_light", -3.2, -2.3, 0.6, 1.5, ROOF, ROOF + 0.35)
	k.cylinder("metal", 3.4, 0.4, ROOF, ROOF + 0.6, 0.07)


def interior(k):
	"""Enough of the room to read through the glass: floor, counter, shelves and pendant lights."""
	back = FRONT + ROOM_DEPTH
	k.box("wood", -SHOP_X, SHOP_X, FRONT + 0.15, back, FLOOR, FLOOR + 0.01, bevel=0)
	k.box("wood", -2.5, 2.5, back - 0.9, back - 0.3, FLOOR, FLOOR + 0.95)
	k.box("stone", -2.6, 2.6, back - 0.95, back - 0.25, FLOOR + 0.95, FLOOR + 1.0)
	k.box("metal_light", 0.8, 1.4, back - 0.75, back - 0.35, FLOOR + 1.0, FLOOR + 1.45)
	for z in (1.5, 2.0):
		k.box("wood", -3.5, 3.5, back - 0.25, back, FLOOR + z, FLOOR + z + 0.04, bevel=0)
	for x in (-2.4, 0.0, 2.4):
		k.rod("metal", (x, FRONT + 1.2, FASCIA_TOP - 0.05), (x, FRONT + 1.2, 2.9), 0.006)
		k.sphere("lamp_glow", x, FRONT + 1.2, 2.82, 0.12, subdiv=2)


def terrace(k, rng):
	k.box("paving", -6, 6, -6, 6, 0.0, 0.02, bevel=0)
	# Planting bed along the left of the building.
	k.ring("stone", -5.9, -4.65, FRONT + 0.1, BACK + 0.3, 0.0, 0.15, 0.1)
	k.box("soil", -5.8, -4.75, FRONT + 0.2, BACK + 0.2, 0.02, 0.12, bevel=0)
	k.shrubs(-5.6, -4.95, FRONT + 1.6, BACK, 0.12, 0.35, rng, count=7)
	k.tree(-5.3, FRONT + 0.6, 0.12, 4.2, rng)
	# Planters along the front edge of the terrace, and two by the door.
	for x in (-5.0, -3.6, 3.6, 5.0):
		k.planter(x, -5.5, 1.2, 0.5, 0.5, rng)
	for x in (-1.45, 1.45):
		k.planter(x, FRONT - 0.35, 0.6, 0.4, 0.45, rng)
	# Bistro tables under the awning, umbrella tables in front.
	for x in (-2.6, 2.6):
		k.table(x, -2.5)
		k.chair(x - 0.55, -2.5, -90)
		k.chair(x + 0.55, -2.5, 90)
	for x in (-3.2, 3.2):
		k.table(x, -4.3)
		k.umbrella(x, -4.3)
		k.chair(x, -4.85, 0)
		k.chair(x - 0.55, -4.1, -90)
		k.chair(x + 0.55, -4.1, 90)
	menu_board(k, 1.5, -3.9)


def menu_board(k, x, y):
	"""An A-frame chalkboard."""
	h = 0.9
	for s in (1, -1):
		k.prism("wood", [(y, 0.02), (y + s * 0.2, 0.02), (y + s * 0.02, h), (y, h)], x - 0.3, x + 0.3)
		k.prism("frame_dark", [(y - s * 0.005, 0.12), (y + s * 0.17, 0.12), (y + s * 0.02, h - 0.08),
			(y - s * 0.005, h - 0.08)], x - 0.25, x + 0.25)


def lights():
	"""Real lights for the pendants and lanterns, exported with the model so Godot lights the terrace too."""
	spots = [((x, FRONT + 1.2, 2.82), 25.0) for x in (-2.4, 0.0, 2.4)]
	spots += [((x, FRONT - 0.2, 2.6), 8.0) for x in (-0.925, 0.925)]
	spots += [((-2.5, BACK + 0.15, 2.5), 8.0)]
	for i, (loc, watts) in enumerate(spots):
		light = bpy.data.lights.new(f"light{i}", "POINT")
		light.energy = watts
		light.color = (1.0, 0.72, 0.42)
		light.shadow_soft_size = 0.08
		obj = bpy.data.objects.new(f"light{i}", light)
		obj.location = loc
		bpy.context.scene.collection.objects.link(obj)


def collision(k):
	"""A separate collision-only mesh for Godot: the building and the solid furniture."""
	import bmesh
	bm = bmesh.new()
	parts = [(-W / 2, W / 2, FRONT, BACK, 0, PARAPET)]
	parts += [(x - 0.6, x + 0.6, -5.75, -5.25, 0, 0.5) for x in (-5.0, -3.6, 3.6, 5.0)]
	parts += [(x - 0.3, x + 0.3, FRONT - 0.55, FRONT - 0.15, 0, 0.45) for x in (-1.45, 1.45)]
	parts += [(x - 0.35, x + 0.35, y - 0.35, y + 0.35, 0, 0.75) for x, y in
		((-2.6, -2.5), (2.6, -2.5), (-3.2, -4.3), (3.2, -4.3))]
	for p in parts:
		part = Kit._box_bm(*p, 0)
		me = bpy.data.meshes.new("p")
		part.to_mesh(me)
		part.free()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
	me = bpy.data.meshes.new("cafe-colonly")
	bm.to_mesh(me)
	bm.free()
	obj = bpy.data.objects.new("cafe-colonly", me)
	bpy.context.scene.collection.objects.link(obj)
	return obj


def build():
	bpy.ops.wm.read_factory_settings(use_empty=True)
	rng = np.random.default_rng(12)
	k = Kit(os.path.join(HERE, ".cache"))
	front_wall(k, rng)
	side_and_back_walls(k)
	roof(k)
	k.shell("brick", -W / 2, W / 2, FRONT, BACK, 0.0, PARAPET)
	interior(k)
	terrace(k, rng)
	obj = k.build_object("cafe")
	collision(k)
	lights()
	return obj


if __name__ == "__main__":
	cafe = build()
	os.makedirs(os.path.dirname(OUT), exist_ok=True)
	bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_yup=True, export_apply=True,
		export_lights=True)
	print("faces", len(cafe.data.polygons), "materials", len(cafe.data.materials), "->", OUT)
