# Meadowbrook

Cozy community builder, Godot 4.3. Design: docs/design.md. Build order and open questions: docs/plan.md. Controls and
code map: README.md. Read narrowly: grep, then read only the part you need.

## How to work

- **Mistakes:** don't apologise. A mistake means a gap in the instruction files: name the gap and propose the fix.
- **YAGNI.** Don't overengineer or widen scope without permission. Suggest scope changes when they're worth it. Every
  change must be justifiable.
- **Engineering level:** scale effort to the task, from quick-and-dirty (greybox, throwaway) to production-grade
  (systems that ship). Most work is greybox until the first playable milestone.
- **Review:** after changing anything, spawn a subagent (Agent tool, `model: haiku`) with minimal context (the diff and the files
  it touches) to look for problems. Fix what it finds that holds up.

## Conventions

- Typed GDScript, tabs. Load scripts by `preload` constants, not `class_name`, so it runs without an editor import.
- Real metres: a tile is 4 m, eye height 1.6 m.
- Keep README.md in sync with the code, in the same commit. Record closed open questions in docs/plan.md.
- Before committing, if Godot is available: `godot --headless --path . --quit`, with no script errors.
- Assets: follow docs/assets.md (conventions, build, import, preview). Never accept an asset from code running; look
  at its preview renders. The town waits until the slice is approved.
- Cloud setup (Blender via PyPI, Godot from GitHub releases, software Vulkan): docs/assets.md, "Running it in a cloud
  session". Install Blender in the background; it takes about 15 min.
- Scratch scripts and screenshots go in the session scratchpad, never the repository.
- No pull requests unless asked. No model names in code, comments, commits or PR text.
- Scope: design.md §9 stays out until the core building and exploring experiences are proven.
