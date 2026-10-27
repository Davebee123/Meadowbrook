extends SceneTree
## Renders a scene to PNG for checking without opening the editor.
## godot --path . -s res://tools/shot.gd -- <scene.tscn> <out_dir> [Camera,Camera,...] [frames]
## With camera names, renders one PNG per camera found anywhere under the scene; without, the scene's own view.

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	var out: String = args[1]
	DirAccess.make_dir_recursive_absolute(out)
	var names := args[2].split(",") if args.size() > 2 and args[2] != "" else PackedStringArray([""])
	var frames := int(args[3]) if args.size() > 3 else 12
	for name in names:
		if name != "":
			var cam := scene.find_child(name, true, false) as Camera3D
			if cam == null:
				push_error("No camera named %s" % name)
				continue
			cam.current = true
		for i in frames:
			await process_frame
		await RenderingServer.frame_post_draw
		var file := (name if name != "" else args[0].get_file().get_basename()) + ".png"
		root.get_texture().get_image().save_png(out.path_join(file))
	print("draw calls %d, primitives %d" % [
		RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),
		RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)])
	quit()
