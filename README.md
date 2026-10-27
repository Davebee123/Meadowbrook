# Meadowbrook

A cozy community builder you can step inside. Build a neighbourhood from above, then walk into it in first person.
Godot 4.3.

The design is in [docs/design.md](docs/design.md); the build order and open questions are in [docs/plan.md](docs/plan.md).

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

Everything is built in code from `scenes/main.tscn`, so there are no scene files to keep in sync yet.

| File | Holds |
| --- | --- |
| `scripts/main.gd` | the scene: light, sky, ground, input actions, switching between building and walking |
| `scripts/town.gd` | the layout data (pieces, paths, occupancy), placement rules, save and load, greybox models |
| `scripts/build_tool.gd` | the placement ghost and mouse editing |
| `scripts/iso_camera.gd` | the angled orthographic builder's camera |
| `scripts/visitor.gd` | the first-person visitor |
| `scripts/hud.gd` | the build bar and status line |
| `shaders/grid.gdshader` | the tile lines shown while building |

**Scale.** One tile is 4 m and the plot is 32 × 32 tiles (128 m). Models are real size so first person feels right:
eye height is 1.6 m.
