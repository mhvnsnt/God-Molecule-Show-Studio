# PROJECT BIBLE — God Molecule

> The world the `god-molecule-scene-builder` skill directs inside. Canon sources of truth: `docs/GOD-MOLECULE-UNIFIED-BIBLE.md` (DRAFT) in this repo, with **Bible A as the #1 authority** until the owner blesses the unified bible — Bible A lives in `God-molecule-production-stage/src/components/ShowBible.tsx`. Also in-repo: `src/components/ShowBible.tsx`, `src/components/Cosmology.tsx`, `src/data.ts`. If anything here conflicts with those docs, the docs win — flag the mismatch, never propagate it. Facts the repo docs do not cover are marked **TBD** — never invented.

## SERIES

- **Logline:** God Molecule is an adult surrealist animated/AI-assisted anthology about Mars, a deadpan, overconfident, psychedelic consciousness whose mind contains entire worlds — a floating head whose forehead symbol is a portal, travelling realities that file under four lands, asking what reality and consciousness are, then immediately making a stupid joke.
- **Title:** EP1 — naming unresolved (see Episode Notes): Bible A blocks it as Scene 001 "The Void" / Scene 002 "The Door"; `src/data.ts` titles Episode 01 *"The Recursive Room"* (Scene 01 "The Awakening", Scene 02 "Tonnō Pass").
- **Visual style:** mutable per reality — cheap old video game, psychedelic children's program, abandoned mall, cosmic horror landscape, suburban backyard, microscopic world, fake documentary, dream, medical simulation, 3D game, crude 2D animation, found footage, live-action/AI-assisted footage, completely abstract universe. **Style may change; identity may not drift.** Mars's lock never changes with the style. Visual bible: character colors cobalt/electric blue + indigo; lighting Key, Fill, Rim, Practical, Volumetric, Supernatural/Molecular; materials organic (skin, teeth, gums, tongue, hair) + world (Gaussian radiance, molecular lattice, cosmic/quantum effects, transformation shaders); camera fourth-wall, intimate, observational, surreal, macro, cosmic; grades Base Show, Ep01 Void, Cosmic, Dream, Night, Comedy.
- **Creative references:** Osamu Sato / Eastern Mind (**Tonnō**), LSD: Dream Emulator, Xavier: Renegade Angel, Adult Swim / Off the Air / Robot Chicken–style anthology energy.
- **Aspect ratio:** TBD — no canon value in the repo docs.
- **Default scene length:** 15 seconds when no cut spec exists (production default from the method, not canon). Format: 24fps; characters on twos (12 drawings per second) for drama, on ones (24 drawings per second) for action peaks and scale moves, on threes only for labelled slow beats. Every movement gets a deliberate frame count (48f = slow/deliberate, 12f = quick).
- **Episode shape:** episode runtime/format length TBD (open gap in the unified bible). Inspirations run ~11 minutes (Off the Air) / 11–12 minutes (Xavier). Every episode runs the same machine: ritual open → koan thesis → forehead-portal arrival → one central question → escalation → anti-ending.
- **Season structure:** nine episodes = nine lives = nine soul-fragments of a shattered central figure, scattered across the four lands and exploited by each land's ruler. Finale reversal template: the devouring thing the audience feared all season was the cure.

## CHARACTERS

