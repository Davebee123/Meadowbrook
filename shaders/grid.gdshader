// Faint tile lines over the ground, shown only while building.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

uniform float tile = 4.0;
uniform vec4 line_color : source_color = vec4(1.0, 0.98, 0.9, 0.22);

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 p = world_pos.xz / tile;
	vec2 d = abs(fract(p + 0.5) - 0.5) / fwidth(p);
	float line = 1.0 - min(min(d.x, d.y), 1.0);
	ALBEDO = line_color.rgb;
	ALPHA = line * line_color.a;
}
