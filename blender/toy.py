"""Shared pieces for the stylised assets (docs/style.md): the material table, blob-cluster plants, and export.

Every asset script builds into a fresh Blender scene with a Kit, then calls export(), which writes
assets/<folder>/<name>.glb and the editable source blender/src/<name>.blend.
"""
import math
import os
import sys

import bpy  # noqa: I001  (first: loading bpy makes bmesh and mathutils importable)
import bmesh
import numpy as np
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Kit  # noqa: E402

ROOT = os.path.dirname(HERE)

# name: (albedo hex, roughness, texture, tile, extra), the same shape as kit.MATERIALS
MATERIALS = {
	"stucco": ("#ece3d3", 0.9, None, 1.0, {}),
	"trim_sand": ("#d9c4a3", 0.8, None, 1.0, {}),
	"trim_tan": ("#c4955f", 0.7, None, 1.0, {}),
	"frame": ("#3b3f45", 0.5, None, 1.0, {}),
	"door_sage": ("#6f8f4a", 0.5, None, 1.0, {}),
	"roof_slate": ("#646b78", 0.8, None, 1.0, {}),
	"roof_flat": ("#d6d1c7", 0.9, None, 1.0, {}),
	"interior_glow": ("#ffc27a", 0.9, None, 1.0, {"emit": 0.9}),
	"interior_wood": ("#c98f55", 0.7, None, 1.0, {"emit": 0.25}),
	"glass": ("#6f8796", 0.05, None, 1.0, {"alpha": 0.3}),
	"pavers": ("#d9d3c8", 0.85, None, 1.0, {}),
	"joints": ("#b8b0a3", 0.9, None, 1.0, {}),
	"asphalt": ("#5b5d60", 0.9, None, 1.0, {}),
	"lane_paint": ("#efe3bd", 0.8, None, 1.0, {}),
	"curb": ("#cfc8bc", 0.85, None, 1.0, {}),
	"lawn": ("#6e9a45", 0.95, None, 1.0, {}),
	"soil": ("#6b4e36", 1.0, None, 1.0, {}),
	"foliage": ("#ffffff", 0.8, None, 1.0, {"vertex_colour": True}),
	"leaf_dark": ("#3f7a2c", 0.8, None, 1.0, {}),
	"leaf_mid": ("#5e9b3a", 0.8, None, 1.0, {}),
	"leaf_light": ("#86bf4f", 0.8, None, 1.0, {}),
	"blossom_dark": ("#c88aa0", 0.75, None, 1.0, {}),
	"blossom": ("#e7a3b6", 0.75, None, 1.0, {}),
	"blossom_light": ("#f3c6d2", 0.75, None, 1.0, {}),
	"flower_white": ("#f6f1e6", 0.7, None, 1.0, {"two_sided": True}),
	"flower_pink": ("#e7a3b6", 0.7, None, 1.0, {"two_sided": True}),
	"flower_lavender": ("#a58ccf", 0.7, None, 1.0, {"two_sided": True}),
	"flower_centre": ("#e9c24a", 0.7, None, 1.0, {"two_sided": True}),
	"bark": ("#7a5a40", 0.9, None, 1.0, {}),
	"wood": ("#b07a4a", 0.75, None, 1.0, {}),
	"metal": ("#a9adb0", 0.45, None, 1.0, {"metallic": 0.5}),
	"brass": ("#c9a45c", 0.35, None, 1.0, {"metallic": 0.9}),
	"lamp_glow": ("#ffd9a0", 0.4, None, 1.0, {"emit": 3.0}),
}


def new_kit(bevel=0.05, segments=3):
	bpy.ops.wm.read_factory_settings(use_empty=True)
	return Kit(os.path.join(HERE, ".cache"), materials=MATERIALS, bevel=bevel, bevel_segments=segments)


def export(kit, name, folder, organic=False):
	"""Builds the kit's mesh as one object and writes the GLB and the .blend source."""
	obj = kit.build_object(name, weighted_normals=not organic)
	if FOLIAGE:
		joined = bmesh.new()
		joined.verts.layers.float_color.new("Col")
		for part in FOLIAGE:
			me = bpy.data.meshes.new("part")
			part.to_mesh(me)
			part.free()
			joined.from_mesh(me)
			bpy.data.meshes.remove(me)
		FOLIAGE.clear()
		me = bpy.data.meshes.new(name + "_foliage")
		joined.to_mesh(me)
		joined.free()
		me.materials.append(kit.materials[kit.mat("foliage")])
		me.color_attributes.active_color = me.color_attributes["Col"]
		fol = bpy.data.objects.new(name + "_foliage", me)
		bpy.context.scene.collection.objects.link(fol)
	glb = os.path.join(ROOT, "assets", folder, name + ".glb")
	os.makedirs(os.path.dirname(glb), exist_ok=True)
	# No lights: they arrive in Godot at uncontrolled strength. Lot scenes add their own.
	bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
	bpy.context.preferences.filepaths.save_version = 0  # no .blend1 backups
	src = os.path.join(HERE, "src", name + ".blend")
	os.makedirs(os.path.dirname(src), exist_ok=True)
	bpy.ops.wm.save_as_mainfile(filepath=src, compress=True)
	tris = sum(len(p.vertices) - 2 for o in bpy.context.scene.objects if o.type == "MESH" for p in o.data.polygons)
	print(f"{name}: {tris} triangles -> {os.path.relpath(glb, ROOT)}")
	return tris


