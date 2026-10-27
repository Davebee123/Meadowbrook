extends CanvasLayer
## The build bar along the bottom and a short status line. Placeholder look:
## warm cream panel, to be replaced once the visual style sheet is settled.

signal tool_picked(id: String)
signal walk_pressed
signal save_pressed
signal load_pressed
signal clear_pressed

const Town := preload("res://scripts/town.gd")

const PANEL := Color("f4eee1")
const INK := Color("3b3a36")
const SELECTED := Color("8fa65a")

var _bar: Control
var _status: Label
var _walk_hint: Label
var _crosshair: Label
var _buttons := {}  # tool id -> Button


func _ready() -> void:
	var root := Control.new()
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", _style(PANEL, 10))
	root.add_child(panel)
	_bar = panel

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	panel.add_child(row)

	for kind in ["house", "cottage", "family_home", "townhouse", "cafe"]:
		_add_tool(row, kind, Town.KINDS[kind]["name"], "Building. Click to place it, R to rotate it.")
	row.add_child(VSeparator.new())
	_add_tool(row, "path", "Path", "A paved path. Drag to lay a run of it.")
	for kind in ["tree", "bush", "bench", "lamp"]:
		_add_tool(row, kind, Town.KINDS[kind]["name"], "Landscaping. Click to place it.")
	_add_tool(row, "remove", "Remove", "Removes whatever you click. Right click does this with any tool.")
	row.add_child(VSeparator.new())
	_add_action(row, "Walk", "Step into the town in first person. Tab switches back and forth.", walk_pressed)
	_add_action(row, "Save", "Saves the town.", save_pressed)
	_add_action(row, "Load", "Loads the last saved town.", load_pressed)
	_add_action(row, "Clear", "Clears the plot.", clear_pressed)

	# Pinned to the bottom centre; it grows up and out to fit its buttons.
	panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	panel.offset_left = 0
	panel.offset_right = 0
	panel.offset_top = -16
	panel.offset_bottom = -16

	_status = Label.new()
	_status.add_theme_color_override("font_color", Color.WHITE)
	_status.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	_status.position = Vector2(20, 16)
	root.add_child(_status)

	_walk_hint = Label.new()
	_walk_hint.text = "Tab: back to building"
	_walk_hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.75))
	_walk_hint.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	_walk_hint.position = Vector2(20, 16)
	_walk_hint.visible = false
	root.add_child(_walk_hint)

	_crosshair = Label.new()
	_crosshair.text = "·"
	_crosshair.visible = false
	_crosshair.set_anchors_preset(Control.PRESET_CENTER)
	_crosshair.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_crosshair.grow_vertical = Control.GROW_DIRECTION_BOTH
	root.add_child(_crosshair)

	highlight("house")


func set_walking(on: bool) -> void:
	_bar.visible = not on
	_status.visible = not on
	_walk_hint.visible = on
	_crosshair.visible = on


func show_status(text: String) -> void:
	_status.text = text
	var t := create_tween()
	_status.modulate.a = 1.0
	t.tween_interval(2.0)
	t.tween_property(_status, "modulate:a", 0.0, 0.6)


func highlight(id: String) -> void:
	for t in _buttons:
		var b: Button = _buttons[t]
		b.add_theme_stylebox_override("normal", _style(SELECTED if t == id else Color(0, 0, 0, 0), 6))


func _add_tool(row: HBoxContainer, id: String, label: String, tip: String) -> void:
	var b := _button(label, tip)
	b.pressed.connect(func() -> void:
		highlight(id)
		tool_picked.emit(id))
	_buttons[id] = b
	row.add_child(b)


func _add_action(row: HBoxContainer, label: String, tip: String, sig: Signal) -> void:
	var b := _button(label, tip)
	b.pressed.connect(func() -> void: sig.emit())
	row.add_child(b)


func _button(label: String, tip: String) -> Button:
	var b := Button.new()
	b.text = label
	b.tooltip_text = tip
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(72, 40)
	b.add_theme_color_override("font_color", INK)
	b.add_theme_color_override("font_hover_color", INK)
	b.add_theme_color_override("font_pressed_color", INK)
	b.add_theme_stylebox_override("normal", _style(Color(0, 0, 0, 0), 6))
	b.add_theme_stylebox_override("hover", _style(Color(0, 0, 0, 0.07), 6))
	b.add_theme_stylebox_override("pressed", _style(Color(0, 0, 0, 0.12), 6))
	return b


static func _style(color: Color, radius: int) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = color
	s.set_corner_radius_all(radius)
	s.set_content_margin_all(8)
	return s
