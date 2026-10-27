"""The modular kit: materials from docs/style.md and the parts buildings are assembled from.

Everything is built into one bmesh in metres, Blender axes: X right, -Y is the front (it becomes +Z in Godot), Z up.
Parts take coordinates in the current frame, set with `with kit.frame(...)`, so a window can be placed on any wall.
"""
import math
import os
from contextlib import contextmanager

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise

import textures

BEVEL = 0.02  # every exposed edge, docs/style.md

# name: (albedo hex, roughness, texture function or None, texture tile in metres, extra)
MATERIALS = {
	"brick": ("#9a5f4a", 0.85, textures.brick, 1.8, {}),
	"stone": ("#9a958c", 0.8, textures.stone, 1.0, {}),
	"paving": ("#c8ab92", 0.85, textures.paving, 2.0, {}),
	"roof_flat": ("#7d7570", 0.95, textures.roof_membrane, 2.0, {}),
	"awning_charcoal": ("#efe2cc", 0.9, lambda: textures.stripes("#4a4642"), 0.6, {}),
	"wood": ("#6e4b32", 0.7, textures.wood, 1.0, {}),
	"frame_dark": ("#2f3a33", 0.5, None, 1.0, {}),
	"metal": ("#34383a", 0.45, None, 1.0, {"metallic": 0.6}),
	"metal_light": ("#a7a49c", 0.5, None, 1.0, {"metallic": 0.4}),
	"glass_dark": ("#2b2f33", 0.05, None, 1.0, {}),
	"glass_clear": ("#2b2f33", 0.05, None, 1.0, {"alpha": 0.25}),
	"glass_lit": ("#ffb35c", 0.1, None, 1.0, {"emit": 1.2}),
	"canvas": ("#ecdcc4", 0.9, None, 1.0, {}),
	"cream": ("#efe2cc", 0.6, None, 1.0, {}),
	"plaster_warm": ("#e8d3b5", 0.9, None, 1.0, {}),
	"soil": ("#4a3a2c", 1.0, None, 1.0, {}),
	"foliage_dark": ("#4f6a32", 0.85, None, 1.0, {"two_sided": True}),
	"foliage": ("#6f8a3e", 0.75, None, 1.0, {"two_sided": True}),
	"foliage_light": ("#8aa04c", 0.7, None, 1.0, {"two_sided": True}),
	"bark": ("#5a4636", 0.9, None, 1.0, {}),
	"flower_pink": ("#e3a6b8", 0.7, None, 1.0, {"two_sided": True}),
	"flower_red": ("#b8463a", 0.7, None, 1.0, {"two_sided": True}),
	"flower_yellow": ("#c9a24a", 0.7, None, 1.0, {"two_sided": True}),
	"flower_white": ("#efe6d6", 0.7, None, 1.0, {"two_sided": True}),
	"flower_violet": ("#9c7fb0", 0.7, None, 1.0, {"two_sided": True}),
	"lamp_glow": ("#ffcf8a", 0.4, None, 1.0, {"emit": 4.0}),
	"brass": ("#b08d57", 0.35, None, 1.0, {"metallic": 0.9}),
}


def srgb_to_linear(c):
	return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


