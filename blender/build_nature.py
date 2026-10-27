"""Trees, shrubs and flower beds for assets/nature/. Origin at the base, centred.

Run: <blender-venv>/bin/python blender/build_nature.py [name ...]
"""
import sys

import numpy as np

import toy  # first: it loads bpy, which makes mathutils importable


def tree_round(k, rng):
	"""A round-crowned shade tree, 5.5 m."""
	tips = toy.trunk(k, 0, 0, 0, 2.6, 0.16, 0.1, rng, limbs=5, limb_len=1.0)
	lobes = [(t.x, t.y, t.z + 0.4) for t in tips] + [(0, 0, 4.3)]
	for c in lobes:
		r = rng.uniform(0.9, 1.15)
		toy.cluster(k, c, (r, r, r * 0.85), 0.26, rng, flatten_bottom=False, max_tris=1800)


def tree_conifer(k, rng):
	"""A conifer in stacked rounded tiers, 6 m."""
	k.cylinder("bark", 0, 0, 0, 1.4, 0.14, r_top=0.1, segments=10)
	tiers = [(1.3, 1.6), (2.4, 1.3), (3.4, 1.0), (4.3, 0.72), (5.1, 0.45)]
	for z, r in tiers:
		toy.cluster(k, (0, 0, z), (r, r, 0.55), 0.2, rng, palette=("leaf_dark", "leaf_dark", "leaf_mid"),
			max_tris=2000)
	toy.cluster(k, (0, 0, 5.65), (0.22, 0.22, 0.3), 0.12, rng, palette=("leaf_dark", "leaf_mid", "leaf_mid"),
		max_tris=300)


def tree_blossom(k, rng):
	"""A small blossom tree, 4.5 m, pink with a little green showing."""
	tips = toy.trunk(k, 0, 0, 0, 2.0, 0.13, 0.08, rng, limbs=4, limb_len=0.85)
	lobes = [(t.x, t.y, t.z + 0.35) for t in tips] + [(0, 0, 3.6)]
	for c in lobes:
		r = rng.uniform(0.75, 0.95)
		toy.cluster(k, c, (r, r, r * 0.85), 0.22, rng, palette=("blossom_dark", "blossom", "blossom_light"),
			flatten_bottom=False, max_tris=1800)


def bush_round(k, rng):
	"""A round flowering bush, 1 m across."""
	tops = toy.cluster(k, (0, 0, 0.42), (0.5, 0.5, 0.45), 0.13, rng, max_tris=2000)
	toy.flowers(k, toy.pick(tops, 18, rng), 0.065, rng)


def topiary_cone(k, rng):
	"""A clipped cone, 1.6 m tall, like the reference's corner topiaries."""
	for z, r in ((0.35, 0.42), (0.75, 0.34), (1.1, 0.25), (1.4, 0.15)):
		toy.cluster(k, (0, 0, z), (r, r, 0.28), 0.1, rng, palette=("leaf_dark", "leaf_mid", "leaf_light"),
			max_tris=600)
	k.cylinder("wood", 0, 0, 0, 0.12, 0.3, r_top=0.3, segments=16)


def flower_bed(k, rng):
	"""A 2 × 0.8 m bed: timber edging, low foliage mounds, dense flowers in two colours."""
	k.ring("wood", -1.0, 1.0, -0.4, 0.4, 0.0, 0.18, 0.08)
	k.box("soil", -0.92, 0.92, -0.32, 0.32, 0.0, 0.14, bevel=0)
	for x in np.linspace(-0.68, 0.68, 4):
		tops = toy.cluster(k, (x + rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), 0.2),
			(0.3, 0.26, 0.2), 0.09, rng, max_tris=450)
		colour = "flower_white" if x < 0 else "flower_pink"
		toy.flowers(k, toy.pick(tops, 16, rng), 0.06, rng, colour=colour)


def hedge(k, rng):
	"""A 2 m clipped hedge section, 0.9 m tall, made to butt against the next one."""
	for x in (-0.5, 0.5):
		toy.cluster(k, (x, 0, 0.45), (0.55, 0.32, 0.45), 0.12, rng, palette=("leaf_dark", "leaf_mid", "leaf_mid"),
			max_tris=1200)


def window_box_plants(k, rng):
	"""Trailing plants for a 1 m window box: low mounds spilling over the front, white flowers."""
	for x in (-0.33, 0.0, 0.33):
		tops = toy.cluster(k, (x, -0.02, 0.0), (0.2, 0.14, 0.14), 0.07, rng, max_tris=260)
		toy.flowers(k, toy.pick(tops, 6, rng), 0.05, rng)


ASSETS = {
	"tree_round": (tree_round, 0.05),
	"tree_conifer": (tree_conifer, 0.05),
	"tree_blossom": (tree_blossom, 0.05),
	"bush_round": (bush_round, 0.02),
	"topiary_cone": (topiary_cone, 0.02),
	"flower_bed": (flower_bed, 0.02),
	"hedge": (hedge, 0.02),
	"window_box_plants": (window_box_plants, 0.02),
}


if __name__ == "__main__":
	names = [a for a in sys.argv[1:] if a in ASSETS] or list(ASSETS)
	for i, name in enumerate(names):
		fn, bevel = ASSETS[name]
		k = toy.new_kit(bevel=bevel, segments=2)
		fn(k, np.random.default_rng(100 + list(ASSETS).index(name)))
		toy.export(k, name, "nature", organic=True)
