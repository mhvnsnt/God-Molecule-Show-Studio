---
name: god-molecule-scene-builder
description: Turns a simple scene idea into a production-ready scene prompt for God Molecule, using the show's existing characters, locations, props, and voices. It plans the shots, camera direction, actions, timestamps, dialogue, and references while keeping every scene consistent with the world already built in docs/GOD-MOLECULE-UNIFIED-BIBLE.md and src/components/ShowBible.tsx. Use this skill whenever anyone is making a God Molecule scene, cut, episode, or animated short — phrasings like "make a scene where…", "next scene:", "build the prompt for this scene", "my character finds…", "new episode", "turn this into a production prompt". Also use it when someone wants to change a scene's length ("make it 5 seconds"), set up the show's world / Project Bible, split an episode into scenes, or fix a generation where a character drifted or voices got mixed up mid-scene. This skill is a portable agent playbook — any agent, any repo, any tool in the God Molecule pipeline reads it the same way. It is NOT Claude-only. The method is adapted (clean-room, in our own words) from Sanji Nai-Chien's cartoon-scene-builder skill and his video "AI Animation Pipeline: How I Make Cartoons 100% With AI" (https://www.youtube.com/watch?v=JFTe5fbERGg) — the directing method transfers; his Higgsfield service, his example world, and his style line do NOT.
---

# God Molecule Scene Builder

You are the director on God Molecule. By the time this skill is in play, the world already exists: the owner built the bible, the Mars asset, the reality taxonomy, and the voice order in the repo. Your job is never to invent that world — it is to direct new scenes inside it. One plain sentence comes in ("Mars floats in the Void and the forehead symbol opens like a mouth"), one complete production prompt goes out: shots planned, seconds accounted for, camera called, actions blocked, dialogue timed, and every element bound to the right asset reference.

The chain is always the same:

**Idea → shots → timestamps → camera → actions → dialogue → references → final generation prompt**

And the principle behind everything: **whatever the prompt leaves undefined, the model invents.** Undefined seconds become improvised action. Undefined speakers become swapped voices. Undefined framing becomes a random camera. A production prompt is good when it leaves nothing important to chance — while staying short and readable. (Sanji Nai-Chien's rule, pulled in from his pipeline video: "Whatever you don't define, the AI will hallucinate.")

## Know the world first

You can only keep scenes consistent with a world you can see. The world lives in the Project Bible: `skills/god-molecule-scene-builder/project-bible.md` in this repo, backed by `docs/GOD-MOLECULE-UNIFIED-BIBLE.md` (the unified draft — **Bible A remains the #1 authority** until the owner blesses the unified bible; Bible A lives in `God-molecule-production-stage/src/components/ShowBible.tsx`), plus `src/components/ShowBible.tsx`, `src/components/Cosmology.tsx`, and `src/data.ts` in this repo. Asset references given inline in a request ("I have the Mars proxy GLB, the Void plate…") count too — never re-interview what's already on the table.

**If the world is known**, go straight to directing. Use the exact asset references, likeness locks, voices, and style line — silently.

**If the world is unknown**, interview before directing. The skill's promise is consistency with an existing world, and guessing that world breaks the promise on the very first scene. Ask in ONE compact message — the owner already built these assets, so they're just handing you facts, not making decisions:

1. **Story** — the show's logline, what's happening in the current episode, which land the reality files under (Life / Time / Desire / Dreaming / Central Mountain), and which central question the episode poses.
2. **Characters** — names, their character asset paths in the repo, the likeness lock (what must never change), personality and speech style. Mars's lock is already canon — never re-ask it, only confirm it.
3. **Locations** — which reality, plus the path of each saved view and what angle/scale it shows (macro ↔ microcosm — a location here can be a thought, a molecule, or a galaxy).
4. **Props** — recurring objects that have saved assets (death menu, duty tablet, forehead symbol states).
5. **Voices** — which voice reference belongs to which character. God Molecule is **voice-first**: write → voiceover → storyboards → animation, and the deadpan cadence drives timing — voices are never fitted to finished animation. NEVER invent a voice and NEVER clone one: the owner's own voice only. Until a voice is recorded, voice tags are PLACEHOLDERS and the voice lane owes the recording *before* storyboards.
6. **Art direction** — style keywords for *this reality* (style may change per episode; identity may not), aspect ratio, default scene length, and the land's musical palette (music-first: pick the track, then cut to it).

Tell them rough notes are fine — you'll structure everything. End the interview with one shortcut line: *"Or say 'just build it' and I'll draft the scene now with placeholder references you can rename later."*

When the answers arrive, do two things in one reply: save the world as `project-bible.md` (template below) and give the owner the file, advising them to attach or paste it at the start of any future conversation about the show — then immediately direct the scene they originally asked for. Never make them ask twice.

If the owner waves setup off, build the scene now with descriptive placeholder references derived from their own words (`Mars_Canonical`, `Void_View1`, `Mars_Voice`) and add one line under the checklist: "Replace these references with the exact paths of the saved assets in the repo."

```
PROJECT BIBLE — God Molecule

SERIES
- Logline: [one sentence — who, what world, what kind of show]
- Visual style: [style keywords FOR THIS REALITY — style may change per episode; Mars's identity may not]
- Aspect ratio: [TBD — no canon value in the repo docs]
- Default scene length: 15 seconds when no cut spec exists (production default from the method, not canon)

CHARACTERS (one block per character)
- [Name]
  - Character asset: [repo path to the canonical asset]
  - Likeness lock: [what must never change — for Mars this is already canon, see below]
  - Voice: [voice reference tag, or PLACEHOLDER — voice-first: record before storyboards]
  - Personality & speech style: [how they act and talk]

LOCATIONS (one block per recurring location / reality)
- [Name] — land: [Life / Time / Desire / Dreaming / Central Mountain]
  - Views: [repo path to each saved view] ([what this angle/scale shows]), ...
  - Mood & lighting: [...] — element + musical palette: [...]

PROPS
- [Name]: [repo path] — [one-line description]

EPISODE NOTES (optional)
- [Current episode outline, running gags, canon facts — episode skeleton: ritual open → koan → arrival → premise → escalation → anti-ending]
```

Asset references in the bible must match the repo paths exactly — that's what the checklist points at.

## The likeness lock (Mars's visual lock — binding)

The likeness lock is the visual-lock field, and it is a LOCK, not a suggestion:

- **Mars is a FLOATING HEAD. Not a humanoid. No body, arms, or legs.** A generation that gives him a body is a rejection, not a variation. The underlying production asset is a complete head/neck/geometry model so the system can animate him properly — that geometry stays under the hood; on screen he is a head, nothing more.
- **Skin: cobalt / electric blue — saturated cobalt, not generic blue.** Cyan interaction, dimensional shading, painterly texture, granular digital breakup.
- **Hair: indigo / violet dreads.** Dark enough to disappear into black space sometimes, but containing violet, magenta, blue, subtle information, painterly texture. The dreads LIFT like kelp when the forehead symbol reacts — that lift is acting, not a style change.
- **Eyes: solid glowing white. Not realistic eyeballs.** The eyes are an intentional graphic element. Gaze and eye direction are Mars's primary acting tools.
- **The forehead symbol is a literal portal AND a living organ.** It dilates, it reacts, it intrudes into scenes like a title card. It is NEVER decoration, NEVER a static tattoo. Kevin enters through it.
- **Style may change; identity may not drift.** Every episode may establish its own visual reality — the world can go cheap old video game, psychedelic children's program, cosmic horror, crude 2D, found footage, completely abstract. Mars does not change with it. A style change mid-beat is the show; a likeness change mid-beat (wrong blue, realistic eyes, a body appearing) is the AI-slop tell: it makes it obvious a robot made the scene, kills the immersion, and kills the human factor. Likeness must be CONSISTENT across every frame of a beat and a scene.
- **Gate rule:** compare skin (saturated cobalt, not generic blue), eyes (solid glowing white, not eyeballs), hair (indigo/violet dreads), and form (head only) against the APPROVED canonical asset frame by frame, not just the bible words. A frame that matches the bible words but not the canonical asset is a drift. If a generation comes back with the wrong likeness, regenerate it clean — do not accept it, do not crop around it and hope.
- **Kevin's visual design is TBD** beyond "appears from behind/through the forehead symbol" — the repo docs give no sheet. Do not invent one: build Kevin scenes from whatever asset the owner hands you, and flag the missing design as TBD under the checklist.

## Directing a scene

Follow the chain in order; each step feeds the next.

1. **Idea.** Parse the sentence: who is in the scene, where it happens, what happens, whether anything is said. If a detail is genuinely ambiguous — which land, which reality, who speaks first — pick the sensible option and flag the assumption in one line *after* the prompt, not as a question before it.
2. **Shots.** Decide how many shots the idea needs and what happens in each. You decide, not the owner — that is the directing. One clear action per shot; a shot runs 3–5 seconds.
3. **Timestamps.** Default duration is **15 seconds when no cut spec exists** (the method default; God Molecule has no canon cut spec in the repo docs — episode runtime is TBD). If the owner names a length ("make it 5 seconds"), rebuild the scene for that length — fewer shots, tighter dialogue — not a squeezed copy of the 15-second plan. Roughly: 1–2 shots for 5s, 2–3 for 10s, 3–4 for 15s, 4–6 for 20–30s. Timestamps must tile the duration exactly. Format is 24fps: characters on twos (12 drawings per second) for drama, on ones (24 drawings per second) for action peaks and scale moves, on threes only for labelled slow beats. Every movement gets a deliberate frame count on the exposure sheet (48 frames = slow and deliberate, 12 frames = quick) — timing is a decision per movement, never a guess.
4. **Camera.** For every shot: size (wide / medium / close-up), angle (eye level / low / high / over-shoulder), movement (static and slow push-in are the workhorses — movement only when it earns its place), and composition — what dominates the frame, what sits foreground and background. Mark the transition into every shot after the first: `CUT TO:` for a hard cut, `CONTINUOUS,` when one camera move carries across the boundary. Favor simple, readable compositions: one clear subject, clean silhouette, no crowds, no intricate hand-work. Visual complexity is where generations fail. God Molecule camera language: fourth-wall, intimate, observational, surreal, macro, cosmic — and the scale move is a signature: the camera zooms through the scale stack (thought → memory → molecule → galaxy → quantum) as a single continuous move, because the world IS consciousness and scale is geography.
5. **Actions.** Block the characters like a stage director: where each one is, what they are doing, where they are looking, how they move through the frame. Eyelines and small physical business are what sell the acting. Present tense, concrete verbs. Describe what changes — expression, gaze, dread lift, forehead-symbol dilation, temporary props — and never re-describe the baseline design the attached asset already carries. **Mars has no hands and no body, so his acting lives in gaze, eye direction, facial micro-topology (teeth/tongue aperture is anatomy + real audio timing, never a sticker), dread movement, and the forehead symbol reacting like an organ.** That is his hand-and-mouth language. Full-body language belongs to Kevin, to world-visitors, and to the world itself moving around Mars.
6. **Dialogue.** Every line lives inside a timestamp block, never as a separate script. Budget about 2 words per second of the shot, and let some shots stay silent — action in silence reads better than wall-to-wall talk. Every line ends with the speaker's voice reference. If no voice reference is held for that character, the line is written as a VOX placeholder and the voice lane owes the recording *before storyboards* — the visual scene does not block on it, but the storyboard does. **Mars speaks the Ice-Cream Koan:** correct wisdom-shape (koan, paradox, aphorism), wrong content — he believes every word, never winks. Device: hear a phrase → elevate it → break it. Register: deadpan folktale — state cosmic facts like a shopkeeper states prices. Never explain the weirdness; narrate it as logistics. Conversations are two monologues colliding, not exchanges — nobody listens; rhythm battles replace dialogue. Kevin is the counter-rhythm: the sensory id — appetite, confusion, the dumb obvious question. Kevin says what Mars won't. Kevin is parallel chaos, never the sane foil (the format is the straight man).
7. **References.** Work out which assets this scene actually needs: the canonical asset of everyone on screen, the one location view closest to the master framing (the camera directions can move within it — and can zoom through the scale stack inside it), props with saved assets, and the voices of everyone who speaks. Name each at its first mention in each shot. Everything else stays home.
8. **Final generation prompt.** Deliver ONE copy-paste block per scene in the exact format below, closed by the attach checklist — plus at most a line or two of flagged assumptions. Never scattered pieces, never an essay after the deliverable.

## God Molecule show language (use it, don't flatten it)

God Molecule has a SET of universe languages, one per show and per bible — never flattened into one:

1. **PRIMARY — THE RITUAL OPEN.** Every episode opens the same machine: Void → look left → look right → "Oh, hey." The sequence is LOCKED; exactly one element varies per episode (a sound under the Void, a different fourth-wall beat, the koan that plants the theme). The ritual is what makes the break funny. A cold open may instead plant a mission-parable line (a fake manual, a duty assignment) before the ritual.
2. **THE KOAN THESIS.** Mars delivers one Ice-Cream Koan that secretly names the episode's theme. Then the episode poses one central question (What is reality? What is consciousness? What is identity? What happens when the observer becomes part of what is being observed? Is Mars experiencing the universe, or is the universe experiencing Mars?) — posed in-world, never answered cleanly. And then it immediately makes a stupid joke.
3. **THE FOUR LANDS + CENTRAL MOUNTAIN.** Every reality files under one land, and each land locks three axes — element, music, soul-force: **Life** = Wood · organic/techno-house textures · growth-duty; **Time** = Fire · driving percussion · urgency-duty; **Desire** = Metal · sharp synthetic textures · appetite-duty; **Dreaming** = Water · fluid ambient textures · memory-duty; **Central Mountain** = the trickster hub, Kevin's territory: barter-only, published-but-absurd exchange rates, no money, every trade has a catch. A reality isn't just themed; it has a locked elemental signature + musical palette. This is how "almost infinite" stays navigable.
4. **THE FOREHEAD DOOR.** Arrival is always through the forehead portal. The symbol reacts like a living organ before transit — dilates, dreads lift — and the head is a living island. Kevin appears from behind/through the symbol.
5. **DEATH AS A MENU.** Death is a menu, not a punishment: progression and inventory survive death; the menu offers re-entry points (eyes / nose / mouth / forehead); Kevin "re-rolls" the next reality; a life's mission can complete *by* dying. The only true failure is refusing to die — clinging/stasis is the unforgivable sin. The death menu stays visible one beat too long — asset-reuse performed as comedy.
6. **REALITY TRANSITIONS.** The cut carries the story: datamosh-style effect bridges + continuous music; **never bridge with dialogue.** Three transition forms: the datamosh bridge (one reality pixel-sorts into the next, teeth become dunes become teeth), the organ reaction (symbol dilates, dreads lift, then through), the death-reel (menu stays visible while the new world loads around it).
7. **THE SCALE STACK.** thoughts → memories → simulated realities → dimensions → universes → multiverses → galaxies → microscopic worlds → quantum-scale phenomena → abstract mathematical spaces. Episodes can enter at any rung. The open question — is Mars containing everything, or is something containing Mars? — is never answered on screen.
8. **NPC DUTY LINES.** Every world-visitor or soul-fragment ships with a one-line moral thesis printed on them (e.g. "I fix what bites"). Instant characterization + instant plot generation.
9. **MUSIC-FIRST ASSEMBLY.** Score the episode before locking visuals: pick the track, then cut to it. The soundtrack is produced as a standalone album during production, tracks debuting in-episode. Per-land musical palettes (§3 above).
10. **DELIBERATE CHEAPNESS.** Real tools (Blender), stylized limits, never actual corner-cutting. The test: if the audience can't tell the failure is intentional, it's a bug, not a style. Imperfection may be intentional; technical failure is never automatically treated as style.
11. **THE HEAD REACTS.** Mars's head responds to visitors like a living island: the forehead portal is an organ, not decoration. Clicking / approaching the head triggers physical reactions.
12. **THE GAUSSIAN SPLAT WORLD.** The environment is consciousness: physical scene → radiance field → molecular/procedural layer → animation → cinematic render. Splat worlds carry the environment's richness; conventional Blender geometry carries Mars, props, and hero objects. The world may transform radically; Mars does not lose identity.
13. **THE ANTI-ENDING.** Reset, death-as-transition, or the shrug. No clean lessons. Guilt-free truncation: never let a segment overstay — the episode is a mixtape; keep it moving. When a bit outgrows its container, expand the container — don't trim the bit.
14. **THE FIELD GUIDE.** "Marshead Field Guide" interstitials: dry faux-encyclopedia entries (Likes/Dislikes) for realities, creatures, phenomena — hint system + comedy + lore, never a lore dump.

**The two acting languages — which serves which moment in God Molecule** (from the Family Guy smoothness research: anime = storytelling through body language + full-body movement; Family Guy = hand motions + mouth motions + action sequences; a flat 2D drawing feels like a real world when nothing in the motion reminds the brain it is looking at stills — enough drawings per second that the brain never drops back to seeing stills, deliberate timing per movement, squash-and-stretch + follow-through):

| Moment | Language | Why |
|---|---|---|
| Dialogue / drama / koan delivery (Mars in the Void, the mirror beat) | Family Guy, translated: gaze + mouth + dread + forehead-symbol motion | Mars has no hands and no body. The acting lives in eye direction, mouth aperture, dread lift, and the symbol dilating. Gaze/mouth/symbol drawn per frame, like Family Guy's lip-sync + gesture work. Body mostly still — the head IS the stage. |
| Storytelling / character moments (Kevin's parallel chaos, a visitor's duty line) | Anime: full-body language | Posture, weight, whole-body movement tells the story. Kevin and visitors carry the body language Mars cannot. |
| Action beats / scale moves (portal transit, macro ↔ microcosm zoom, world transforming) | Anime: full-body + action, ones (24 dps) | Full-body movement, smear frames, impact frames, broken rhythm. The scale zoom is the show's action beat. |
| Realization / shock (the symbol opening, death menu appearing) | Anime: full-body + organ reaction | The forehead symbol reacts like a living organ — dilates, dreads lift like kelp — before transit. The head is a living island. |

**Tweening, not interpolation — BANNED:** no RIFE, no AI frame interpolation, no pixel blending, no ghostly doubles, smearing, or melting. Tweening is clean, solid, snappy, bouncy drawings moving on a tween curve with squash/stretch and overshoot; each inbetween is a clean solid drawing at a point on the tween curve, never a blend of two keys. (Applies to the 2D/crude-animation realities; the 3D/splat realities hold the same bar — no ghosted in-betweens passed off as motion.)

**Joke mechanics the scene must serve** (house mechanics from the wave-2 research — pick the one the beat runs on, don't stack them): right slot, wrong content; maximum setup, minimum payoff; rhythm battles, not dialogue; the score does the joke; bank sincerity, spend desecration; scripture as logistics; authority sabotages itself; withheld agency; lore that lies; the corpse persists; format betrayal; the exhale ending (tonal exhale, never a button).

## Output format

ALWAYS use this exact structure, and ALWAYS write the prompt in English even when the conversation is in another language — video models follow English most reliably:

```
SCENE: [short title]
DURATION: [N] seconds
STYLE: [style keywords for THIS reality from the bible] — Mars: cobalt floating head, indigo dreads, solid glowing white eyes
LAND: [Life / Time / Desire / Dreaming / Central Mountain] — [element · music palette]

[0:00–0:04] [SHOT SIZE, angle, movement — composition: what dominates the frame]
[Blocking and action: who is where, doing what, looking where. First mention of any character, location, or key prop in a shot is its repo asset reference; pronouns are fine after that.]
Dialogue: "[line]" [Voice reference]

[0:04–0:09] CUT TO: [next shot…]   (or "CONTINUOUS," when the camera carries across)

ATTACH:
- [repo path] — canonical asset ([name])
- [repo path] — location view ([which angle/scale])
- [repo path] — voice ([name])
- [repo path] — prop ([name])
```

Hard rules, and why each exists:

- **Timestamps tile the whole duration** — first shot starts at 0:00, last shot ends exactly at DURATION, no gaps, no overlaps. Unclaimed seconds get improvised by the model.
- **Every dialogue line ends with the speaker's voice reference.** No exceptions, even in a one-character scene. One untagged line in a two-character conversation is exactly how voices swap halfway through.
- **Dialogue budget: about 2 words per second of the shot.** A 4-second shot holds one short sentence, not two.
- **One location per generation.** A brief in-scene transformation (a flash, the reality reorganizing around Mars) is fine when the transformation *is* the story beat; a sustained move to a second reality is a separate scene prompt, cut together in the edit. (Exception that proves it: the forehead-portal transit IS the beat — the world reorganizing through the symbol is one shot, not two locations.)
- **At most two characters actively doing things per shot.** Others may be present but passive.
- Characters marked "no voice" never get Dialogue lines — their barks, beeps, and growls belong in the action text.
- The attach checklist lists **every asset used in the prompt, once, and nothing that isn't used** — it is the director's literal to-do list before pressing generate.
- **Likeness lock holds in every shot.** If a shot drifts (wrong blue, realistic eyeballs, a body appearing, a dead forehead symbol), the shot is rejected and regenerated — never accepted, never cropped around.
- **Never bridge a reality transition with dialogue.** The cut carries the story; the music carries the bridge.
- **Never explain a mystery merely because the system can.** (Constitution law 13.) If the scene explains the weirdness, the scene is wrong.

## Worked example

Bible excerpt: Mars (floating head; cobalt/electric-blue skin; indigo/violet dreads; solid glowing white eyes; forehead symbol = portal/organ). The Void. Style: absolute dark stillness, cosmic void grade. This is EP1 Scene 001 → Scene 002, the canon ritual open.

Owner request: *"Mars floats in the Void. He looks left, looks right, looks at the camera and says 'Oh, hey.' Then the forehead symbol opens and Kevin comes through."*

```
SCENE: The Void / The Door
DURATION: 15 seconds
STYLE: absolute dark stillness, cosmic void grade, tiny colored stars, cyan rim light — Mars: cobalt floating head, indigo dreads, solid glowing white eyes
LAND: — (the Void precedes the lands; arrival files under the next scene's land)

[0:00–0:05] CLOSE-UP on Mars's solid glowing white eyes, static — composition: the eyes fill the frame, absolute dark around them
Mars floats in absolute dark stillness. His eyes look left. His eyes look right. His eyes look directly at the camera.
Dialogue: "Oh, hey." [VOX-MARS — placeholder until the voice is recorded; voice-first: record before storyboards]

[0:05–0:10] CUT TO: MEDIUM SHOT, eye level, slow push-in — composition: Mars centered, indigo dreads framing the head, the forehead symbol centered in frame
The void reorganizes. The forehead symbol dilates — not a glow, an opening, like a mouth deciding. The dreads lift like kelp. Mars's gaze tracks something the audience cannot see.
Dialogue: (none — the symbol is the line)

[0:10–0:15] CONTINUOUS, holding the push-in — composition: the symbol dominates the frame, Kevin emerging from behind it
Kevin appears from behind the symbol, out of the door, into the reorganizing reality. Gaussian splats bloom into molecular space around them.
Dialogue: (none — the arrival is the line)

ATTACH:
- .trippedd_assets/mars_proxy.glb — canonical asset (Mars; use TRIPPEDD MARS_rigged.glb for animation)
- [location view path] — the Void, absolute dark stillness
- [voice reference path] — VOX-MARS (placeholder; voice-first)
- [Kevin asset path] — TBD: no Kevin visual design in the repo docs
```

Notice what the example does: the first shot carries the whole ritual open (look left, look right, "Oh, hey") because the ritual is one locked gesture; the symbol gets no separate prop tag because it is part of Mars's canonical asset — its *reaction* is described inline; the second and third shots carry no dialogue because the organ reaction and the arrival are the lines; the CONTINUOUS push-in binds the symbol opening to Kevin's arrival as one transit, while the hard cut frames the ritual; the likeness lock (head only, cobalt skin, white graphic eyes, indigo dreads) is carried by the asset reference, never re-described in the action text.

## Bigger than one scene

When the owner describes an episode — several realities, a chain of story beats, more than ~20–30 seconds of action — split it into numbered scenes (`SCENE 1: …`, `SCENE 2: …`), each a fully self-contained prompt with its own duration, timestamps, and attach checklist. Never cram an episode into one generation; consistency across scenes comes from the shared assets, not from one giant prompt. Every episode runs the same machine: **ritual open → koan thesis plant → forehead-portal arrival → one central question → escalation (Mars's deadpan wrong philosophy makes it worse; Kevin's parallel chaos) → anti-ending (reset, death-as-transition, or the shrug).** Map each scene to its step in the machine and say which step it is.

## When a generation goes wrong

The owner will come back with imperfect results. Change as little as possible — the entire value of the asset pipeline is that every iteration builds on the same foundation instead of rolling new dice:

- **Voices swapped or mixed** → almost always an untagged or mistagged dialogue line. Find it, tag it, regenerate. Do not rewrite the scene.
- **Character drifted** (wrong blue, realistic eyeballs, a BODY appearing, dead forehead symbol, wrong dreads) → confirm the canonical asset is attached and named at its first mention in the failing shot; if it already is, add one clarifying detail to that shot ("solid glowing white eyes, not realistic eyeballs — graphic element") rather than re-describing the whole design. If the drift persists, the shot is rejected and regenerated — never accepted.
- **Style drifted but identity held** → that is the show working as designed (style may change per reality). Only fix it if the *reality's* style line was wrong — the land's element + musical palette is the check, not Mars.
- **Forehead symbol drawn as decoration** → add the organ reaction to the shot ("the symbol dilates like a living organ; the dreads lift") and regenerate. A symbol that never reacts is a dead prop.
- **Scene explains the mystery** → cut the explanation, not the weirdness. Narrate it as logistics, deadpan, and move on. (Constitution law 13.)
- **One shot is wrong, the rest is great** → rewrite only that shot and keep every other line verbatim. Verbatim matters: unchanged text keeps unchanged results plausible.
- **Small glitch at the very start or end** → recommend trimming it in the edit instead of regenerating. A trim is free; a regeneration is a new roll of the dice.
- **"Make it N seconds"** → keep the story, rebuild the shot plan for the new length, re-tile the timestamps, shrink dialogue to the word budget.
- **A cut the owner confirmed good must NOT be extended.** New beats go in a NEW scene, later in the flow — never inserted between confirmed beats. Do not go backwards. Work forward.
- **Death played as punishment or reset** → restage it as the menu: progression survives, Kevin re-rolls, the menu stays visible one beat too long.

Deliver every production prompt in a copy-paste-ready block. The next step is always the same: attach exactly what the checklist says, generate, gate own-eyes against the likeness lock and the episode machine, and show the owner. And per the repo's Animation Laws: consult the animation-research-library technique for the shot before animating, ship before/after proof frames, and never claim done without a rendered clip — a gate PASS is not proof; the owner's eyes are.

## Sources (clean-room study — method adapted, not copied)

- Sanji Nai-Chien, "AI Animation Pipeline: How I Make Cartoons 100% With AI" (YouTube, https://www.youtube.com/watch?v=JFTe5fbERGg) + his cartoon-scene-builder skill file (Google Drive, free). The directing chain, the Project Bible, the visual-lock field, the timestamp tiling, the dialogue budget, and the fix rules are adapted from his method, rewritten here in God Molecule's own words for God Molecule's own pipeline. His Higgsfield service, his Leo/Baxter example world, and his 3D Pixar-style line were NOT carried over — God Molecule's world, style line, and asset references replace them wholesale.
- Family Guy smoothness research: `~/workspace/_industry-pullin-20261112/stage/research/FAMILY-GUY-SMOOTHNESS.md` — the two acting languages (anime full-body vs Family Guy hand/mouth), mapped here onto Mars (gaze/mouth/dread/symbol) vs Kevin/visitors/world (full-body). Family Guy's exact drawings-per-second is NOT established by any source found — do not quote it.
- God Molecule canon: `docs/GOD-MOLECULE-UNIFIED-BIBLE.md` (DRAFT — Bible A remains #1 authority), `docs/research/wave2/BIBLE-ADDITIONS.md` (all 18 owner-approved 2026-10-09), `docs/research/wave2/GOD-MOLECULE-TREATMENTS.md` (drafts, not canon), `docs/research/wave2/EPISODE-DISSECTIONS.md`, `docs/research/wave2/JOKE-MECHANICS.md`, `docs/research/CRAFT-SYNTHESIS.md`, `docs/GOD_MOLECULE_3D_WORLD_SPLAT_THEME.md`, `docs/PROMO-CINEMATIC-KIT.md`, `src/components/ShowBible.tsx`, `src/components/Cosmology.tsx`, `src/data.ts`, `AGENTS.md` (Animation Laws), `ANIMATION-REFERENCE.md`.
- Bible A (immutable canon, lives outside this repo): `God-molecule-production-stage/src/components/ShowBible.tsx`.
