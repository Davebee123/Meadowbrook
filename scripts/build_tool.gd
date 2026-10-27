extends Node3D
## Building from above. The ghost shows where the next piece goes: left click
## places it, drag paints paths, right click removes, R rotates.

const Town := preload("res://scripts/town.gd")

const OK_COLOR := Color(0.55, 0.85, 0.55, 0.45)
const BLOCKED_COLOR := Color(0.9, 0.4, 0.35, 0.45)

var town: Town
var camera: Camera3D
var selected := "house"   # a kind from Town.KINDS, or "path" or "remove"
var rot := 0
var active := true

var _ghost: MeshInstance3D
var _ghost_mat: StandardMaterial3D
var _painting := false
var _erasing := false


func _ready() -> void:
	_ghost_mat = StandardMaterial3D.new()
	_ghost_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_ghost_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_ghost = MeshInstance3D.new()
	_ghost.mesh = BoxMesh.new()
	_ghost.material_override = _ghost_mat
	add_child(_ghost)


func set_tool(t: String) -> void:
	selected = t


func set_active(on: bool) -> void:
	active = on
	_painting = false
	_erasing = false
	_ghost.visible = on


func _process(_delta: float) -> void:
	if not active:
		return
	var cell: Variant = _hover_cell()
	_ghost.visible = cell != null
	if cell == null:
		return
	var size := Vector2i.ONE
	var height := 0.1
	var ok := true
	var center := Town.cell_center(cell)
	if Town.KINDS.has(selected):
		var origin := _origin(cell)
		size = Town.rotated_size(selected, rot)
		height = 1.0
		ok = town.can_place(selected, origin, rot)
		center = Town.footprint_center(selected, origin, rot)
	elif selected == "path":
		ok = Town.in_bounds(cell) and not town.occupied.has(cell)
	else:
		ok = town.occupied.has(cell) or town.paths.has(cell)
	(_ghost.mesh as BoxMesh).size = Vector3(size.x * Town.TILE - 0.1, height, size.y * Town.TILE - 0.1)
	_ghost.position = center + Vector3(0, height / 2.0 + 0.05, 0)
	_ghost_mat.albedo_color = OK_COLOR if ok else BLOCKED_COLOR


func _unhandled_input(event: InputEvent) -> void:
	if not active:
		return
	if event.is_action_pressed("rotate_piece"):
		rot = (rot + 1) % 4
	elif event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			_painting = event.pressed
			if event.pressed:
				_apply(false)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			_erasing = event.pressed
			if event.pressed:
				_apply(true)
	elif event is InputEventMouseMotion:
		if _erasing:
			_apply(true)
		elif _painting and selected in ["path", "remove"]:
			_apply(false)


func _apply(erase: bool) -> void:
	var cell: Variant = _hover_cell()
	if cell == null:
		return
	if erase or selected == "remove":
		town.remove_at(cell)
	elif selected == "path":
		town.set_path(cell, true)
	else:
		town.place(selected, _origin(cell), rot)


## Centres a multi-tile footprint on the hovered cell.
func _origin(cell: Vector2i) -> Vector2i:
	var s := Town.rotated_size(selected, rot)
	return cell - Vector2i(floori((s.x - 1) / 2.0), floori((s.y - 1) / 2.0))


func _hover_cell() -> Variant:
	var mouse := get_viewport().get_mouse_position()
	var from := camera.project_ray_origin(mouse)
	var dir := camera.project_ray_normal(mouse)
	var hit: Variant = Plane(Vector3.UP, 0.0).intersects_ray(from, dir)
	if hit == null:
		return null
	var cell := Town.world_to_cell(hit)
	return cell if Town.in_bounds(cell) else null
