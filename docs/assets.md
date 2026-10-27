# Asset pipeline

How a model gets from an idea into the game: conventions, the build and import workflow, the preview that every asset
passes, and what the project depends on. The look itself is in docs/style.md.

## Audit (before the vertical slice)

What the project had when the pipeline was set up, and what the pipeline changes.

| Area | Before | Now |
| --- | --- | --- |
| Renderer | Godot 4.3, Forward+, MSAA 2×, 4096 directional shadow map | Same, plus high-quality soft shadow filtering (project.godot) |
| Lighting | Built in code in scripts/main.gd: procedural sky, filmic tonemap, SSAO, glow, one warm sun at 38° | scenes/lighting/daylight.tscn, a reusable scene: sky fill, SSAO and SSIL, filmic, a sun at 45° with filtered soft shadows. Used by the slice and the preview; the game's main scene still has its own until the slice is approved |
| Camera | scripts/iso_camera.gd: orthographic, 35.264° tilt, 45° yaw, 48 m tall view by default; scripts/visitor.gd: first person, 1.6 m eye height, 70° field of view | Unchanged; the slice reuses the builder's camera |
| Models | None. Greybox shapes built in GDScript (scripts/town.gd, make_model) | Blender-authored GLBs in assets/, with .blend sources in blender/src/ |
| Materials | Flat StandardMaterial3D colours in code | One shared table of named materials (blender/toy.py, MATERIALS), mirrored in docs/style.md |
| Input | Registered inside scripts/main.gd | scripts/controls.gd, shared by the game and the slice |

To be replaced once the slice is approved: the greybox house, cottage, family home, townhouse, tree, bush, bench and
streetlight in scripts/town.gd. The café (assets/buildings/cafe.glb) is parked: it's in an earlier, realistic style.

## Conventions

- **Units and axes:** metres, Y up in Godot. In Blender, Z is up and the front faces -Y, so it faces +Z in Godot.
- **Origin:** the centre of the footprint at ground level. Lots are whole 4 m tiles (house_a: 3 × 4 tiles, 12 × 16 m).
- **Files:** assets/<buildings|nature|street>/<name>.glb, with the source at blender/src/<name>.blend and the script
  that builds it in blender/build_<group>.py.
- **Materials:** named from the shared table, so `stucco` or `frame` means the same colour in every asset. Foliage is
  one material, `foliage`, coloured per vertex.
- **No lights or cameras in a GLB.** They arrive at uncontrolled strength. Lot scenes add their own lights.
- **Collision:** a separate box mesh named `<name>-colonly`; Godot turns it into a static body.
- **Plants and props are separate assets,** placed by a lot scene (scenes/lots/house_a_lot.tscn), so the same bush
  serves every lot.
- **Budgets:** the triangle budgets in docs/style.md.

## Building and importing

1. Write or change the build script, then run it with Blender's Python:
   `<blender-venv>/bin/python blender/build_house.py` (or `build_nature.py`, `build_street.py`, optionally with asset
   names). It writes the GLB and the .blend source, and prints the triangle count.
2. Import into Godot: `godot --headless --import --path .`. Godot's default import settings are used: levels of
   detail and shadow meshes on.
3. Preview the asset (below). Iterate until it passes.
4. Place it: in a lot scene for buildings and planting, or directly in a scene.

blender/ carries a `.gdignore`: Godot tries to import .blend files through a local Blender install, and without one,
a headless import waits forever.

## Previewing an asset

`tools/preview.sh <out_dir> res://assets/<group>/<name>.glb[@x,y,z] [...]` imports, then renders each asset on the
preview stage (scenes/preview.tscn: the daylight scene, a lawn, and a 1.75 m figure for scale):

| File | View |
| --- | --- |
| `<name>_builder.png` | the builder's camera at the game's default zoom |
| `<name>_close.png` | the same angle, framed on the asset |
| `<name>_eye3m.png`, `<name>_eye1m.png` | eye level (1.6 m, 70°) at 3 m and 1 m from the focus point |
| `<name>_x100.png` | a 10 × 10 block of copies |
| `report.md` | size, triangles, and draw calls and primitives for the block of 100 |

`@x,y,z` sets the focus point for the eye-level views (house_a uses its door: `@-1.6,1.6,2.5`).

An asset is accepted when, in those renders:

- its silhouette and proportions match docs/style.md and the reference;
- windows and doors line up, and nothing intersects, floats or shows a hole;
- materials come from the shared table and read clearly at both distances;
- foliage has a clear silhouette and colour variation;
- shadows ground it;
- it is inside its triangle budget, and 100 copies stay at a few hundred draw calls or fewer.

To check a whole scene from its cameras: `godot --path . -s res://tools/shot.gd -- res://scenes/slice.tscn <out_dir>
Builder,BuilderClose,EyeStreet,EyeDoor`.

## Running it in a cloud session

- **Blender:** `python3.13 -m venv <dir> && <dir>/bin/pip install bpy==5.2.3`, in the background (about 15 minutes).
  download.blender.org is blocked; PyPI isn't.
- **Godot:** Godot_v4.3-stable_linux.x86_64.zip from the godotengine/godot GitHub releases.
- **Rendering without a GPU:** `apt-get install mesa-vulkan-drivers` (software Vulkan), then run Godot under
  `xvfb-run` with `--rendering-driver vulkan`. tools/preview.sh does the xvfb part itself. A render takes about 20 s.

## External assets, formats, dependencies and licences

| Item | Use | Licence |
| --- | --- | --- |
| Third-party art | None. Every model is authored in this repository. | — |
| Godot 4.3 | engine | MIT |
| Blender 5.2.3 (as the `bpy` Python module) | modelling and export | GPL-3.0 for the tool; models made with it belong to their author |
| numpy | texture and geometry maths in the build scripts | BSD-3-Clause |
| Mesa (lavapipe), Xvfb | software rendering for headless previews only | MIT |
| glTF 2.0 binary (.glb) | model format the game loads | open standard |
| .blend | editable model sources | — |

Kenney, Quaternius and Poly Haven (all CC0) can't be reached from cloud sessions. Packs from them would need adding to
the repository by hand, with their licence file next to them.

## The vertical slice

scenes/slice.tscn: house_a on its lot (scenes/lots/house_a_lot.tscn) with three trees, shrubs, topiaries, window-box
planting, a picket fence and a mailbox; a 32 m street with sidewalks, three lamps and a bench; a hedge and flower bed
across the road; the daylight scene. 1–4 switch to the fixed cameras (builder at gameplay zoom, builder close, eye
level from the street, eye level at the door); 0 returns to the movable builder's camera.

The whole scene draws in about 100 draw calls and 180 000 primitives, shadows included.

## Remaining differences from the reference

- **Plant detail:** the reference's bushes are crisp clusters of distinct round leaf balls; ours are softer fused
  lumps. The flowers are smaller and fewer.
- **Interiors:** the reference shows furnished, lamp-lit rooms; ours are a warm glow with one furniture block and a
  curtain.
- **Surface finish:** the reference has a faint plaster texture and soft colour variation on walls; ours are flat.
- **Roof:** the shingle courses step only slightly and read faintly from the builder's camera.
- **Light:** the reference is lit like a studio product shot, with a strong rim and very soft shadows. Ours is
  outdoor daylight; shadows are softer than before but still harder than the reference's.
- **Lot base:** the reference sits on a raised, rounded paver plinth. Our lots are flush with the ground, as a town
  needs.
- **Not yet in the game:** the slice is its own scene. The builder's placement tools still use the greybox shapes.
