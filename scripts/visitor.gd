extends CharacterBody3D
## The first-person visitor: walk the town you built, at human scale.
## WASD walks, Shift hurries, the mouse looks. Esc frees the mouse; a click takes it back.

const WALK_SPEED := 3.2
const HURRY_SPEED := 6.0
const GRAVITY := 18.0
const LOOK_SENSITIVITY := 0.0025
const EYE_HEIGHT := 1.6

var camera: Camera3D
var active := false


func _ready() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.75
	shape.shape = capsule
	shape.position.y = 0.875
	add_child(shape)
	camera = Camera3D.new()
	camera.position.y = EYE_HEIGHT
	camera.fov = 70.0
	camera.near = 0.05
	add_child(camera)
	set_active(false)


func set_active(on: bool) -> void:
	active = on
	camera.current = on
	set_physics_process(on)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if on else Input.MOUSE_MODE_VISIBLE


## Puts the visitor on the ground at pos, looking along yaw (radians).
func arrive(pos: Vector3, yaw: float) -> void:
	global_position = pos
	rotation = Vector3(0, yaw, 0)
	camera.rotation = Vector3.ZERO
	velocity = Vector3.ZERO


func _unhandled_input(event: InputEvent) -> void:
	if not active:
		return
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * LOOK_SENSITIVITY)
		camera.rotate_x(-event.relative.y * LOOK_SENSITIVITY)
		camera.rotation.x = clampf(camera.rotation.x, deg_to_rad(-85), deg_to_rad(85))
	elif event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _physics_process(delta: float) -> void:
	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var dir := (transform.basis * Vector3(input.x, 0, input.y)).normalized()
	var speed := HURRY_SPEED if Input.is_action_pressed("hurry") else WALK_SPEED
	velocity.x = dir.x * speed
	velocity.z = dir.z * speed
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY * delta
	move_and_slide()
