extends Camera3D
## A fixed inspection camera that aims at a point, so scenes can place it by eye rather than by rotation.

@export var target := Vector3.ZERO


func _ready() -> void:
	look_at(target)
