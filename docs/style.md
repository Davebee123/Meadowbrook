# Style sheet

The look of Meadowbrook: a detailed, stylised miniature village, chunky and soft like a well-made toy. The target is
the designer's reference shop render (docs/concept/style-target.png, the corner shop with the green awning). The first
concept images (town-overview, style-sheet, pitch-board) still set the town's layout, density and mood, but not the
modelling style.

Every model and material follows this file; change the file first, then the assets.

## The look in one paragraph

Real-world scale, so the visitor's eye height of 1.6 m feels right, but every detail is thicker and softer than
reality: trims are chunky bands with rounded edges, frames are thick, bevels are big enough to catch a highlight from
the builder's camera. Surfaces are plain, clean colours with no grime, no brick-by-brick texture and no noise. Windows
glow warm with a glimpse of furnished interior. Plants are dense, rounded clusters of small leaf blobs in bright,
fresh greens, dotted with simple flowers. Light is bright and warm with soft shadows and gentle contact shading.

## Palette

sRGB albedo. Materials are flat colours with a roughness value; textures only where a flat colour can't carry the
surface.

| Material | Albedo | Roughness | Used for |
| --- | --- | --- | --- |
| Stucco | `#ece3d3` | 0.9 | walls |
| Trim, sand | `#d9c4a3` | 0.8 | belt courses, sills, surrounds, coping, plinths |
| Trim, tan | `#c4955f` | 0.7 | accent bands, fascias, steps |
| Frame | `#3b3f45` | 0.5 | window and door frames, lamp, railings |
| Door, sage | `#6f8f4a` | 0.5 | front doors, awnings, shutters (one accent per building) |
| Roof, slate | `#646b78` | 0.8 | pitched roofs |
| Roof, flat | `#d6d1c7` | 0.9 | flat roofs |
| Interior glow | `#ffc27a` | emissive | lit rooms behind glass |
| Interior wood | `#c98f55` | 0.7 | floors and furniture seen through windows |
| Glass | `#6f8796` | 0.05 | window glass (tinted, glossy) |
| Pavers | `#d9d3c8`, joints `#b8b0a3` | 0.85 | sidewalks, paths, lot edges |
| Asphalt | `#5b5d60`, lane paint `#efe3bd` | 0.9 | roads |
| Curb | `#cfc8bc` | 0.85 | curbs |
| Lawn | `#6e9a45` | 0.95 | grass |
| Foliage | `#3f7a2c`, `#5e9b3a`, `#86bf4f` | 0.8 | dark, mid and light leaf blobs |
| Flowers | white `#f6f1e6` with yellow `#e9c24a` centres, pink `#e7a3b6`, lavender `#a58ccf` | 0.7 | flower dots |
| Bark | `#7a5a40` | 0.9 | trunks |
| Wood, planters | `#b07a4a` | 0.75 | planters, benches, fences |
| Metal | `#a9adb0` | 0.45 | rooftop units, vents, mailboxes |

Rules: no pure white or black. Greens may be fresh and saturated; everything else stays warm and soft.

## Shapes and measurements

Metres. Real sizes for anything the visitor touches (doors, steps, furniture); exaggerated thickness for trims.

| Element | Size |
| --- | --- |
| Bevel, buildings | 0.05, three segments (rounded, catches light) |
| Bevel, small props | 0.02 |
| Storey | 3.0 floor to floor |
| Ground floor level | 0.3 above the ground, reached by one or two steps 0.15 high, 0.35 deep |
| Door | 1.0 × 2.2, frame 0.1 wide, set back 0.15 |
| Window | 1.0 × 1.4 (arched head allowed), frame 0.08 wide, glass set back 0.15, sill 0.9 above floor |
| Window surround | 0.12 wide, 0.04 proud; sill 0.1 high, 0.08 proud |
| Belt course | 0.25 high, 0.06 proud, between storeys |
| Plinth | 0.3 high, 0.04 proud |
| Pitched roof | 40°, eaves overhang 0.35, fascia 0.2 deep, verge 0.25 |
| Roof shingle course | 0.25 per course, each course 0.04 thick with a rounded lower edge |
| Flat roof | coping 0.3 wide × 0.25 high, rounded |
| Chimney | 0.7 × 0.7, cap 0.1 proud |
| Interior behind glass | a room box at least 0.6 deep, warm lit, with one or two furniture shapes |

## Plants

Plants are built from clusters of small rounded leaf blobs, not single leaves and not one smooth ball.

- **Blob size:** 0.08–0.15 for shrubs, 0.2–0.35 for tree crowns; three greens mixed, darker inside and below.
- **Shapes:** round bush, cone topiary, flower bed (low mound with dense flowers), hedge, round-crowned tree, conifer,
  blossom tree.
- **Flowers:** small five-petal discs, 0.04–0.06 across, in clusters, never spread evenly.
- **Trees:** 4–7 m, trunk visible below the crown, crown made of 4–7 clustered lobes.

## Light

Bright, warm daylight, the reference's soft studio look rather than a sunset.

- **Sun:** about 45° above the horizon, from the front left, colour `#fff1dc`, soft shadows.
- **Ambient:** sky fill, slightly cool, strong enough that shadows stay readable and coloured.
- **Contact shading:** screen-space ambient occlusion, moderate, so every object sits on the ground.
- **Windows:** interiors glow at all times of day, softly.
- **Builder's camera only:** later, a light tilt-shift; not part of the vertical slice.

## Budgets

Per asset, for the builder's camera with many instances.

| Asset | Triangles |
| --- | --- |
| House with its lot | up to 40 000 |
| Tree | up to 12 000 (Godot's automatic LODs cut this at builder zoom) |
| Shrub or flower bed | up to 3 000 |
| Prop | up to 1 500 |
| Street module | up to 2 000 |

## Checking an asset

Every asset passes the preview in Godot before it enters the library (docs/assets.md, "Previewing an asset"):
the builder's camera at gameplay zoom, a close builder view, eye level at 3 m and at 1 m, and a block of repeated
instances for performance. It passes when its silhouette, proportions and colours match this sheet and the reference,
nothing intersects or floats, and it stays inside its budget.
