extends Node3D
## Meadowbrook greybox: lay out a street from above, then step in and walk it.

const Town := preload("res://scripts/town.gd")
const IsoCamera := preload("res://scripts/iso_camera.gd")
const Visitor := preload("res://scripts/visitor.gd")
const BuildTool := preload("res://scripts/build_tool.gd")
const Hud := preload("res://scripts/hud.gd")
const Controls := preload("res://scripts/controls.gd")

const GRASS := Color("7f9a52")
const MEADOW := Color("6c8546")

var town: Town
var iso: IsoCamera
var visitor: Visitor
var build: BuildTool
var hud: Hud
var walking := false
var _grid: MeshInstance3D


func _ready() -> void:
	Controls.register()
	_make_environment()
	_make_ground()

	town = Town.new()
	add_child(town)
	iso = IsoCamera.new()
	add_child(iso)
	visitor = Visitor.new()
	add_child(visitor)
	build = BuildTool.new()
	build.town = town
	build.camera = iso.camera
	add_child(build)
	hud = Hud.new()
	add_child(hud)

	hud.tool_picked.connect(build.set_tool)
	hud.walk_pressed.connect(_toggle_walk)
	hud.save_pressed.connect(func() -> void:
		hud.show_status("Saved." if town.save_town() else "Couldn't save."))
	hud.load_pressed.connect(func() -> void:
		hud.show_status("Loaded." if town.load_town() else "No saved town yet."))
	hud.clear_pressed.connect(town.clear)

	iso.set_active(true)
	if town.load_town():
		hud.show_status("Welcome back.")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_walk"):
		_toggle_walk()
	elif event.is_action_pressed("quick_save"):
		hud.show_status("Saved." if town.save_town() else "Couldn't save.")


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST and town != null:
		town.save_town()


func _toggle_walk() -> void:
	walking = not walking
	if walking:
		var yaw := iso.facing()
		visitor.arrive(_free_spot(iso.focus()), yaw)
	visitor.set_active(walking)
	iso.set_active(not walking)
	build.set_active(not walking)
	hud.set_walking(walking)
	_grid.visible = not walking


## The nearest open tile to pos, so the visitor never arrives inside a building.
func _free_spot(pos: Vector3) -> Vector3:
	var start := Town.world_to_cell(pos)
	for r in Town.SIZE:
		for dx in range(-r, r + 1):
			for dy in range(-r, r + 1):
				var c := start + Vector2i(dx, dy)
				if Town.in_bounds(c) and not town.occupied.has(c):
					return Town.cell_center(c)
	return Vector3.ZERO


func _make_environment() -> void:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("8fb4d6")
	sky_mat.sky_horizon_color = Color("f1dcc0")
	sky_mat.ground_horizon_color = Color("f1dcc0")
	sky_mat.ground_bottom_color = Color("6c7a55")
	sky_mat.sun_angle_max = 20.0
	var sky := Sky.new()
	sky.sky_material = sky_mat

	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.8
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	env.ssao_intensity = 1.2
	env.glow_enabled = true
	env.glow_intensity = 0.3
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)

	# Low, warm late-afternoon sun: the model-village light from the concept art.
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-38, -40, 0)
	sun.light_color = Color("ffe2b8")
	sun.light_energy = 1.3
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 220.0
	add_child(sun)


func _make_ground() -> void:
	var plot := Town.SIZE * Town.TILE

	var meadow := MeshInstance3D.new()
	var meadow_mesh := PlaneMesh.new()
	meadow_mesh.size = Vector2(plot * 4.0, plot * 4.0)
	meadow.mesh = meadow_mesh
	meadow.material_override = Town._mat(MEADOW)
	meadow.position.y = -0.02
	add_child(meadow)

	var ground := MeshInstance3D.new()
	var ground_mesh := PlaneMesh.new()
	ground_mesh.size = Vector2(plot, plot)
	ground.mesh = ground_mesh
	ground.material_override = Town._mat(GRASS)
	add_child(ground)

	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	floor_shape.shape = WorldBoundaryShape3D.new()
	floor_body.add_child(floor_shape)
	add_child(floor_body)

	# Keep the visitor on the plot.
	for side in [Vector3(1, 0, 0), Vector3(-1, 0, 0), Vector3(0, 0, 1), Vector3(0, 0, -1)]:
		var wall := StaticBody3D.new()
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(1, 6, plot) if side.x != 0 else Vector3(plot, 6, 1)
		shape.shape = box
		wall.add_child(shape)
		wall.position = side * (plot / 2.0 + 0.5) + Vector3(0, 3, 0)
		add_child(wall)

	_grid = MeshInstance3D.new()
	var grid_mesh := PlaneMesh.new()
	grid_mesh.size = Vector2(plot, plot)
	_grid.mesh = grid_mesh
	var grid_mat := ShaderMaterial.new()
	grid_mat.shader = preload("res://shaders/grid.gdshader")
	grid_mat.set_shader_parameter("tile", Town.TILE)
	_grid.material_override = grid_mat
	_grid.position.y = 0.08
	add_child(_grid)
