# Style sheet

The measured look of Meadowbrook, taken from the concept art (docs/concept/) and corrected to real-world sizes. Every
model and material follows this file; change the file first, then the assets.

**The bar:** a handcrafted model village from the builder's camera that still holds up at 1 m from the visitor's eye.

## What to keep from the concept art, and what not

Keep: warm late-afternoon light, soft shadows, muted earthy colours, bevelled soft-cornered shapes, strong roof
silhouettes, dense small detail (planters, window boxes, rooftop units), shopfronts with striped awnings and terraces.

Don't copy: the concept art's scale (people, doors and windows disagree from building to building), its signs (the
lettering is garbled), or its window counts (they change between views of the same building). Use the measurements
below instead.

## Palette

The six swatches from the style sheet image, sampled exactly. Materials below are built from these.

| Name | Hex | Used for |
| --- | --- | --- |
| Meadow | `#9fa055` | lit grass, young foliage |
| Moss | `#727759` | shaded foliage, hedges, sage paint |
| Lake | `#4c636d` | water, blue-grey paint, shutters |
| Rosewood | `#895352` → `#b7756a` | brick, terracotta, red awnings |
| Sand | `#c9a98a` | paving, warm render, wood |
| Linen | `#dbc7b2` | light render, trim, canvas |

Rules: no pure white (lightest is about `#efe6d6`), no pure black (darkest is about `#2b2a28`). Keep colours earthy:
HSV saturation at most 0.55 for surfaces (walls, roofs, ground, foliage, wood), at most 0.7 for accents (awnings,
terracotta, lane paint, flowers, autumn leaves). Only lit windows go above that.

## Materials

Albedo starting values, sRGB. Calibrate them in the side-by-side render (see "Checking an asset"), then update this table.

| Material | Albedo | Notes |
| --- | --- | --- |
| Red brick | `#9a5f4a` | running bond, bricks 215 × 65 mm with 10 mm mortar `#c9b9a5` |
| Cream render | `#e3d6bf` | plaster on houses and café upper storeys |
| Grey stone | `#9a958c` | plinths, sills, lintels, corner buildings |
| Painted siding | `#d9c7a3`, `#a7a49c`, `#8e9a7c` | 150 mm boards; cream, grey and sage |
| Slate roof | `#5e5a60` | 300 × 200 mm tiles |
| Terracotta roof | `#a8553a` | cottages only |
| Flat roof | `#7d7570` | membrane with gravel speckle |
| Window frame, dark | `#2f3a33` | on brick |
| Window frame, light | `#efe6d4` | on render and siding |
| Glass | `#2b2f33`, roughness 0.05 | warm interior glow `#ffb35c` behind it at dusk |
| Awning stripes | `#efe2cc` with `#4a4642`, `#b8463a`, `#c9a24a` or `#3f6b4f` | stripes 300 mm wide; one colour pair per shop |
| Plaza paving | `#c8ab92` | 400 × 400 mm slabs |
| Sidewalk | `#b9b2a6` | 1 × 1 m slabs, 150 mm curb `#a9a39a` |
| Asphalt | `#4a4a4c` | lane paint `#d8b04a`, crossings `#e6dfd2` |
| Grass | `#7f9a52` | |
| Foliage | `#6f8a3e`, `#8aa04c` | blossom `#e3a6b8`, autumn `#c98d40` |
| Wood | `#6e4b32` | furniture, benches, fences, doors |
| Metal | `#34383a` | lamp posts, café chairs, railings |
| Canvas | `#ecdcc4` | umbrellas, plain awnings |

**Texel density:** 512 px per metre for anything within 4 m of the ground (ground floors, terraces, props, paving),
256 px per metre above that. Tiling textures are made from Blender's procedural shaders and baked at that density, so
their colours start from this table.

## Measurements

All in metres. These matter most at eye level, where a wrong door height reads instantly.

### Buildings

