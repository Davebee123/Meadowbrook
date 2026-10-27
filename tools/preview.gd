extends SceneTree
## Renders an asset on the preview stage, the way docs/style.md "Checking an asset" asks:
## the builder's camera at gameplay zoom, a close builder view, eye level at 3 m and 1 m,
## and a 10 × 10 block of copies with draw calls and triangles counted.
##
## Run through tools/preview.sh, which imports new files first:
##   tools/preview.sh <out_dir> res://assets/nature/tree_round.glb [res://... ...]
## An asset may carry a focus point for the eye-level views: path@x,y,z (default: the middle of its front).

const STAGE := "res://scenes/preview.tscn"
const PITCH := -35.264  # the game's builder camera (scripts/iso_camera.gd)
const YAW := 45.0
const GAME_ZOOM := 48.0
const SETTLE_FRAMES := 8

var stage: Node3D
var camera: Camera3D
var out_dir: String
var report := PackedStringArray()


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	out_dir = args[0]
	DirAccess.make_dir_recursive_absolute(out_dir)
	stage = (load(STAGE) as PackedScene).instantiate()
	root.add_child(stage)
	camera = stage.get_node("Camera")
	for spec in args.slice(1):
		await _preview(spec)
	var f := FileAccess.open(out_dir.path_join("report.md"), FileAccess.WRITE)
	f.store_string("\n".join(report) + "\n")
	print("\n".join(report))
	quit()


func _preview(spec: String) -> void:
	var parts := spec.split("@")
	var path := parts[0]
	var name := path.get_file().get_basename()
	var asset: Node3D = (load(path) as PackedScene).instantiate()
	stage.add_child(asset)
	var box := _bounds(asset)
	var focus := Vector3(box.get_center().x, minf(1.5, box.size.y * 0.5), box.end.z)
	if parts.size() > 1:
		var p := parts[1].split_floats(",")
		focus = Vector3(p[0], p[1], p[2])
	var figure: Node3D = stage.get_node("Figure")
	figure.position = Vector3(box.end.x + 0.6, 0.875, box.end.z - 0.3)
	figure.visible = true

	_ortho(box.get_center(), GAME_ZOOM)
	await _shot(name + "_builder")
	_ortho(box.get_center(), maxf(box.size.y, maxf(box.size.x, box.size.z)) * 1.25)
	await _shot(name + "_close")
	_eye(focus, 3.0)
	await _shot(name + "_eye3m")
	_eye(focus, 1.0)
	await _shot(name + "_eye1m")

	# Performance: a 10 × 10 block of copies, framed from the builder's angle.
	figure.visible = false
	var spacing := maxf(box.size.x, box.size.z) + 1.0
	var copies: Array[Node3D] = []
	for i in 10:
		for j in 10:
			var c: Node3D = (load(path) as PackedScene).instantiate()
			c.position = Vector3((i - 4.5) * spacing, 0, (j - 4.5) * spacing)
			stage.add_child(c)
			copies.append(c)
	asset.visible = false
	_ortho(Vector3.ZERO, spacing * 10 * 0.75)
	await _shot(name + "_x100")
	var draws := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
	var prims := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
	var objs := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)
	report.append("| %s | %.1f × %.1f × %.1f m | %d | %d | %d |" % [name, box.size.x, box.size.y, box.size.z,
		_triangles(asset), draws, prims])
	print("%s x100: %d objects, %d draw calls, %d primitives" % [name, objs, draws, prims])
	for c in copies:
		c.queue_free()
	asset.queue_free()
	await process_frame


func _ortho(target: Vector3, size: float) -> void:
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = size
	var basis := Basis.from_euler(Vector3(deg_to_rad(PITCH), deg_to_rad(YAW), 0))
	camera.global_transform = Transform3D(basis, target + basis.z * 300.0)


func _eye(focus: Vector3, distance: float) -> void:
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 70.0
	var from := Vector3(focus.x + distance * 0.35, 1.6, focus.z + distance)
	camera.global_transform = Transform3D(Basis(), from).looking_at(focus, Vector3.UP)


func _shot(file: String) -> void:
	for i in SETTLE_FRAMES:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out_dir.path_join(file + ".png"))


func _bounds(node: Node) -> AABB:
	var box := AABB()
	var first := true
	for n in node.find_children("*", "VisualInstance3D", true, false):
		if n is Light3D:
			continue
		var b: AABB = n.global_transform * n.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


func _triangles(node: Node) -> int:
	var total := 0
	for n in node.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = n.mesh
		for s in mesh.get_surface_count():
			var arrays := mesh.surface_get_arrays(s)
			var idx: Variant = arrays[Mesh.ARRAY_INDEX]
			var count: int = (idx as PackedInt32Array).size() if idx != null else (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
			total += count / 3
	return total
