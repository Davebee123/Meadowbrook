"""Renders an exported asset the way docs/style.md "Checking an asset" asks: four turnarounds, the builder's camera,
and two eye-level views, under the style sheet's golden-hour light.

Run: <blender-venv>/bin/python blender/check.py assets/buildings/cafe.glb <out_dir> [samples]
Renders the GLB itself, so what's checked is what Godot will load.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

GRASS = (0.212, 0.319, 0.085)        # #7f9a52, linear
SUN = (1.0, 0.479, 0.188)            # #ffb878, linear: low golden-hour sun
HORIZON = (0.888, 0.571, 0.337)      # #f2c79b, linear
ZENITH = (0.212, 0.346, 0.552)       # #7fa0c4, linear


TILT_SHIFT_FSTOP = 0.4


def scene(glb, samples):
	bpy.ops.wm.read_factory_settings(use_empty=True)
	bpy.ops.import_scene.gltf(filepath=glb)
	for o in list(bpy.data.objects):
		if o.name.endswith("-colonly"):
			bpy.data.objects.remove(o)
	s = bpy.context.scene
	s.render.engine = "CYCLES"
	s.cycles.device = "CPU"
	s.cycles.samples = samples
	s.cycles.use_denoising = True
	s.view_settings.view_transform = "AgX"
	s.view_settings.look = "AgX - Punchy"

	# Gradient sky: warm at the horizon, blue overhead. It is also the fill light, so shadows go cool.
	world = bpy.data.worlds.new("sky")
	world.use_nodes = True
	nodes, links = world.node_tree.nodes, world.node_tree.links
	coord = nodes.new("ShaderNodeTexCoord")
	split = nodes.new("ShaderNodeSeparateXYZ")
	ramp = nodes.new("ShaderNodeValToRGB")
	ramp.color_ramp.elements[0].position = 0.0
	ramp.color_ramp.elements[0].color = (*HORIZON, 1)
	ramp.color_ramp.elements[1].position = 0.45
	ramp.color_ramp.elements[1].color = (*ZENITH, 1)
	links.new(coord.outputs["Generated"], split.inputs[0])
	links.new(split.outputs["Z"], ramp.inputs["Fac"])
	links.new(ramp.outputs["Color"], nodes["Background"].inputs["Color"])
	nodes["Background"].inputs["Strength"].default_value = 1.1
	s.world = world

	sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
	sun.data.energy = 5.0
	sun.data.color = SUN
	sun.data.angle = math.radians(2)
	# 16° above the horizon, from the front left: long shadows, warm faces.
	sun.rotation_euler = (math.radians(90 - 16), 0, math.radians(-40))
	s.collection.objects.link(sun)

	mat = bpy.data.materials.new("grass")
	mat.use_nodes = True
	mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*GRASS, 1)
	mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
	bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.005))
	bpy.context.object.data.materials.append(mat)
	return s


def camera(s, name, loc, target, ortho_scale=None, fov_v=None, lens=None):
	cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
	s.collection.objects.link(cam)
	cam.location = loc
	cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
	if ortho_scale:
		cam.data.type = "ORTHO"
		cam.data.ortho_scale = ortho_scale
		# Tilt-shift: focus on the target, so what's nearer and farther softens like a model photographed close up.
		cam.data.dof.use_dof = True
		cam.data.dof.focus_distance = (Vector(target) - Vector(loc)).length
		cam.data.dof.aperture_fstop = TILT_SHIFT_FSTOP
	elif fov_v:
		cam.data.sensor_fit = "VERTICAL"
		cam.data.angle = math.radians(fov_v)
	elif lens:
		cam.data.lens = lens
	cam.data.clip_end = 500
	return cam


def render(s, cam, path, w, h):
	s.camera = cam
	s.render.resolution_x, s.render.resolution_y = w, h
	s.render.filepath = path
	bpy.ops.render.render(write_still=True)
	print("rendered", path)


def main():
	glb, out = sys.argv[1], sys.argv[2]
	samples = int(sys.argv[3]) if len(sys.argv) > 3 else 48
	only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
	os.makedirs(out, exist_ok=True)
	s = scene(glb, samples)
	centre = Vector((0, 0, 3.0))
	views = []
	for i, name in enumerate(("front", "right", "back", "left")):
		a = math.radians(-90 + 90 * i)
		d = 30.0
		loc = (d * math.cos(a), d * math.sin(a), 11.0)
		views.append((name, camera(s, name, loc, centre, lens=50), 960, 720))
	# Builder's camera: orthographic, tilted 35.264°, yawed 45°, at the game's default zoom (48 m tall),
	# plus a close crop at the same angle.
	pitch, yaw = math.radians(35.264), math.radians(-45)
	direction = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
	views.append(("builder", camera(s, "builder", tuple(direction * 100), (0, 0, 0), ortho_scale=48 * 16 / 9),
		1600, 900))
	views.append(("builder_close", camera(s, "builder_close", tuple(direction * 100 + Vector((0, 0, 2))),
		(0, 0, 2), ortho_scale=20), 1200, 900))
	# Eye level, 1.6 m, the game's 70° vertical field of view: 3 m from the door, then 1 m.
	views.append(("eye_3m", camera(s, "eye_3m", (0.6, -4.5, 1.6), (0, -1.5, 1.8), fov_v=70), 1280, 720))
	views.append(("eye_1m", camera(s, "eye_1m", (-0.9, -2.6, 1.6), (-2.2, -1.5, 1.5), fov_v=70), 1280, 720))
	for name, cam, w, h in views:
		if only is None or name in only:
			render(s, cam, os.path.join(out, name + ".png"), w, h)


if __name__ == "__main__":
	main()
