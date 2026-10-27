# Plan and open questions

## Build order

1. **Greybox street (done, first pass).** Place buildings and props on the grid, paint paths, then press Tab and walk
   the result in first person. Save and load. No art. This proves the core promise, building a place and then being
   in it, before any asset work starts.
2. **One finished café, at both distances.** Model the café in Blender properly and look at it from the builder's
   camera and from the terrace at eye level. This settles the level-of-detail question below.
3. **The café moment.** Walk up, order, sit at a terrace table, and the camera settles into a view of the street.
4. **Pedestrians.** Residents walk from homes along paths to the café and the park.
5. **The rest of the first playable milestone** (design.md §8): three houses, a townhouse, landscaping, terrain polish.

## Open questions

These need a decision before the work they block.

1. **What does the miniature look become at eye level?** From above, the model-village charm comes from the high camera,
   warm light and dense detail. At street level, low-detail textures and toy proportions show. Either first person
   keeps a stylised miniature feel (shallow depth of field, a slightly toy-like scale) or every asset is made to hold
   up at both distances, which roughly doubles art cost. *Blocks: step 2.*
2. **What does street level give back to the builder?** Sitting in the café is lovely once. To come back, the street
   should reflect design decisions: the café is busy because it's beside the park; a path feels alive because it links
   homes to shops. *Blocks: step 4.*
3. **One rule for the economy.** Suggested: homes bring residents, residents walk the paths, shops earn from the foot
   traffic that passes them. That makes pedestrians the economy, and links the two scales. *Blocks: step 5.*
4. **Grid buildings and freeform roads.** Buildings need frontage on a road or path. Snapping grid footprints to curved
   roads, and pedestrian navigation over organic paths, is the hardest system in the milestone. The greybox uses grid
   paths only; freeform roads deserve their own prototype.
5. **Time of day and seasons.** The concept art shows day and night and the UI shows "Spring, Year 2"; the design
   doesn't mention either. Give them a purpose or cut them.
6. **Why money at all?** Tiny Glade and Townscaper sold on building with no economy. Write down what money adds that a
   milestone-based unlock can't.

## Concept art caveats

The concept images are AI-generated mood references. They show far more unique props per screen than a small team can
model, their camera isn't strictly orthographic, and they have generation tells ("Street Furitnure", a garbled school
sign, inconsistent scale between houses and people). Turn them into a measured style sheet (roof pitches, window grid,
palette values, light angle, prop density per tile) before modelling.
