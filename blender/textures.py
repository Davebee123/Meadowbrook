"""Seamless tiling textures, drawn with numpy so every pattern repeats exactly.

Each function returns (albedo, normal), float arrays of shape (h, w, 3) in sRGB 0..1; normal is an OpenGL-style
normal map, or None for flat surfaces. Sizes follow docs/style.md: 512 px per metre near the ground.
"""
import numpy as np


def hex_rgb(h):
	h = h.lstrip("#")
	return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def _value_noise(h, w, cells, rng):
	"""Periodic value noise: a random lattice of cells × cells, smoothly interpolated, wrapping at the edges."""
	lattice = rng.random((cells, cells))
	y = np.arange(h) * cells / h
	x = np.arange(w) * cells / w
	y0 = np.floor(y).astype(int)
	x0 = np.floor(x).astype(int)
	fy = y - y0
	fx = x - x0
	fy = fy * fy * (3 - 2 * fy)
	fx = fx * fx * (3 - 2 * fx)
	y1 = (y0 + 1) % cells
	x1 = (x0 + 1) % cells
	a = lattice[np.ix_(y0, x0)]
	b = lattice[np.ix_(y0, x1)]
	c = lattice[np.ix_(y1, x0)]
	d = lattice[np.ix_(y1, x1)]
	top = a + (b - a) * fx[None, :]
	bottom = c + (d - c) * fx[None, :]
	return top + (bottom - top) * fy[:, None]


def noise(h, w, seed, octaves=(4, 8, 16, 32, 64)):
	"""Tiling fractal noise, mean 0, roughly -1..1."""
	rng = np.random.default_rng(seed)
	total = np.zeros((h, w))
	amp = 1.0
	norm = 0.0
	for cells in octaves:
		total += amp * _value_noise(h, w, cells, rng)
		norm += amp
		amp *= 0.55
	return (total / norm - 0.5) * 2.0


def normal_from_height(height, metres_per_px, strength=1.0):
	"""OpenGL normal map from a height field in metres; wraps at the edges so it tiles."""
	dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) / (2 * metres_per_px)
	dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) / (2 * metres_per_px)
	# Image rows run downward; flip so +Y points up the texture.
	n = np.dstack([-dx * strength, dy * strength, np.ones_like(height)])
	n /= np.linalg.norm(n, axis=2, keepdims=True)
	return n * 0.5 + 0.5


def _hash(*ints):
	v = np.zeros_like(ints[0], dtype=np.uint64)
	for i, k in enumerate(ints):
		v ^= (k.astype(np.uint64) + np.uint64(0x9E3779B9) * np.uint64(i + 1)) * np.uint64(0x85EBCA6B)
		v ^= v >> np.uint64(13)
		v *= np.uint64(0xC2B2AE35)
		v ^= v >> np.uint64(16)
	return (v % np.uint64(10007)).astype(np.float64) / 10007.0


def brick(px=1024, tile=1.8):
	"""Running-bond brick, 215 × 65 mm bricks with 10 mm mortar: 8 bricks by 24 courses per 1.8 m tile."""
	m = tile / px
	cols, rows = 8, 24
	bw, bh = tile / cols, tile / rows
	y, x = np.mgrid[0:px, 0:px] * m
	row = np.floor(y / bh).astype(np.int64)
	xo = x + (row % 2) * bw / 2
	col = np.floor(xo / bw).astype(np.int64) % cols
	# Distance from the brick's edge, for mortar and soft brick edges.
	ex = np.minimum(xo % bw, bw - xo % bw)
	ey = np.minimum(y % bh, bh - y % bh)
	edge = np.minimum(ex, ey)
	mortar = edge < 0.005
	rnd = _hash(row % rows, col)
	rnd2 = _hash(col, row % rows + 101)
	base = hex_rgb("#9a5f4a")
	tone = 0.86 + 0.24 * rnd[..., None]
	warm = np.dstack([np.ones_like(rnd), 0.97 + 0.06 * rnd2, 0.95 + 0.08 * rnd2])
	grain = noise(px, px, 1, (32, 64, 128))[..., None]
	alb = base * tone * warm * (1 + 0.06 * grain)
	alb = np.where((rnd2 > 0.93)[..., None], alb * 0.78, alb)  # a few darker, overfired bricks
	mortar_col = hex_rgb("#c9b9a5") * (1 + 0.05 * grain)
	alb = np.where(mortar[..., None], mortar_col, alb)
	height = np.clip((edge - 0.005) / 0.004, 0, 1) * 0.006 + 0.0006 * grain[..., 0]
	return np.clip(alb, 0, 1), normal_from_height(height, m, 1.0)


