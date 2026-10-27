# Meadowbrook

A cozy community builder you can step inside. Build a neighbourhood from above, then walk into it in first person.
Godot 4.3.

The design is in [docs/design.md](docs/design.md), the build order and open questions in [docs/plan.md](docs/plan.md),
and the measured look in [docs/style.md](docs/style.md).

## Running it

Open the folder in Godot 4.3 or later and press F5, or run `godot --path .` from here.

## Controls

**Building**

| Input | Does |
| --- | --- |
| WASD or arrows | pan |
| Mouse wheel | zoom |
| Q and E | turn the view a quarter |
| Left click | place the selected piece; drag to lay paths |
| Right click | remove whatever is under the cursor; drag to remove several |
| R | rotate the piece |
| Tab | step into the town |
| F5 | save |

**Walking**

| Input | Does |
| --- | --- |
| WASD and mouse | walk and look |
| Shift | hurry |
| Esc | free the mouse; click to take it back |
| Tab | back to building |

The town saves to `user://town.json` when you close the window, and loads when you start.

## Code map

The game is built in code from `scenes/main.tscn`. The art pipeline (Blender models, preview, import) is described in
[docs/assets.md](docs/assets.md).

| File | Holds |
| --- | --- |
| `scripts/main.gd` | the game scene: light, sky, ground, switching between building and walking |
| `scripts/controls.gd` | the input actions, shared by every scene |
| `scripts/town.gd` | the layout data (pieces, paths, occupancy), placement rules, save and load, greybox models |
| `scripts/build_tool.gd` | the placement ghost and mouse editing |
| `scripts/iso_camera.gd` | the angled orthographic builder's camera |
| `scripts/visitor.gd` | the first-person visitor |
| `scripts/hud.gd` | the build bar and status line |
| `shaders/grid.gdshader` | the tile lines shown while building |
| `scenes/slice.tscn`, `scripts/slice.gd` | the vertical slice: one finished house lot and street, for approval |
| `scenes/lots/house_a_lot.tscn` | house_a with its planting, fence, mailbox and porch light |
| `scenes/lighting/daylight.tscn` | the shared daylight: sky, sun, ambient and contact shading |
| `scenes/preview.tscn`, `tools/preview.gd`, `tools/preview.sh` | the asset preview stage and renderer |
| `tools/shot.gd` | renders a scene's cameras to PNG |
| `scripts/look_at_camera.gd` | a fixed camera that aims at a point |
| `assets/` | models (GLB): buildings, nature, street |
| `blender/` | the Python scripts that build every model, and their .blend sources in `blender/src/` |

**Scale.** One tile is 4 m and the plot is 32 × 32 tiles (128 m). Models are real size so first person feels right:
eye height is 1.6 m.
