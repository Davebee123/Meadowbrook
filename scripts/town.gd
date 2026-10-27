extends Node3D
## The community: what is built where. Owns the layout data, rebuilds the
## greybox models from it, and saves it to JSON.

signal changed

const TILE := 4.0          # metres per grid tile
const SIZE := 32           # tiles per side of the plot
const SAVE_PATH := "user://town.json"
const SAVE_VERSION := 1

## Everything that can be placed. size is the footprint in tiles before
## rotation; the front of each model faces +Z at rot 0.
const KINDS := {
	"house": {"name": "House", "size": Vector2i(2, 2), "style": "house",
		"height": 5.5, "wall": Color("e6dcc6"), "roof": Color("575c66")},
	"cottage": {"name": "Cottage", "size": Vector2i(2, 2), "style": "house",
		"height": 4.0, "wall": Color("d8b48a"), "roof": Color("9a4f3a")},
	"family_home": {"name": "Family home", "size": Vector2i(3, 2), "style": "house",
		"height": 6.5, "wall": Color("c9cfd3"), "roof": Color("4a5560")},
	"townhouse": {"name": "Townhouse", "size": Vector2i(3, 2), "style": "townhouse",
		"height": 9.0, "wall": Color("9c5a44"), "roof": Color("3f444c")},
	"cafe": {"name": "Café", "size": Vector2i(2, 2), "style": "cafe",
		"height": 4.5, "wall": Color("a8634a"), "roof": Color("5b5048"), "awning": Color("c9a24a")},
	"tree": {"name": "Tree", "size": Vector2i(1, 1), "style": "tree"},
	"bush": {"name": "Bush", "size": Vector2i(1, 1), "style": "bush"},
	"bench": {"name": "Bench", "size": Vector2i(1, 1), "style": "bench"},
	"lamp": {"name": "Streetlight", "size": Vector2i(1, 1), "style": "lamp"},
}

const PATH_COLOR := Color("cdbb9e")

var objects := {}      # id -> {"kind": String, "cell": Vector2i, "rot": int}
var occupied := {}     # Vector2i -> id
var paths := {}        # Vector2i -> true
var _next_id := 1
var _nodes := {}       # id -> Node3D
var _path_nodes := {}  # Vector2i -> Node3D


# --- Grid -------------------------------------------------------------------

static func in_bounds(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < SIZE and cell.y < SIZE


static func world_to_cell(p: Vector3) -> Vector2i:
	return Vector2i(floori(p.x / TILE + SIZE / 2.0), floori(p.z / TILE + SIZE / 2.0))


## The world position of a cell's north-west corner.
static func cell_corner(cell: Vector2i) -> Vector3:
	return Vector3((cell.x - SIZE / 2.0) * TILE, 0.0, (cell.y - SIZE / 2.0) * TILE)


static func cell_center(cell: Vector2i) -> Vector3:
	return cell_corner(cell) + Vector3(TILE / 2.0, 0.0, TILE / 2.0)


static func rotated_size(kind: String, rot: int) -> Vector2i:
	var s: Vector2i = KINDS[kind]["size"]
	return Vector2i(s.y, s.x) if rot % 2 == 1 else s


static func footprint(kind: String, origin: Vector2i, rot: int) -> Array[Vector2i]:
	var s := rotated_size(kind, rot)
	var cells: Array[Vector2i] = []
	for x in s.x:
		for y in s.y:
			cells.append(origin + Vector2i(x, y))
	return cells


static func footprint_center(kind: String, origin: Vector2i, rot: int) -> Vector3:
	var s := rotated_size(kind, rot)
	return cell_corner(origin) + Vector3(s.x * TILE / 2.0, 0.0, s.y * TILE / 2.0)


# --- Editing ----------------------------------------------------------------

func can_place(kind: String, origin: Vector2i, rot: int) -> bool:
	for c in footprint(kind, origin, rot):
		if not in_bounds(c) or occupied.has(c) or paths.has(c):
			return false
	return true


func place(kind: String, origin: Vector2i, rot: int) -> int:
	if not KINDS.has(kind) or not can_place(kind, origin, rot):
		return 0
	var id := _next_id
	_next_id += 1
	objects[id] = {"kind": kind, "cell": origin, "rot": rot}
	for c in footprint(kind, origin, rot):
		occupied[c] = id
	var node := make_model(kind)
	node.position = footprint_center(kind, origin, rot)
	node.rotation.y = rot * PI / 2.0
	add_child(node)
	_nodes[id] = node
	changed.emit()
	return id


func set_path(cell: Vector2i, on: bool) -> bool:
	if on == paths.has(cell) or not in_bounds(cell) or (on and occupied.has(cell)):
		return false
	if on:
		paths[cell] = true
		var tile := _box(Vector3(TILE, 0.06, TILE), PATH_COLOR)
		tile.position = cell_center(cell) + Vector3(0, 0.03, 0)
		add_child(tile)
		_path_nodes[cell] = tile
	else:
		paths.erase(cell)
		_path_nodes[cell].queue_free()
		_path_nodes.erase(cell)
	changed.emit()
	return true


## Removes whatever is on the cell: a building or prop first, then a path.
func remove_at(cell: Vector2i) -> bool:
	if occupied.has(cell):
		var id: int = occupied[cell]
		var o: Dictionary = objects[id]
		for c in footprint(o["kind"], o["cell"], o["rot"]):
			occupied.erase(c)
		objects.erase(id)
		_nodes[id].queue_free()
		_nodes.erase(id)
		changed.emit()
		return true
	return set_path(cell, false)


func clear() -> void:
	for n in _nodes.values():
		n.queue_free()
	for n in _path_nodes.values():
		n.queue_free()
	objects.clear()
	occupied.clear()
	paths.clear()
	_nodes.clear()
	_path_nodes.clear()
	_next_id = 1
	changed.emit()


# --- Save and load ----------------------------------------------------------

func to_dict() -> Dictionary:
	var objs := []
	for o in objects.values():
		objs.append({"kind": o["kind"], "x": o["cell"].x, "y": o["cell"].y, "rot": o["rot"]})
	var path_list := []
	for c in paths.keys():
		path_list.append([c.x, c.y])
	return {"version": SAVE_VERSION, "objects": objs, "paths": path_list}


func from_dict(data: Dictionary) -> void:
	clear()
	for p in data.get("paths", []):
		set_path(Vector2i(int(p[0]), int(p[1])), true)
	for o in data.get("objects", []):
		place(str(o["kind"]), Vector2i(int(o["x"]), int(o["y"])), int(o["rot"]))


func save_town() -> bool:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(to_dict(), "\t"))
	return true