def paving(px=1024, tile=2.0):
	"""400 mm square slabs with 6 mm joints: 5 × 5 per 2 m tile."""
	m = tile / px
	n = 5
	s = tile / n
	y, x = np.mgrid[0:px, 0:px] * m
	r = np.floor(y / s).astype(np.int64)
	c = np.floor(x / s).astype(np.int64)
	edge = np.minimum(np.minimum(x % s, s - x % s), np.minimum(y % s, s - y % s))
	joint = edge < 0.003
	rnd = _hash(r % n, c % n)
	grain = noise(px, px, 2, (16, 32, 64, 128))[..., None]
	alb = hex_rgb("#c8ab92") * (0.95 + 0.07 * rnd[..., None]) * (1 + 0.07 * grain)
	alb = np.where(joint[..., None], hex_rgb("#8f7b69"), alb)
	height = np.clip((edge - 0.003) / 0.003, 0, 1) * 0.004 + 0.0005 * grain[..., 0]
	return np.clip(alb, 0, 1), normal_from_height(height, m, 1.0)


def roof_membrane(px=512, tile=2.0):
	"""Flat-roof membrane with gravel speckle, 256 px per metre (it's out of reach)."""
	g = noise(px, px, 3, (8, 16, 32))[..., None]
	rng = np.random.default_rng(4)
	speck = (rng.random((px, px)) > 0.92)[..., None]
	alb = hex_rgb("#7d7570") * (1 + 0.08 * g)
	alb = np.where(speck, alb * (0.8 + 0.35 * rng.random((px, px, 1))), alb)
	return np.clip(alb, 0, 1), None


def stripes(colour_b, px=512, tile=0.6):
	"""Awning canvas: 300 mm stripes, cream and colour_b, with a fine weave."""
	m = tile / px
	y, x = np.mgrid[0:px, 0:px] * m
	stripe = (np.floor(x / 0.3) % 2 == 1)[..., None]
	alb = np.where(stripe, hex_rgb(colour_b), hex_rgb("#efe2cc"))
	weave = (np.sin(x / m * np.pi / 2) * np.sin(y / m * np.pi / 2))[..., None]
	alb = alb * (1 + 0.025 * weave + 0.03 * noise(px, px, 5, (8, 16))[..., None])
	return np.clip(alb, 0, 1), None


def stone(px=512, tile=1.0):
	"""Dressed stone for plinths, sills, lintels and cornices."""
	g = noise(px, px, 6, (4, 8, 16, 32, 64))[..., None]
	alb = hex_rgb("#9a958c") * (1 + 0.07 * g)
	return np.clip(alb, 0, 1), normal_from_height(0.0008 * g[..., 0], tile / px, 1.0)


def wood(px=512, tile=1.0):
	"""Wood with grain running along U, for furniture, doors and the interior floor."""
	rng = np.random.default_rng(7)
	streak = _value_noise(px, px, 64, rng)
	streak = np.repeat(streak[:, :1], px, axis=1) * 0.6 + 0.4 * _value_noise(px, px, 32, rng)
	g = noise(px, px, 8, (16, 32))
	alb = hex_rgb("#6e4b32") * (0.88 + 0.2 * streak[..., None] + 0.04 * g[..., None])
	return np.clip(alb, 0, 1), None