| Element | Size |
| --- | --- |
| Storey, residential | 3.0 floor to floor |
| Storey, shop ground floor | 4.0 |
| Ground floor level | 0.15 above the ground outside |
| Plinth | a band 0.4 high at the foot of the wall, 0.05 proud; it stops at doors |
| Door, house | 1.0 × 2.1, recessed 0.15, step 0.15 |
| Door, shop | 1.0 × 2.4, glazed |
| Window, residential | 0.9 × 1.4, sill at 0.9 above the floor, recessed 0.12 |
| Window frame | 0.06 wide; glazing bars 0.03 |
| Sill and lintel | 0.06 proud; sill 0.05 thick, lintel 0.2 |
| Shopfront glazing | 2.6 high above a 0.5 stall riser |
| Fascia (sign band) | 0.6 high, above the shopfront |
| Awning | fixed under the fascia at 3.1, 1.8 deep, falls 20° to a lower edge at 2.5 |
| Pitched roof | 40° (houses), 50° (cottages), eaves overhang 0.4, verge 0.2 |
| Flat roof | parapet 0.8, cornice 0.3 high projecting 0.25 |
| Chimney | 0.6 × 0.9, 1.0 above the ridge |
| Dormer | 1.2 wide, set 0.6 back from the eaves |
| Corner bevel | 0.02 on every exposed edge |

### Street and props

| Element | Size |
| --- | --- |
| Sidewalk | 2.0 wide |
| Road, two lanes | 7.0 wide, curbs 0.15 high |
| Path | 2.0 wide |
| Street lamp | 4.0 high, lantern 0.35 |
| Bench | 1.8 × 0.5, seat 0.45 high |
| Café table | 0.7 across, 0.75 high |
| Café chair | seat 0.45, back 0.85 |
| Umbrella | 2.4 across, canopy edge at 2.2 |
| Planter | 1.2 × 0.5 × 0.5 |
| Street tree | 6–9 high, canopy 4–6 across |
| Person | 1.6–1.85 |

### Lots

A building is placed with its lot: yard, front path, hedges and planters. Lot sizes in 4 m tiles, width (along the
street) × depth, replacing the greybox footprints in scripts/town.gd once the models land. Building sizes are in
metres, also width × depth.

| Lot | Tiles | Building |
| --- | --- | --- |
| Cottage | 3 × 3 | 7 × 7, one storey plus attic |
| House | 3 × 4 | 8 × 9, two storeys plus attic |
| Family home | 4 × 4 | 11 × 9, two storeys, porch |
| Townhouse row | 4 × 3 | 15 × 9: three units 5 m wide, three storeys, 40° roof with dormers |
| Café | 3 × 3 | 9 × 7, two storeys, terrace 4 m deep along the front |

The front of every lot faces +Z at rotation 0.

## Detail density

The concept look comes from small detail. Every asset carries its own; players shouldn't have to place it.

- **Shops:** awning, fascia sign, two planters, a menu board; a terrace with two to four tables if the lot has room.
- **Houses:** a front path, a hedge or fence, one or two shrubs, window boxes on about a third of the windows.
- **Flat roofs:** one or two rooftop units, a roof hatch.
- **Pitched roofs:** a chimney, and a dormer on houses deeper than 8 m.
- **Streets:** a lamp every 16 m, a tree every 8 m, a planter or bench every 12 m in plazas (spacings fit the 4 m grid).

## Light

Golden hour is the default (time of day is still an open question, docs/plan.md question 5).

- **Sun:** about 28° above the horizon, colour `#ffd9a8`, soft shadows.
- **Sky fill:** cool, about `#9db4c8`, so shadows read blue against the warm sun.
- **Ambient occlusion:** strong in corners and under awnings.
- **Builder's camera only:** a slight tilt-shift blur at the top and bottom of the screen.

## Checking an asset

Before an asset enters the game, render it in Blender:

1. Four turnaround views, 90° apart.
2. One view from the builder's camera, orthographic and tilted 35°, at gameplay zoom.
3. Two eye-level views, 1.6 m high: one from 3 m away, one from 1 m away at the door.

Place each render beside the matching crop of the concept art, under the light above. An asset passes when its
silhouette and colour match the concept, and when the eye-level views have no flat or stretched surfaces.