func load_town() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if not data is Dictionary:
		return false
	from_dict(data)
	return true


# --- Greybox models ---------------------------------------------------------

## Builds a kind's model centred on its footprint, front facing +Z.
## Buildings get a collision box so the visitor can't walk through them.
static func make_model(kind: String) -> Node3D:
	var k: Dictionary = KINDS[kind]
	var s: Vector2i = k["size"]
	var w := s.x * TILE
	var d := s.y * TILE
	var root := Node3D.new()
	root.name = kind
	match k["style"]:
		"house", "townhouse":
			var bw := w - 0.8
			var bd := d - 2.0
			var h: float = k["height"]
			_add(root, _box(Vector3(bw, h, bd), k["wall"]), Vector3(0, h / 2.0, -0.4))
			var roof := MeshInstance3D.new()
			var prism := PrismMesh.new()
			var roof_h := 2.6 if k["style"] == "house" else 1.6
			prism.size = Vector3(bd + 0.6, roof_h, bw + 0.4)
			roof.mesh = prism
			roof.material_override = _mat(k["roof"])
			roof.rotation.y = PI / 2.0  # ridge runs along the width
			_add(root, roof, Vector3(0, h + roof_h / 2.0, -0.4))
			_add(root, _box(Vector3(1.1, 2.2, 0.15), Color("4b3a2e")), Vector3(0, 1.1, bd / 2.0 - 0.4 + 0.05))
			_add(root, _solid(Vector3(bw, h, bd)), Vector3(0, h / 2.0, -0.4))
		"cafe":
			# Building at the back, a terrace with tables out front.
			var bw := w - 0.8
			var bd := d * 0.55
			var h: float = k["height"]
			var bz := -d / 2.0 + 0.4 + bd / 2.0
			_add(root, _box(Vector3(bw, h, bd), k["wall"]), Vector3(0, h / 2.0, bz))
			_add(root, _box(Vector3(bw + 0.3, 0.4, bd + 0.3), k["roof"]), Vector3(0, h + 0.2, bz))
			var awning := _box(Vector3(bw, 0.12, 1.8), k["awning"])
			awning.rotation.x = deg_to_rad(18)
			_add(root, awning, Vector3(0, 3.0, bz + bd / 2.0 + 0.8))
			_add(root, _box(Vector3(w - 0.4, 0.08, d - bd - 0.6), Color("b9a587")), Vector3(0, 0.04, bz + bd / 2.0 + (d - bd - 0.6) / 2.0))
			for x in [-w / 4.0, w / 4.0]:
				var tz := bz + bd / 2.0 + 2.2
				_add(root, _cylinder(0.45, 0.75, Color("efe7d8")), Vector3(x, 0.375, tz))
				_add(root, _cylinder(0.04, 2.3, Color("6b5d4f")), Vector3(x, 1.15, tz))
				_add(root, _cylinder(1.1, 0.12, Color("f2ede2")), Vector3(x, 2.3, tz))
			_add(root, _solid(Vector3(bw, h, bd)), Vector3(0, h / 2.0, bz))
		"tree":
			_add(root, _cylinder(0.18, 2.0, Color("6b4f38")), Vector3(0, 1.0, 0))
			_add(root, _sphere(1.6, Color("5f7f3a")), Vector3(0, 3.2, 0))
			_add(root, _solid(Vector3(0.4, 2.0, 0.4)), Vector3(0, 1.0, 0))
		"bush":
			_add(root, _sphere(0.8, Color("6f8f45")), Vector3(0, 0.5, 0))
		"bench":
			_add(root, _box(Vector3(1.8, 0.1, 0.5), Color("8a6a4a")), Vector3(0, 0.45, 0))
			_add(root, _box(Vector3(1.8, 0.5, 0.08), Color("8a6a4a")), Vector3(0, 0.75, -0.22))
			_add(root, _solid(Vector3(1.8, 0.9, 0.5)), Vector3(0, 0.45, 0))
		"lamp":
			_add(root, _cylinder(0.06, 4.0, Color("3d4248")), Vector3(0, 2.0, 0))
			_add(root, _sphere(0.25, Color("f3e3b5")), Vector3(0, 4.1, 0))
			_add(root, _solid(Vector3(0.2, 4.0, 0.2)), Vector3(0, 2.0, 0))
	return root


static func _add(parent: Node3D, child: Node3D, pos: Vector3) -> void:
	child.position = pos
	parent.add_child(child)


static func _mat(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.9
	return m


static func _box(size: Vector3, color: Color) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mi.mesh = mesh
	mi.material_override = _mat(color)
	return mi


static func _cylinder(radius: float, height: float, color: Color) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = height
	mi.mesh = mesh
	mi.material_override = _mat(color)
	return mi


static func _sphere(radius: float, color: Color) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mi.mesh = mesh
	mi.material_override = _mat(color)
	return mi


static func _solid(size: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	return body