class Kit:
	def __init__(self, cache_dir, materials=None, bevel=BEVEL, bevel_segments=2):
		self.cache = cache_dir
		self.table = materials or MATERIALS
		self.bevel = bevel
		self.bevel_segments = bevel_segments
		os.makedirs(cache_dir, exist_ok=True)
		self.bm = bmesh.new()
		self.materials = []
		self.index = {}
		self.tile = []
		self.cutters = []  # (mesh, material name), consumed by shell()
		self.xf = Matrix.Identity(4)

	# --- Frames -------------------------------------------------------------

	@contextmanager
	def frame(self, x=0.0, y=0.0, z=0.0, rot_deg=0.0):
		"""Nested local frame: translate, then rotate about Z."""
		old = self.xf
		self.xf = old @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")
		try:
			yield
		finally:
			self.xf = old

	# --- Materials ----------------------------------------------------------

	def mat(self, name):
		if name in self.index:
			return self.index[name]
		hexcol, rough, tex, tile, extra = self.table[name]
		m = bpy.data.materials.new(name)
		m.use_nodes = True
		nodes = m.node_tree.nodes
		links = m.node_tree.links
		bsdf = nodes.get("Principled BSDF")
		col = srgb_to_linear(textures.hex_rgb(hexcol))
		bsdf.inputs["Base Color"].default_value = (*col, 1.0)
		bsdf.inputs["Roughness"].default_value = rough
		bsdf.inputs["Metallic"].default_value = extra.get("metallic", 0.0)
		if "alpha" in extra:
			bsdf.inputs["Alpha"].default_value = extra["alpha"]
			m.surface_render_method = "BLENDED"
		m.use_backface_culling = not extra.get("two_sided", False)
		if "emit" in extra:
			bsdf.inputs["Emission Color"].default_value = (*col, 1.0)
			bsdf.inputs["Emission Strength"].default_value = extra["emit"]
		if extra.get("vertex_colour"):
			vc = nodes.new("ShaderNodeVertexColor")
			vc.layer_name = "Col"
			links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
		if tex is not None:
			albedo, normal = tex()
			img = self._image(name, albedo, False)
			node = nodes.new("ShaderNodeTexImage")
			node.image = img
			links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
			if normal is not None:
				nimg = self._image(name + "_normal", normal, True)
				nnode = nodes.new("ShaderNodeTexImage")
				nnode.image = nimg
				nmap = nodes.new("ShaderNodeNormalMap")
				links.new(nnode.outputs["Color"], nmap.inputs["Color"])
				links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
		self.index[name] = len(self.materials)
		self.materials.append(m)
		self.tile.append(tile)
		return self.index[name]

	def _image(self, name, arr, non_color):
		h, w, _ = arr.shape
		img = bpy.data.images.new(name, w, h, alpha=False)
		if non_color:
			img.colorspace_settings.name = "Non-Color"
		rgba = np.ones((h, w, 4), dtype=np.float32)
		rgba[..., :3] = arr[::-1]  # Blender's first row is the bottom
		img.pixels.foreach_set(rgba.ravel())
		img.filepath_raw = os.path.join(self.cache, name + ".png")
		img.file_format = "PNG"
		img.save()
		return img

	# --- Primitives ---------------------------------------------------------

	def _merge(self, bm, mat_name, smooth=False):
		"""Adds bm to the kit in the current frame. mat_name None keeps the faces' own material indices."""
		idx = None if mat_name is None else self.mat(mat_name)
		bmesh.ops.transform(bm, matrix=self.xf, verts=bm.verts)
		for f in bm.faces:
			if idx is not None:
				f.material_index = idx
			f.smooth = smooth
		me = bpy.data.meshes.new("tmp")
		bm.to_mesh(me)
		bm.free()
		self.bm.from_mesh(me)
		bpy.data.meshes.remove(me)

	@staticmethod
	def _box_bm(x0, x1, y0, y1, z0, z1, bevel, segments=2):
		bm = bmesh.new()
		bmesh.ops.create_cube(bm, size=1.0)
		sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
		bmesh.ops.transform(bm, matrix=Matrix.Diagonal((sx, sy, sz, 1.0)), verts=bm.verts)
		bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts)
		if bevel > 0 and min(sx, sy, sz) > bevel * 2.5:
			bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=segments, profile=0.5, affect="EDGES")
		return bm

	def box(self, mat, x0, x1, y0, y1, z0, z1, bevel=None):
		"""A box; bevel defaults to the kit's bevel and shrinks to fit thin parts."""
		if bevel is None:
			bevel = min(self.bevel, min(x1 - x0, y1 - y0, z1 - z0) * 0.3)
		self._merge(self._box_bm(x0, x1, y0, y1, z0, z1, bevel, self.bevel_segments), mat)

	def ring(self, mat, x0, x1, y0, y1, z0, z1, width):
		"""Four boxes framing a rectangle, for cornices, copings and bands."""
		self.box(mat, x0, x1, y0, y0 + width, z0, z1)
		self.box(mat, x0, x1, y1 - width, y1, z0, z1)
		self.box(mat, x0, x0 + width, y0 + width, y1 - width, z0, z1)
		self.box(mat, x1 - width, x1, y0 + width, y1 - width, z0, z1)

	def cylinder(self, mat, x, y, z0, z1, r, r_top=None, segments=16):
		bm = bmesh.new()
		bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=r,
			radius2=r if r_top is None else r_top, depth=z1 - z0,
			matrix=Matrix.Translation((x, y, (z0 + z1) / 2)))
		self._merge(bm, mat, smooth=True)

	def rod(self, mat, p0, p1, r, segments=8):
		"""A thin cylinder between two points."""
		p0, p1 = Vector(p0), Vector(p1)
		d = p1 - p0
		bm = bmesh.new()
		rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
		bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=r, radius2=r,
			depth=d.length, matrix=Matrix.Translation((p0 + p1) / 2) @ rot)
		self._merge(bm, mat, smooth=True)

	def sphere(self, mat, x, y, z, r, scale=(1.0, 1.0, 1.0), subdiv=2):
		bm = bmesh.new()
		bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r,
			matrix=Matrix.Translation((x, y, z)) @ Matrix.Diagonal((*scale, 1.0)))
		self._merge(bm, mat, smooth=True)

	def prism(self, mat, profile_yz, x0, x1):
		"""A polygon in the YZ plane, extruded from x0 to x1."""
		bm = bmesh.new()
		a = [bm.verts.new((x0, y, z)) for y, z in profile_yz]
		b = [bm.verts.new((x1, y, z)) for y, z in profile_yz]
		bm.faces.new(a[::-1])
		bm.faces.new(b)
		n = len(profile_yz)
		for i in range(n):
			j = (i + 1) % n
			bm.faces.new((a[i], a[j], b[j], b[i]))
		bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
		self._merge(bm, mat)

	def text(self, mat, body, size, depth, x, y, z):
		"""Letters standing in the XZ plane, facing -Y, centred on x, baseline at z."""
		curve = bpy.data.curves.new("text", "FONT")
		curve.body = body
		curve.size = size
		curve.extrude = depth / 2
		curve.align_x = "CENTER"
		obj = bpy.data.objects.new("text", curve)
		bpy.context.scene.collection.objects.link(obj)
		me = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
		bpy.data.objects.remove(obj)
		bm = bmesh.new()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
		bmesh.ops.transform(bm, matrix=Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(90), 4, "X"),
			verts=bm.verts)
		self._merge(bm, mat)

	# --- Walls with openings ------------------------------------------------

	def cut(self, mat, x0, x1, y0, y1, z0, z1):
		"""Registers a hole for the next shell(); the hole's faces take mat."""
		bm = self._box_bm(x0, x1, y0, y1, z0, z1, 0)
		bmesh.ops.transform(bm, matrix=self.xf, verts=bm.verts)
		me = bpy.data.meshes.new("cutter")
		bm.to_mesh(me)
		bm.free()
		self.cutters.append((me, mat))

	def shell(self, mat, x0, x1, y0, y1, z0, z1):
		"""A solid block with every registered cut taken out, bevelled after cutting."""
		block = bpy.data.objects.new("shell", bpy.data.meshes.new("shell"))
		bm = self._box_bm(x0, x1, y0, y1, z0, z1, 0)
		bmesh.ops.transform(bm, matrix=self.xf, verts=bm.verts)
		bm.to_mesh(block.data)
		bm.free()
		block.data.materials.append(self.materials[self.mat(mat)])
		coll = bpy.data.collections.new("cutters")
		bpy.context.scene.collection.objects.link(block)
		for me, cmat in self.cutters:
			me.materials.append(self.materials[self.mat(cmat)])
			o = bpy.data.objects.new("cutter", me)
			coll.objects.link(o)
		boolean = block.modifiers.new("cut", "BOOLEAN")
		boolean.operation = "DIFFERENCE"
		boolean.operand_type = "COLLECTION"
		boolean.collection = coll
		boolean.solver = "EXACT"
		boolean.material_mode = "TRANSFER"
		bevel = block.modifiers.new("bevel", "BEVEL")
		bevel.width = self.bevel
		bevel.segments = self.bevel_segments
		bevel.limit_method = "ANGLE"
		me = bpy.data.meshes.new_from_object(block.evaluated_get(bpy.context.evaluated_depsgraph_get()))
		for p in me.polygons:
			p.material_index = self.index[me.materials[p.material_index].name]
		self.bm.from_mesh(me)
		bpy.data.meshes.remove(me)
		for o in list(coll.objects):
			bpy.data.objects.remove(o)
		bpy.data.collections.remove(coll)
		bpy.data.objects.remove(block)
		self.cutters = []

	def window(self, cx, sill, w, h, glass="glass_dark", recess=0.12, cut_depth=None, bars=True):
		"""A recessed window in the current wall frame: the wall face is y=0, outside is -Y.
		Frame, glazing bars, stone sill and lintel. cut_depth lets the hole reach a room behind the wall."""
		x0, x1 = cx - w / 2, cx + w / 2
		self.cut("brick", x0, x1, -0.05, cut_depth or recess, sill, sill + h)
		self.box(glass, x0, x1, recess - 0.02, recess, sill, sill + h, bevel=0)
		f, d0, d1 = 0.06, recess - 0.08, recess - 0.02
		self.box("frame_dark", x0, x1, d0, d1, sill, sill + f)
		self.box("frame_dark", x0, x1, d0, d1, sill + h - f, sill + h)
		self.box("frame_dark", x0, x0 + f, d0, d1, sill, sill + h)
		self.box("frame_dark", x1 - f, x1, d0, d1, sill, sill + h)
		if bars:
			self.box("frame_dark", cx - 0.015, cx + 0.015, d0 + 0.01, d1, sill, sill + h, bevel=0)
			bar_z = sill + h * 0.62
			self.box("frame_dark", x0, x1, d0 + 0.01, d1, bar_z - 0.015, bar_z + 0.015, bevel=0)
		self.box("stone", x0 - 0.08, x1 + 0.08, -0.06, d0, sill - 0.05, sill)
		self.box("stone", x0 - 0.1, x1 + 0.1, -0.04, 0.0, sill + h, sill + h + 0.2)

	def window_box(self, cx, sill, w, rng):
		"""A flower box hung under a sill, in the current wall frame."""
		self.box("wood", cx - w / 2, cx + w / 2, -0.28, -0.08, sill - 0.25, sill - 0.07)
		self.box("soil", cx - w / 2 + 0.03, cx + w / 2 - 0.03, -0.25, -0.11, sill - 0.09, sill - 0.06, bevel=0)
		self.shrubs(cx - w / 2 + 0.1, cx + w / 2 - 0.1, -0.24, -0.12, sill - 0.1, 0.12, rng, count=4, sag=0.12)

	# --- Planting and furniture ---------------------------------------------

	def bush(self, mat, x, y, z, r, rng, squash=0.85):
		"""A lumpy, noise-displaced mound of foliage; returns points on its upper surface for flowers."""
		bm = bmesh.new()
		bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r)
		seed = Vector(rng.uniform(-100, 100, 3))
		for v in bm.verts:
			n = v.co.normalized()
			lump = noise.noise(n * 2.2 + seed) * 0.22 + noise.noise(n * 6.0 + seed) * 0.08
			v.co = n * r * (1 + lump)
			v.co.z *= squash
		bmesh.ops.translate(bm, vec=(x, y, z + r * squash * 0.6), verts=bm.verts)
		tops = [v.co.copy() for v in bm.verts if v.normal.z > 0.35]
		self._merge(bm, mat, smooth=True)
		return tops

	FLOWERS = ["flower_pink", "flower_red", "flower_yellow", "flower_white", "flower_violet"]

	def _leaves(self, points, normals, size, rng, mats=("foliage_dark", "foliage", "foliage_light"),
			weights=(0.25, 0.45, 0.3)):
		"""Single leaves: a folded diamond each, built in one bmesh per material so thousands stay cheap."""
		buckets = {m: bmesh.new() for m in mats}
		pick = rng.choice(len(mats), size=len(points), p=weights)
		for p, n, k in zip(points, normals, pick):
			bm = buckets[mats[k]]
			length = size * rng.uniform(0.75, 1.25)
			z = Vector(n).normalized()
			t = z.orthogonal().normalized()
			t.rotate(Matrix.Rotation(rng.uniform(0, math.tau), 3, z))
			b = z.cross(t)
			p = Vector(p)
			fold = z * length * 0.08
			base = bm.verts.new(p - t * length * 0.5)
			tip = bm.verts.new(p + t * length * 0.5 - z * length * 0.1)
			left = bm.verts.new(p - b * length * 0.28 + fold)
			right = bm.verts.new(p + b * length * 0.28 + fold)
			bm.faces.new((base, right, tip))
			bm.faces.new((base, tip, left))
		for m, bm in buckets.items():
			self._merge(bm, m, smooth=False)

	def _flowers(self, points, size, colour):
		"""Five-petal star flowers, facing mostly up."""
		bm = bmesh.new()
		for p in points:
			p = Vector(p)
			ring = []
			for i in range(10):
				a = i * math.tau / 10
				rad = size if i % 2 == 0 else size * 0.45
				ring.append(bm.verts.new(p + Vector((math.cos(a) * rad, math.sin(a) * rad, (i % 2) * size * 0.15))))
			bm.faces.new(ring)
		self._merge(bm, colour)

	def foliage(self, x, y, z, r, rng, leaf=0.075, squash=0.85, flower=None, flower_count=0, sag=0.0):
		"""A mound of leaves: a dark core so no gaps show, and a shell of single leaves over it.
		sag lets the lower leaves spill outward and down, for plants hanging over a planter's edge."""
		self.bush("foliage_dark", x, y, z, r * 0.75, rng, squash)
		centre = Vector((x, y, z + r * squash * 0.6))
		area = 4 * math.pi * r * r * 0.8
		n = int(area / (0.5 * leaf * leaf) * 1.4)
		pts, nrm, tops = [], [], []
		for _ in range(n):
			d = Vector(rng.normal(size=3)).normalized()
			if d.z < -0.35:
				d.z = -d.z * 0.3
			lump = 1 + noise.noise(d * 2.2) * 0.2
			p = centre + Vector((d.x, d.y, d.z * squash)) * r * lump * rng.uniform(0.9, 1.08)
			if sag and d.z < 0.1:
				p += Vector((d.x, d.y, -1.2)) * sag * rng.uniform(0.3, 1.0)
			pts.append(p)
			nrm.append(d + Vector(rng.normal(size=3)) * 0.5 + Vector((0, 0, 0.3)))
			if d.z > 0.3:
				tops.append(p + d * leaf * 0.3)
		self._leaves(pts, nrm, leaf, rng)
		if flower and tops:
			idx = rng.choice(len(tops), size=min(len(tops), flower_count), replace=False)
			self._flowers([tops[i] for i in idx], leaf * 0.35, flower)

	def shrubs(self, x0, x1, y0, y1, z, size, rng, count=4, flowers=True, sag=0.0):
		"""A planted row of foliage mounds, one flower colour per row."""
		colour = rng.choice(self.FLOWERS) if flowers else None
		for _ in range(count):
			x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
			r = size * rng.uniform(0.8, 1.2)
			self.foliage(x, y, z, r, rng, leaf=min(0.08, max(0.045, r * 0.3)), flower=colour,
				flower_count=int(r * 60), sag=sag)

	def tree(self, x, y, z, height, rng, crown=1.6):
		"""A small deciduous tree: tapered trunk, a few limbs, and a crown of leaf mounds at their ends."""
		top = z + height * 0.55
		self.cylinder("bark", x, y, z, top, 0.09, r_top=0.055, segments=10)
		ends = []
		for i in range(5):
			a = i * math.tau / 5 + rng.uniform(-0.3, 0.3)
			reach = crown * rng.uniform(0.35, 0.6)
			end = Vector((x + math.cos(a) * reach, y + math.sin(a) * reach, z + height * rng.uniform(0.68, 0.82)))
			self.rod("bark", (x, y, top - 0.3), end, 0.035, segments=6)
			ends.append(end)
		ends.append(Vector((x, y, z + height * 0.82)))
		for e in ends:
			self.foliage(e.x, e.y, e.z - crown * 0.25, crown * rng.uniform(0.38, 0.5), rng, leaf=0.11, squash=0.8)

	def planter(self, x, y, w, d, h, rng):
		self.box("wood", x - w / 2, x + w / 2, y - d / 2, y + d / 2, 0.02, h)
		self.box("soil", x - w / 2 + 0.04, x + w / 2 - 0.04, y - d / 2 + 0.04, y + d / 2 - 0.04, h - 0.04, h - 0.02,
			bevel=0)
		self.shrubs(x - w / 2 + 0.12, x + w / 2 - 0.12, y - d / 2 + 0.1, y + d / 2 - 0.1, h - 0.06, 0.2, rng,
			count=max(3, int(w * 3)), sag=0.12)

	def chair(self, x, y, facing_deg):
		"""Bistro chair; its sitter faces facing_deg (0 = -Y)."""
		with self.frame(x, y, 0.0, facing_deg):
			for lx in (-0.18, 0.18):
				for ly in (-0.18, 0.18):
					self.cylinder("metal", lx, ly, 0.02, 0.45, 0.014, segments=8)
			self.box("wood", -0.21, 0.21, -0.21, 0.21, 0.45, 0.48, bevel=0.01)
			for lx in (-0.18, 0.18):
				self.cylinder("metal", lx, 0.19, 0.48, 0.86, 0.014, segments=8)
			self.box("wood", -0.21, 0.21, 0.17, 0.21, 0.66, 0.84, bevel=0.01)

	def table(self, x, y):
		self.cylinder("metal", x, y, 0.02, 0.05, 0.22, segments=16)
		self.cylinder("metal", x, y, 0.05, 0.72, 0.03, segments=8)
		self.cylinder("wood", x, y, 0.72, 0.75, 0.35, segments=24)

	def umbrella(self, x, y):
		self.cylinder("metal", x, y, 0.75, 2.6, 0.022, segments=8)
		self.cylinder("canvas", x, y, 2.2, 2.55, 1.2, r_top=0.02, segments=8)
		self.sphere("metal", x, y, 2.62, 0.04, subdiv=1)

	def lantern(self, x, y, z):
		"""A wall lantern centred at (x, y, z), hanging off a wall behind it at +Y."""
		self.box("metal", x - 0.02, x + 0.02, y, y + 0.12, z + 0.1, z + 0.14, bevel=0)
		self.box("metal", x - 0.09, x + 0.09, y - 0.09, y + 0.09, z - 0.16, z - 0.13, bevel=0)
		self.box("lamp_glow", x - 0.07, x + 0.07, y - 0.07, y + 0.07, z - 0.13, z + 0.08, bevel=0)
		self.cylinder("metal", x, y, z + 0.08, z + 0.14, 0.1, r_top=0.02, segments=4)

	# --- Output -------------------------------------------------------------

	def build_object(self, name, weighted_normals=True):
		"""Turns the accumulated bmesh into one object with world-scale UVs per material.
		weighted_normals suits hard surfaces; leave it off for organic shapes, which it flattens into facets."""
		me = bpy.data.meshes.new(name)
		bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=0.0001)
		self.bm.to_mesh(me)
		self.bm.free()
		for m in self.materials:
			me.materials.append(m)
		me.shade_smooth()
		me.set_sharp_from_angle(angle=math.radians(50))
		self._project_uvs(me)
		obj = bpy.data.objects.new(name, me)
		bpy.context.scene.collection.objects.link(obj)
		if not weighted_normals:
			return obj
		# Weighted normals keep big faces flat and let only the bevels curve; without them a bevelled box shades
		# like a pillow.
		wn = obj.modifiers.new("normals", "WEIGHTED_NORMAL")
		wn.mode = "FACE_AREA"
		wn.keep_sharp = True
		wn.weight = 100
		baked = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
		obj.modifiers.clear()
		obj.data = baked
		bpy.data.meshes.remove(me)
		baked.name = name
		return obj

	def _project_uvs(self, me):
		"""Box projection in metres, divided by each material's texture tile, so texel density is uniform."""
		while me.uv_layers:  # parts like text bring their own; only the projected layer may export
			me.uv_layers.remove(me.uv_layers[0])
		uv = me.uv_layers.new(name="UVMap")
		co = np.empty(len(me.vertices) * 3)
		me.vertices.foreach_get("co", co)
		co = co.reshape(-1, 3)
		for p in me.polygons:
			n = p.normal
			ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
			t = self.tile[p.material_index]
			for li in p.loop_indices:
				v = co[me.loops[li].vertex_index]
				if az >= ax and az >= ay:
					u, w = v[0], v[1]
				elif ax >= ay:
					u, w = v[1], v[2]
				else:
					u, w = v[0], v[2]
				uv.data[li].uv = (u / t, w / t)
