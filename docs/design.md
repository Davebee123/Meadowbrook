# Meadowbrook: game design document

- **Genre:** cozy community builder, creative sandbox, life sim
- **Perspective:** isometric macro view, plus first-person exploration
- **Engine:** Godot 4
- **Art style:** detailed, stylised 3D miniature village
- **Target experience:** relaxed, creative, personal and social

Concept art: [town overview](concept/town-overview.webp), [style sheet](concept/style-sheet.webp),
[pitch board](concept/pitch-board.webp). These are AI-generated mood references, not production targets.

## 1. Game vision

Create a cozy community-building game where players design their own mixed-use residential development, watch it come
alive, and then step inside the world they created.

Players build homes, apartments, shops, cafés, parks, pedestrian streets and public spaces. Unlike traditional city
builders, the experience goes beyond managing a map: players can enter their community in first person, order a coffee,
sit outside, and enjoy the neighbourhood they designed.

The game combines the creative freedom of a building sandbox, the satisfying progression of a light tycoon, and the
personal immersion of a cozy life sim.

**Core promise:** Build a place of your own. Bring it to life. Go live in it.

## 2. Design pillars

1. **Creative freedom first.** Building and decorating should feel expressive, not like completing chores.
   Experimentation should be easy and mistakes inexpensive.
2. **A living miniature world.** Detailed buildings, landscaping, pedestrians and warm lighting create a handcrafted
   model-village look.
3. **Macro and micro gameplay.** Players can design an entire neighbourhood, then explore it at street level.
4. **Meaningful but lightweight progression.** Money supports expansion and development without turning the game into
   a spreadsheet.
5. **Personal ownership and social discovery.** Players take pride in their own creations and can invite others to
   experience them.

## 3. Core gameplay loop

1. **Design:** lay out roads, pedestrian paths, lots, homes, shops and public spaces.
2. **Develop:** construct residential and commercial buildings and expand into more land.
3. **Bring to life:** residents move in, pedestrians visit shops, and public spaces become active.
4. **Earn and expand:** generate income, buy land, construct new buildings and unlock more options.
5. **Experience:** switch to first person to explore, visit businesses, sit in public spaces and appreciate the
   community.
6. **Share:** invite friends to visit, discover other towns and collect inspiration.

The loop should support both short creative sessions and long-term community development.

## 4. The two scales of play

### Macro: community builder

The primary mode uses an angled orthographic camera.

- Place and rotate buildings on a grid.
- Draw roads and pedestrian paths with flexible placement tools.
- Landscape freely with trees, flowers, fences, benches and other props.
- Customise building materials and architectural details.
- Expand the community as resources and progression allow.
- Select, move, replace and remove objects with minimal friction.

Buildings use defined grid footprints, while roads and landscaping support more organic layouts.

### Micro: first-person visitor

Players can enter their own community and experience it at human scale.

- Walk along streets, paths and plazas.
- Enter selected businesses, beginning with a café.
- Order a coffee, sit at outdoor tables and watch the neighbourhood.
- Use benches, visit parks, browse storefronts and discover small environmental details.
- Meet residents and other players.

The micro experience is about atmosphere, exploration and appreciation, not survival mechanics or elaborate life
simulation.

**Design rule:** first-person activities should reward curiosity and create memorable moments without becoming a
second, chore-heavy game.

## 5. Progression and economy

A creative-first approach with a lightweight, meaningful economy.

### Money

Money is the ability to develop more of the community.

- Residential buildings provide rent or sale proceeds and attract residents.
- Commercial buildings earn income from local demand and visitors.
- Construction, land, infrastructure and business upgrades cost money.
- Expansion creates new opportunities and supports more ambitious developments.

Economic relationships should be understandable without detailed financial optimisation.

### Unlocks

New possibilities come from community milestones, development achievements and exploration: larger residential
buildings, new architectural styles, more commercial categories and new district types.

### Creative freedom

- Basic building and landscaping tools are available early.
- Decorations are not a currency and never need to be farmed.
- Moving buildings and experimenting with layouts is cheap or free.
- Financial setbacks slow expansion; they never destroy a player's progress.

A dedicated Creative Mode may remove economic limits entirely, with the same tools and world.

## 6. Multiplayer and social features

Multiplayer starts with visiting, not co-building. Players keep ownership and creative control of their own
communities.

- Visit friends' towns and explore together.
- See other players walking through the community.
- Sit together at cafés and public spaces.
- Leave postcards, notes or small gifts.
- Discover towns through their architecture, parks, storefronts and landmarks.
- Possibly seasonal events and visitor books.

Collaborative editing and shared district ownership are out of scope for the first prototype. Multiplayer should add
to the pride of individual creation, not dilute it.

## 7. Visual direction and asset production

### Art direction

A detailed miniature model village rendered in real-time 3D.

- Warm, slightly muted colours and inviting architecture.
- Distinctive roofs, windows, doors, awnings and storefronts.
- Rounded but believable landscaping and carefully composed public spaces.
- Soft lighting, restrained ambient occlusion and readable silhouettes.
- Consistent scale and materials across all assets.

The target is a handcrafted miniature world, not generic low-poly graphics or photorealism.

### Asset pipeline

- **Blender:** reusable, measured 3D models and modular components.
- **Godot 4:** rendering, placement, simulation, UI and exploration.
- **AI image generation:** concepts and visual references only, never unverified production geometry.
- **GLB exports:** approved models and materials move into Godot as GLB.

### Quality standards

Every production asset is checked for:

- correct dimensions, proportions and grid footprint;
- symmetry and alignment where intended;
- geometry integrity, normals and surface intersections;
- consistent materials, scale and lighting;
- its look from several angles and at real gameplay zoom;
- visual consistency in a shared neighbourhood scene.

Automated validation and standard turnaround renders should catch defects before assets enter the game.

## 8. First playable milestone

A small, polished neighbourhood rather than a large simulation.

### Required features

- An orthographic camera and attractive miniature terrain.
- Grid-based building placement, rotation, selection and removal.
- Flexible road and path placement.
- Three distinct houses, one townhouse and one café.
- Trees, bushes, benches, streetlights and basic landscaping.
- Simple pedestrian movement.
- A first-person exploration prototype with at least one satisfying café interaction.
- Save and load for community layouts.

### Success criteria

A player can start with an empty plot, build an attractive little neighbourhood, bring it to life, explore it at street
level, and save the result.

The prototype should set the visual quality bar and prove that both building and inhabiting the world are enjoyable
before large-scale content production begins.

## 9. Out of scope for the first prototype

- Complex economic simulation and detailed business accounting.
- Large-scale city infrastructure and traffic simulation.
- Deep resident needs, survival systems or elaborate life simulation.
- Multiplayer co-building and shared ownership.
- Large online persistent worlds.
- Procedural generation of unlimited building designs.
- Extensive interiors or fully simulated businesses.

Consider these only after the core creative and exploration experiences are proven.

## 10. Guiding principle

The player is creating a place they are proud to live in and share.

The economy provides structure, progression adds new possibilities, and multiplayer adds social value. None of them
should undermine the basic pleasure of designing a beautiful community and spending time in it.

**Build a small world that feels wonderful before building a large one.**