# --- Plants: clusters of rounded leaf blobs -----------------------------------------------------------------------

def fuse(kit, spheres, voxel, max_tris):
	"""Fuses spheres [(centre, radii, material)] into one smooth, lumpy surface: voxel remesh, then decimate to
	max_tris. Each face takes the material of the sphere nearest it, so lumps keep their own shade."""
	bm = bmesh.new()
	for c, radii, _ in spheres:
		part = bmesh.new()
		bmesh.ops.create_icosphere(part, subdivisions=2, radius=1.0)
		bmesh.ops.transform(part, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*radii, 1.0)), verts=part.verts)
		me = bpy.data.meshes.new("part")
		part.to_mesh(me)
		part.free()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
	me = bpy.data.meshes.new("cluster")
	bm.to_mesh(me)
	bm.free()
	obj = bpy.data.objects.new("cluster", me)
	bpy.context.scene.collection.objects.link(obj)
	# Pick the voxel from the budget so triangles come out even (about 2 per voxel face), but never so coarse that
	# the lumps melt away. Then smooth out the voxel steps.
	area = sum(4 * math.pi * (max(r) ** 2) for _, r, _ in spheres) * 0.45
	voxel = max(voxel, math.sqrt(2 * area / max_tris))
	remesh = obj.modifiers.new("remesh", "REMESH")
	remesh.mode = "VOXEL"
	remesh.voxel_size = voxel
	smooth = obj.modifiers.new("smooth", "SMOOTH")
	smooth.factor = 0.5
	smooth.iterations = 2
	dg = bpy.context.evaluated_depsgraph_get()
	fused = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
	obj.modifiers.clear()
	obj.data = fused
	tris = sum(len(p.vertices) - 2 for p in fused.polygons)
	if tris > max_tris:
		dec = obj.modifiers.new("decimate", "DECIMATE")
		dec.ratio = max_tris / tris
		dg = bpy.context.evaluated_depsgraph_get()
		final = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
	else:
		final = fused.copy()
	bpy.data.objects.remove(obj)
	bpy.data.meshes.remove(me)
	bpy.data.meshes.remove(fused)
	# Vertex colours: each vertex blends the colours of the lumps nearest it, so shades meet softly.
	co = np.empty(len(final.vertices) * 3)
	final.vertices.foreach_get("co", co)
	co = co.reshape(-1, 3)
	centres = np.array([tuple(c) for c, _, _ in spheres])
	sizes = np.array([max(r) for _, r, _ in spheres])
	cols = np.array([colour(m) * rng_tint(i) for i, (_, _, m) in enumerate(spheres)])
	dist = np.linalg.norm(co[:, None, :] - centres[None, :, :], axis=2) - sizes[None, :]
	falloff = max(np.median(sizes[1:]) if len(sizes) > 1 else sizes[0], 0.05) * 0.45
	w = np.exp(-(dist - dist.min(axis=1, keepdims=True)) / falloff)
	vcol = (w @ cols) / w.sum(axis=1, keepdims=True)
	out = bmesh.new()
	layer = out.verts.layers.float_color.new("Col")
	out.from_mesh(final)
	bpy.data.meshes.remove(final)
	out.verts.ensure_lookup_table()
	out.normal_update()
	for v in out.verts:
		c = vcol[v.index]
		# Baked shading: creases between lumps darken, upward faces catch a little sky.
		if v.link_edges:
			mean = sum((e.other_vert(v).co for e in v.link_edges), Vector()) / len(v.link_edges)
			concave = (mean - v.co).dot(v.normal) / max(voxel, 1e-4)
		else:
			concave = 0.0
		light = 1.0 - min(max(concave * 1.6, 0.0), 0.45) + max(v.normal.z, 0.0) * 0.12
		v[layer] = (c[0] * light, c[1] * light, c[2] * light, 1.0)
	for f in out.faces:
		f.smooth = True
	bmesh.ops.transform(out, matrix=kit.xf, verts=out.verts)
	FOLIAGE.append(out)


FOLIAGE = []  # fused foliage in the current asset, joined into one vertex-coloured mesh by export()


