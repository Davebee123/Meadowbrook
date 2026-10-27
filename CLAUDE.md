# Working on Meadowbrook

A cozy community builder in Godot 4.3. docs/design.md is the design document, docs/plan.md the build order and the
open questions, and README.md the controls and code map.

## Workflow

- **Docs.** Keep README.md (controls, code map) in sync with the code, in the same commit. When a decision closes an
  open question in docs/plan.md, record the answer there.
- **Check before committing.** If Godot is available, run `godot --headless --path . --quit` and make sure it reports
  no script errors.
- **Scale.** Real metres: a tile is 4 m, eye height 1.6 m. New models and pieces keep to this.
- **Code style.** Typed GDScript, tabs, scripts loaded by `preload` constants rather than `class_name`, so the project
  runs without an editor import first.
- **Screenshots and scratch scripts** go in the session's scratchpad, never in the repository.
- **Commits.** No pull requests unless asked. No model names in code, comments, commits or PR text.

## Scope

Build a small world that feels wonderful before building a large one. Anything in design.md §9 stays out until the
first playable milestone is done.