### Mars — LEAD, protagonist, narrator, prisoner, creator, idiot, god (+ observer, + audience)
- **Canonical asset:** `.trippedd_assets/mars_proxy.glb` (proxy); `tools/character/Marshead_Tripo_63779a1f.glb` (Tripo mesh, **NOT rigged** — rig it first, or use TRIPPEDD's `MARS_rigged.glb`). Identity lock: `MARS_CANONICAL` — photographs / scanned likeness outrank generation.
- **Likeness lock:** FLOATING HEAD ONLY — no body, arms, or legs. Cobalt / electric-blue skin — saturated cobalt, not generic blue; cyan interaction, dimensional shading, painterly texture, granular digital breakup. Indigo / violet dreads — dark enough to disappear into black space sometimes, violet/magenta/blue information, painterly texture; dreads lift like kelp when the forehead symbol reacts. Solid glowing white eyes — NOT realistic eyeballs, an intentional graphic element. The forehead symbol is a literal portal AND a living organ — it dilates, reacts, intrudes into scenes like a title card; it is never decoration. The underlying production asset is a complete head/neck/geometry model so the system can animate him properly — that geometry stays under the hood; on screen he is a head, nothing more.
- **Voice:** PLACEHOLDER — Mars's voice actor / voice reference is UNCAST (open gap). Pipeline is voice-first: write → voiceover → storyboards → animation; record Mars's voice before storyboards. The owner's own voice only — never a cloned voice. Never invent a voice.
- **Personality & speech style:** Nine traits — deadpan · overconfident · philosophical · stoner-ish · observant · casually arrogant · curious · emotionally strange · unpredictable. Native tongue: the Ice-Cream Koan — correct wisdom-*shape* (koan, paradox, aphorism), wrong content; he believes every word, never winks. Diction: misfired spiritual / self-help / pseudo-academic forms. Device: hear a phrase → elevate it → break it. Register: deadpan folktale — state cosmic facts like a shopkeeper states prices. Never explain the weirdness; narrate it as logistics. Conversations: two monologues colliding, not exchanges — nobody listens; rhythm battles replace dialogue. Running devices: one meaningless catchphrase-exclamation; one word or sound that always echoes in his presence; the forehead symbol intruding into scenes like a title card.
- **Animation priorities:** gaze, eye direction, facial expressions, micro-topology deformations (GNM teeth/tongue). Lip-sync and mouth aperture are anatomy + real audio timing when claimed — not stickers.

### Kevin — canonical, essential character
- **Character asset:** TBD — no Kevin visual design in the repo docs beyond "appears from behind/through the symbol on Mars's forehead after the world shifts" (EP1 entrance). Do not invent a design; build from whatever asset the owner hands you.
- **Likeness lock:** TBD (see above). Narrative role: his own parallel arcs and comedic pacing, running concurrently with Mars.
- **Voice:** PLACEHOLDER — no voice reference held. Voice-first order applies.
- **Personality & speech style:** The counter-rhythm — if Mars is the deadpan authority, Kevin is the sensory id: appetite, confusion, the dumb obvious question. Kevin says what Mars won't. Kevin is parallel chaos, never the sane foil (the format is the straight man). Kevin "re-rolls" the next reality at the death menu.

### NPCs / world-visitors — "Born with the words of duty"
- **Character-writing device (adopted):** every world-visitor or soul-fragment ships with a one-line moral thesis printed on them (e.g. "I fix what bites"). Instant characterization + instant plot generation.
- **Examples from the treatments (DRAFTS, not canon):** the barber — a wig wearing a smaller wig as a hat; duty line "I cut what grows." The waiter — a vulture in a bow tie; duty line "I serve who waits."

## LOCATIONS / REALITIES

### The Void — the ritual home
- **Views:** TBD — no saved location views in the repo docs. Canon description: absolute dark stillness; near-black space populated by tiny colored stars and cyan rim lights (`src/data.ts` Scene 01).
- **Mood & lighting:** Ep01 Void grade. Key, Fill, Rim, Practical, Volumetric, Supernatural/Molecular.
- **Canon:** Scene 001 — Mars floating in absolute dark stillness → looks left → looks right → looks directly at the camera → "Oh, hey." Fourth-wall interaction establishes the audience relationship.

### The Door — the forehead portal
- **Views:** TBD. Canon: reality reorganizes into Gaussian splats / molecular space; the symbol on Mars's forehead activates as a physical threshold; Kevin appears from behind the symbol / out of the door.
- **Mood & lighting:** the symbol dilates like a living organ; dreads lift; the head is a living island.

### The four lands + Central Mountain (reality taxonomy)
- **Life** = Wood · organic/techno-house textures · growth-duty
- **Time** = Fire · driving percussion · urgency-duty
- **Desire** = Metal · sharp synthetic textures · appetite-duty
- **Dreaming** = Water · fluid ambient textures · memory-duty
- **Central Mountain** = the trickster hub (Kevin's territory): barter-only, published-but-absurd exchange rates, no money, every trade has a catch.
- A reality isn't just themed; it has a locked elemental signature + musical palette. Mapping of the 14 realities below onto the four lands: TBD (future production work, not canon).

### The 14 realities (anthology schema — instances, expanding toward almost infinite worlds)
cheap old video game · psychedelic children's program · abandoned mall · cosmic horror landscape · suburban backyard · microscopic world · fake documentary · dream · medical simulation · 3D game · crude 2D animation · found footage · live-action/AI-assisted footage · completely abstract universe · …

### The cosmology scale stack (geography, not a ladder — episodes enter at any rung)
thoughts → memories → simulated realities → dimensions → universes → multiverses → galaxies → microscopic worlds → quantum-scale phenomena → abstract mathematical spaces. Open question: is Mars containing everything, or is something containing Mars? (Never answered on screen.)

### Preset world families (Gaussian splat theme — starting environments, not limits)
God Molecule / Fullerene C60 · DNA quantum double helix · superconducting torus lattice · cyberpunk splat alley · cosmic nebula splat void. Episode-specific worlds generate from the show cosmology. World pipeline: physical scene → radiance field → molecular/procedural layer → animation → cinematic render.

## PROPS

- **The forehead symbol:** part of Mars's canonical asset, not a separate prop — a literal portal and a living organ. States: dormant / dilating / open / intruding like a title card.
- **The death menu:** re-entry points eyes / nose / mouth / forehead; stays visible one beat too long (asset-reuse as comedy). Asset path: TBD.
- **The duty tablet / duty line:** a stone tablet or printed line carrying a life's mission (e.g. "YOU ARE THE MOON. YOUR DUTY: BE LOOKED AT."). Asset path: TBD.
- **Marshead Field Guide entries:** dry faux-encyclopedia entries (Likes/Dislikes) for realities, creatures, phenomena. Asset path: TBD.
- **The concept of food / the desert sandwich / the farm of Kevins:** one-off payoffs from the treatments — described inline in the scene, never given a standing prop tag unless the owner saves one.

## UNIVERSE LANGUAGES (one set, never flattened)

1. **PRIMARY — THE RITUAL OPEN.** Void → look left → look right → "Oh, hey." Locked; exactly one element varies per episode. Mission-parable cold opens may precede it.
2. **THE KOAN THESIS.** One Ice-Cream Koan names the episode's theme; one central question is posed in-world, never answered cleanly; then a stupid joke.
3. **THE FOUR LANDS + CENTRAL MOUNTAIN.** Element + music + soul-force locked per land.
4. **THE FOREHEAD DOOR.** Arrival through the portal; the symbol reacts like an organ first.
5. **DEATH AS A MENU.** Progression survives; Kevin re-rolls; refusing to die is the only true failure.
6. **REALITY TRANSITIONS.** Datamosh bridge / organ reaction / death-reel. The cut carries the story; never bridge with dialogue; continuous music.
7. **THE SCALE STACK.** Macro ↔ microcosm is geography; the camera zooms through it.
8. **NPC DUTY LINES.** One-line moral thesis printed on every visitor.
9. **MUSIC-FIRST ASSEMBLY.** Score before locking visuals; soundtrack as a standalone album, tracks debuting in-episode.
10. **DELIBERATE CHEAPNESS.** Real tools, stylized limits; if the audience can't tell the failure is intentional, it's a bug, not a style.
11. **THE HEAD REACTS.** The portal is an organ; approaching the head triggers physical reactions.
12. **THE GAUSSIAN SPLAT WORLD.** The environment is consciousness manifest; splat world + Blender geometry + molecular layer + rigged Mars.
13. **THE ANTI-ENDING.** Reset, death-as-transition, or the shrug. No clean lessons.
14. **THE FIELD GUIDE.** Faux-encyclopedia interstitials — hint system + comedy + lore, never a lore dump.

## EPISODE NOTES

- **EP1 staging (canon, Bible A):** Scene 001 "The Void" (look left → look right → camera → "Oh, hey."); Scene 002 "The Door" (void reorganizes into splats/molecular space; symbol activates; Kevin appears). Cold open + scene map pointers in the unified bible: `production/GOD_MOLECULE_EPISODE_01/COLD_OPEN.md`, `production/GOD_MOLECULE_EPISODE_01/SCENE_MAP.md` (verify these paths exist in the production repo — they are pointers from the bible, not confirmed files in this repo).
- **EP1 naming — UNRESOLVED:** `src/data.ts` (mock episode data) titles Episode 01 *"The Recursive Room"* — "Mars finds himself in a room that seems to exist entirely within his own thoughts" (Scene 01 "The Awakening", Scene 02 "Tonnō Pass" — "the reality degrades into a 640x480 quantized retro digital dream"; Shot 003 line: "Yeah. That happens sometimes."). Whether "The Recursive Room" is an alternate title, a different episode, or a superseded mock is unresolved per unified bible §17.1. A's blocking wins per the hierarchy.
- **Episode treatments (DRAFTS for owner review — NOT canon):** "HAIR" (Off the Air style, one-word theme), "THE CUSTOMER IS ALWAYS RIGHT" (Xavier style, solution-escalation), "THE NINTH LIFE" (Tong-Nou style, death-as-menu life arc). Plus three cold opens ("STATIC", "MORNING", "DUTY") and three transition sequences (datamosh bridge, organ reaction, death-reel) in `docs/research/wave2/GOD-MOLECULE-TREATMENTS.md`. Usable as scene-prompt raw material only after the owner approves them.
- **Central questions (KEEP-verdicted):** What is reality? What is consciousness? What is identity? What happens when the observer becomes part of what is being observed? Is Mars experiencing the universe, or is the universe experiencing Mars? — then a stupid joke.
- **Creative constitution (15 laws, KEEP in principle — per-law alignment against the owner's other show laws still pending):** 1. Mars's identity is immutable unless explicitly changed. 2. Canonical references outrank generated interpretations. 3. Generated media is subordinate to source identity. 4. Style may change; identity may not drift. 5. Imperfection may be intentional. 6. Technical failure is never automatically treated as style. 7. Every episode may establish its own visual reality. 8. Reality transitions are a storytelling mechanism. 9. Death may produce progression rather than reset. 10. Comedy and philosophy coexist. 11. Surrealism must have internal logic, even when the audience cannot see it. 12. The audience should be allowed to interpret. 13. Never explain a mystery merely because the system can. 14. Visual experimentation is encouraged. 15. Provenance and source assets must always be preserved. Plus Bible C: UNKNOWN is not PASS; AI is co-author, not replacement.
- **Production pipeline:** voice-first (write → voiceover → storyboards → animation); music-first assembly; commissioning model (theme + trust, not specs; per-reality buckets fill over time); dream-journal writer (defined role — writes the impossible as mundane, separate from the dialogue writer); guilt-free truncation (mixtape rule; expand the container, don't trim the bit). Production hierarchy: 1. Show Authority (storyboard, dialogue, canonical blocking). 2. AI Director. 3. Physical Authority (Blender meshes, splats, rendered pixels, provenance hashes).
- **Repo Animation Laws (apply to every animated piece):** consult the animation-research-library technique for the shot BEFORE touching a frame and cite it in the PR; edit the existing project in place; no rectangular crops ever (subject-mask-cut, verify edges on a checkerboard at 2x zoom); before/after proof frames on every visual change; never claim done without a rendered clip (mp4 in the PR + contact sheet); frame states explicit; owner's voice files get placed, not offloaded; mobile-editable. Numerical PASS + visual FAIL = FAIL.
- **Voice refs held:** 0 — Mars uncast, Kevin uncast. Voice tags in any scene prompt are PLACEHOLDERS until recorded. Voice-first: the recording is owed before storyboards.
- **Joke mechanics (house list — pick one per beat):** right slot, wrong content; maximum setup, minimum payoff; rhythm battles, not dialogue; the score does the joke; bank sincerity, spend desecration; scripture as logistics; authority sabotages itself; withheld agency; lore that lies; the corpse persists; format betrayal; the exhale ending.
- **A cut the owner confirmed good must NOT be extended.** New beats go in a NEW scene, later in the flow — never inserted between confirmed beats. Work forward.

## OPEN GAPS (sources silent — TBD, not invented)

- Mars's voice actor / voice reference (uncast; pipeline requires voice-first recording).
- Kevin's visual design beyond "appears through the forehead symbol."
- Episode runtime / format length; aspect ratio.
- Whether "The Recursive Room" material (cold-open drafts, Tonnō Pass) is current or superseded.
- The 15-law alignment pass against the owner's other show laws.
- Mapping of the 14 realities onto the four lands.
- Saved location-view paths and prop asset paths (none in the repo docs — placeholders until the owner saves them).
- "Observer/audience" wording for Mars's roles — owner-verdicted, exact wording still to be verified against the documented production conversation.

## AUTHORITY ORDER

1. **Bible A** — `God-molecule-production-stage/src/components/ShowBible.tsx` (immutable canon).
2. **B-KEEP** — Bible B items verdict KEEP by the owner (review doc, PR #84).
3. **Bible C** — comedy/style guidance (`GOD_MOLECULE_CANON.md`, subordinate to B).
4. **W2** — wave-2 research additions (all 18 owner-approved 2026-10-09).
5. **This bible + the skill** — working copies only; the docs above win on any conflict.