def colour(name):
	"""Linear RGB of a material in the table."""
	h = MATERIALS[name][0].lstrip("#")
	c = np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
	return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


_tint = np.random.default_rng(7)


def rng_tint(i):
	"""A small brightness shift per lump, so neighbouring lumps of one shade still read apart."""
	return 1.0 if i == 0 else _tint.uniform(0.9, 1.08)


def cluster(kit, centre, radii, blob_r, rng, count=None, palette=("leaf_dark", "leaf_mid", "leaf_light"),
		squash=1.0, flatten_bottom=True, voxel=None, max_tris=1500):
	"""Rounded leaf lumps packed over the surface of a lumpy ellipsoid, fused into one surface. Darker below and
	inside, lighter on top. Returns outward points on the upper half, for flowers."""
	centre = Vector(centre)
	rx, ry, rz = radii
	area = 4 * math.pi * ((rx * ry) ** 1.6 + (rx * rz) ** 1.6 + (ry * rz) ** 1.6) ** (1 / 1.6) / 3
	if count is None:
		count = max(6, int(area / (math.pi * blob_r * blob_r) * 0.9))
	seed = Vector(rng.uniform(-50, 50, 3))
	core_z = rz * 0.85 * squash
	spheres = [(centre, (rx * 0.85, ry * 0.85, core_z * (0.75 if flatten_bottom else 1.0)), palette[0])]
	tops = []
	golden = math.pi * (3 - math.sqrt(5))
	for i in range(count):
		z = 1 - 2 * (i + 0.5) / count
		rad = math.sqrt(1 - z * z)
		a = golden * i
		d = Vector((math.cos(a) * rad, math.sin(a) * rad, z))
		d += Vector(rng.normal(size=3)) * 0.12
		d.normalize()
		if flatten_bottom and d.z < -0.55:
			continue
		lump = 1 + noise.noise(d * 1.8 + seed) * 0.18
		p = centre + Vector((d.x * rx, d.y * ry, d.z * rz * squash)) * lump
		shade = (d.z + 1) / 2 + rng.normal() * 0.25
		mat = palette[0] if shade < 0.35 else palette[1] if shade < 0.75 else palette[2]
		r = blob_r * rng.uniform(0.8, 1.2)
		spheres.append((p, (r, r, r * rng.uniform(0.8, 0.95)), mat))
		if d.z > 0.15:
			tops.append((p + d * r * 0.85, d))
	fuse(kit, spheres, voxel or blob_r * 0.28, max_tris)
	return tops


def flowers(kit, points, size, rng, colour="flower_white", centre_colour="flower_centre"):
	"""Five-petal discs, each with a centre dot. points are (position, outward direction): flowers face outward,
	leaning up, so they open toward the viewer instead of lying edge-on."""
	petals, centres = bmesh.new(), bmesh.new()
	for p, out in points:
		p = Vector(p)
		face = (Vector(out).normalized() + Vector((0, 0, 0.6))).normalized()
		tilt = Vector((0, 0, 1)).rotation_difference(face).to_matrix().to_4x4() @ Matrix.Rotation(
			rng.uniform(0, math.tau), 4, "Z")
		ring = []
		for i in range(10):
			a = i * math.tau / 10
			rad = size if i % 2 == 0 else size * 0.55
			ring.append(petals.verts.new(p + (tilt @ Vector((math.cos(a) * rad, math.sin(a) * rad, 0.0)))))
		petals.faces.new(ring)
		dot = [centres.verts.new(p + (tilt @ Vector((math.cos(i * math.tau / 6) * size * 0.3,
			math.sin(i * math.tau / 6) * size * 0.3, size * 0.12)))) for i in range(6)]
		centres.faces.new(dot)
	kit._merge(petals, colour)
	if centre_colour:
		kit._merge(centres, centre_colour)
	else:
		centres.free()


def pick(points, n, rng):
	if not points:
		return []
	idx = rng.choice(len(points), size=min(n, len(points)), replace=False)
	return [points[i] for i in idx]


def trunk(kit, x, y, z0, z1, r0, r1, rng, limbs=4, limb_len=0.9):
	"""A tapered trunk and a few upward limbs; returns the limb tips for crown lobes."""
	kit.cylinder("bark", x, y, z0, z1, r0, r_top=r1, segments=10)
	tips = []
	for i in range(limbs):
		a = i * math.tau / limbs + rng.uniform(-0.35, 0.35)
		tip = Vector((x + math.cos(a) * limb_len * rng.uniform(0.6, 1.0),
			y + math.sin(a) * limb_len * rng.uniform(0.6, 1.0), z1 + limb_len * rng.uniform(0.5, 0.9)))
		kit.rod("bark", (x, y, z1 - 0.3), tip, r1 * 0.6, segments=6)
		tips.append(tip)
	return tips
