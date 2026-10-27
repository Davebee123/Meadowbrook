extends Node3D
## The builder's camera: angled orthographic, the model-village view.
## WASD pans, the wheel zooms, Q and E turn the view a quarter at a time.

const PAN_SPEED := 22.0
const ZOOM_MIN := 12.0
const ZOOM_MAX := 110.0
const PITCH := -35.264  # true isometric tilt
const TURN_SPEED := 300.0  # degrees per second
const PLOT_HALF := 64.0  # half the plot, in metres (Town.SIZE * Town.TILE / 2)

var camera: Camera3D
var zoom := 48.0
var yaw := 45.0
var _target_yaw := 45.0
var _target_zoom := 48.0
var active := true


func _ready() -> void:
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = zoom
	camera.near = 0.1
	camera.far = 600.0
	camera.position = Vector3(0, 0, 200)
	add_child(camera)
	_apply()


func set_active(on: bool) -> void:
	active = on
	camera.current = on


func _process(delta: float) -> void:
	if not active:
		return
	var v := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	if v != Vector2.ZERO:
		var turn := Basis(Vector3.UP, deg_to_rad(yaw))
		var move := turn * Vector3(v.x, 0, v.y)
		position += move * PAN_SPEED * (zoom / 48.0) * delta
		position.x = clampf(position.x, -PLOT_HALF, PLOT_HALF)
		position.z = clampf(position.z, -PLOT_HALF, PLOT_HALF)
	yaw = move_toward(yaw, _target_yaw, TURN_SPEED * delta)
	zoom = lerpf(zoom, _target_zoom, minf(1.0, 12.0 * delta))
	_apply()


func _unhandled_input(event: InputEvent) -> void:
	if not active:
		return
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_target_zoom = clampf(_target_zoom * 0.9, ZOOM_MIN, ZOOM_MAX)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_target_zoom = clampf(_target_zoom * 1.1, ZOOM_MIN, ZOOM_MAX)
	elif event.is_action_pressed("turn_left"):
		_target_yaw -= 90.0
	elif event.is_action_pressed("turn_right"):
		_target_yaw += 90.0


## The ground point at the centre of the view.
func focus() -> Vector3:
	return Vector3(position.x, 0, position.z)


## Which way the view looks across the ground, as a yaw in radians.
func facing() -> float:
	return deg_to_rad(yaw)


func _apply() -> void:
	rotation_degrees = Vector3(PITCH, yaw, 0)
	camera.size = zoom
