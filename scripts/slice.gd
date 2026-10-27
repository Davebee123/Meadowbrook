extends Node3D
## The vertical-slice scene: the builder's camera by default; 1-4 switch to the fixed inspection cameras,
## 0 back to the builder's camera.

const Controls := preload("res://scripts/controls.gd")
const IsoCamera := preload("res://scripts/iso_camera.gd")

var iso: IsoCamera


func _ready() -> void:
	Controls.register()
	iso = IsoCamera.new()
	iso.position = Vector3(0, 0, 6)
	add_child(iso)
	iso.set_active(true)


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed):
		return
	var cameras := $Cameras.get_children()
	var n: int = event.keycode - KEY_1
	if n >= 0 and n < cameras.size():
		iso.set_active(false)
		(cameras[n] as Camera3D).current = true
	elif event.keycode == KEY_0:
		iso.set_active(true)
