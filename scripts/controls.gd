extends RefCounted
## The game's input actions, registered in code so scenes share one definition.


static func register() -> void:
	var keys := {
		"move_forward": [KEY_W, KEY_UP],
		"move_back": [KEY_S, KEY_DOWN],
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"hurry": [KEY_SHIFT],
		"turn_left": [KEY_Q],
		"turn_right": [KEY_E],
		"rotate_piece": [KEY_R],
		"toggle_walk": [KEY_TAB],
		"quick_save": [KEY_F5],
	}
	for action in keys:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for key in keys[action]:
			var e := InputEventKey.new()
			e.physical_keycode = key
			InputMap.action_add_event(action, e)
