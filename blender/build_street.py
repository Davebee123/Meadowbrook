"""Street pieces and props for assets/street/. Origin at the base, centred; fronts face -Y (+Z in Godot).

Run: <blender-venv>/bin/python blender/build_street.py [name ...]
"""
import math
import sys

import toy  # first: it loads bpy, which makes bmesh and mathutils importable
import numpy as np


def street_straight(k, rng):
	"""A 4 m length of street, 12 m across (three tiles): 2 m sidewalk, curb, 7.5 m road, curb, 2 m sidewalk.
	Runs along x; tiles end to end."""
	k.box("asphalt", -2.0, 2.0, -3.75, 3.75, 0.0, 0.02, bevel=0)
	k.box("lane_paint", -0.9, 0.9, -0.06, 0.06, 0.02, 0.026, bevel=0)
	for side in (-1, 1):
		y_curb = side * 3.75
		k.box("curb", -2.0, 2.0, *sorted((y_curb, y_curb + side * 0.25)), 0.0, 0.15, bevel=0.04)
		y0 = y_curb + side * 0.25
		for i in range(4):
			for j in range(2):
				ya = y0 + side * j * 0.875
				k.box("pavers", -2.0 + i * 1.0 + 0.02, -1.0 + i * 1.0 - 0.02, *sorted((ya + side * 0.02,
					ya + side * 0.855)), 0.0, 0.14, bevel=0.03)


def street_lamp(k, rng):
	"""A 4 m lamp post: fluted base, slim post, lantern with a warm glass."""
	k.cylinder("frame", 0, 0, 0.0, 0.5, 0.16, r_top=0.11, segments=16)
	k.cylinder("frame", 0, 0, 0.5, 3.5, 0.06, r_top=0.05, segments=12)
	k.cylinder("frame", 0, 0, 3.45, 3.55, 0.1, segments=12)
	k.box("frame", -0.16, 0.16, -0.16, 0.16, 3.55, 3.6, bevel=0.015)
	k.box("lamp_glow", -0.12, 0.12, -0.12, 0.12, 3.6, 3.95, bevel=0.01)
	for x in (-0.13, 0.13):
		for y in (-0.13, 0.13):
			k.box("frame", x - 0.02, x + 0.02, y - 0.02, y + 0.02, 3.6, 3.95, bevel=0.005)
	k.cylinder("frame", 0, 0, 3.95, 4.15, 0.22, r_top=0.04, segments=4)
	k.sphere("frame", 0, 0, 4.17, 0.04, subdiv=1)


def mailbox(k, rng):
	"""A post mailbox: rounded box on a timber post, with a flag."""
	k.box("wood", -0.05, 0.05, -0.05, 0.05, 0.0, 1.0, bevel=0.015)
	k.box("door_sage", -0.13, 0.13, -0.25, 0.2, 1.0, 1.2, bevel=0.03)
	k.cylinder("door_sage", 0, 0, 1.2, 1.2001, 0.13, segments=16)
	k.rod("door_sage", (-0.0, -0.25, 1.2), (0.0, 0.2, 1.2), 0.13, segments=16)
	k.box("trim_tan", 0.135, 0.15, 0.0, 0.03, 1.1, 1.45, bevel=0.005)
	k.box("trim_tan", 0.135, 0.15, 0.03, 0.15, 1.36, 1.45, bevel=0.005)


def bench(k, rng):
	"""A park bench, 1.6 m: chunky timber slats on charcoal frames."""
	for x in (-0.65, 0.65):
		k.box("frame", x - 0.04, x + 0.04, -0.22, 0.22, 0.0, 0.42, bevel=0.015)
		k.box("frame", x - 0.04, x + 0.04, 0.16, 0.24, 0.42, 0.85, bevel=0.015)
	for y in (-0.2, -0.06, 0.08):
		k.box("wood", -0.8, 0.8, y, y + 0.12, 0.42, 0.47, bevel=0.02)
	for z in (0.55, 0.7):
		k.box("wood", -0.8, 0.8, 0.18, 0.23, z, z + 0.1, bevel=0.02)


def picket_fence(k, rng):
	"""A 2 m picket fence section, 0.9 m tall, rounded pickets; butts against the next section."""
	for z in (0.25, 0.65):
		k.box("stucco", -1.0, 1.0, 0.0, 0.05, z, z + 0.08, bevel=0.015)
	for i in range(13):
		x = -0.925 + i * 0.154
		k.box("stucco", x - 0.04, x + 0.04, -0.04, 0.0, 0.0, 0.8, bevel=0.02)
	for x in (-0.98, 0.98):
		k.box("stucco", x - 0.05, x + 0.05, -0.04, 0.09, 0.0, 0.95, bevel=0.02)


ASSETS = {
	"street_straight": street_straight,
	"street_lamp": street_lamp,
	"mailbox": mailbox,
	"bench": bench,
	"picket_fence": picket_fence,
}


if __name__ == "__main__":
	names = [a for a in sys.argv[1:] if a in ASSETS] or list(ASSETS)
	for name in names:
		k = toy.new_kit(bevel=0.02, segments=2)
		ASSETS[name](k, np.random.default_rng(200 + list(ASSETS).index(name)))
		toy.export(k, name, "street")
