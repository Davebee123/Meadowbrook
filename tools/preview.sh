#!/usr/bin/env bash
# Imports new or changed assets, then renders them on the preview stage (tools/preview.gd).
# Usage: tools/preview.sh <out_dir> res://assets/<folder>/<name>.glb[@x,y,z] [...]
# Needs: GODOT pointing at a Godot 4.3 binary; on a machine without a display, xvfb-run.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
"$GODOT" --headless --import --path . >/dev/null 2>&1
run=("$GODOT" --path . --rendering-driver vulkan --resolution 1600x900 -s res://tools/preview.gd -- "$@")
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null; then
	xvfb-run -a -s "-screen 0 1600x900x24" "${run[@]}"
else
	"${run[@]}"
fi
