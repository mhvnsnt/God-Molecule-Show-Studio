# Wizard Gang / TRIPPEDD Show-Canon Knowledge Graph

Built 2026-10-10. A lightweight, JSON-backed canon graph for AI agents working on
the Wizard Gang and God Molecule shows — no database, no server, no heavy
dependencies (disk at 87%, this stays a few dozen KB).

## Files

- `graph.json` — the knowledge graph (nodes, edges, flagged contradictions)
- `kg.py` — the query interface
- `KNOWLEDGE-GRAPH.md` — this file

## Schema

### Nodes

```json
{
  "id": {
    "type": "show | character | person | episode | place | concept | role",
    "name": "Display name",
    "aliases": ["alt names"],
    "description": "Canon-grounded prose — no invention",
    "props": { "robe": "...", "voice_status": "...", ... },
    "sources": ["source file + date"]
  }
}
```

Types:
- **show** — a network property (Wizard Gang, TRIPPEDD, God Molecule, In the Bushes,
  The Bastard, Damn, Shit's Wild)
- **character** — a fictional character (the 9 wizards, the Narrator, Mars, Kevin)
- **person** — a real-world basis/voice reference (Lio Rush, Enzo Amore, …)
- **episode** — an episode or pilot (WG EP01–EP03, SHORT_01, …)
- **place** — a canon location (Hollows District, the pier)
- **concept** — recurring gags, laws, structures (voice law, Kiko-late gag, …)
- **role** — a performed role distinct from the character (the Narrator)

### Edges

```json
{ "from": "cipher", "to": "lio_rush", "rel": "based_on",
  "note": "Feral 2026 Blackheart persona specifically", "source": "…" }
```

Relationship types:
`based_on`, `voiced_by`, `member_of`, `secret_leader_of`, `public_face_of`,
`general_of`, `occasional_member_of`, `role_in`, `same_person_as`, `appears_in`,
`set_in`, `speaks_in`, `alter_ego_as`, `performed_as`, `has_voice_role`,
`segment_of`, `spun_from`, `in_universe`, `opens`, `mentioned_in`,
`emerges_from`, `has_trait`, `voice_style_of`.

Every edge and node carries its source. Anything the sources don't answer stays
open/TBD — the graph never invents canon.

## Query interface

```bash
python3 kg.py "who is Cipher"                          # full profile + relationships
python3 kg.py "what is the relationship between Static and Ashes"
python3 kg.py "who voices Sombra Negra"
python3 kg.py "who is Cipher based on"
python3 kg.py "robe color of Echo"
python3 kg.py "what episodes exist"
python3 kg.py "list characters"
python3 kg.py "search pier"
python3 kg.py contradictions                            # flagged contradictions / open questions
```

## Coverage (as of 2026-10-10)

**All 9 wizards** — Static, Cipher, Echo, Onyx, Theory, Sombra Negra, Kiko Tanaka,
Hollow, Ashes (Buffalo Bill) — with robe colors, council roles, voice statuses,
face/design rules, and likeness locks from the v1 model sheets (2026-10-10) and
the approved EP01 dialogue (2026-10-07).

**Real people behind the characters** — the 9 based-on relationships from
`~/memory/people/` pages: Lio Rush, Enzo Amore, Shotzi Blackheart, Onyx (consent
yes), Theory (consent yes), Damian Priest, Keiji Mutoh, Super Dragon, Bill $aber.

**Episodes** — WG EP01 "THE SUMMIT" (approved, 33 lines), EP02 (style fix in
progress), EP03 (voice direction), the 50s pilot SHORT_01, Season 1 (16 eps).

**God Molecule** — Mars (floating head, cobalt skin, forehead portal), Kevin
(emerges through Mars's forehead symbol), the four lands + Central Mountain.

**Concepts** — voice law, the Narrator rule, "you racist bastard!" gag (S1: 6,
one episode twice; S2: 8), Kiko-late gag, the war fund, the 5-of-9
street-crew overlap (alluded, never stated), the Ashes grin exception,
Hollows District + the pier.

**Sibling shows** — minimal nodes for In the Bushes, The Bastard, and
"Damn, Shit's Wild" (series status only; detail belongs to their own graphs).

## Flagged contradictions (also queryable via `contradictions`)

1. **c1** — `memory/people/damian-priest.md` line 17 says Sombra Negra is "an
   original character with no wrestler basis"; the rest of the page (and the
   owner's locked canon) confirms Damian Priest as the basis. Owner-confirmed
   basis wins; the line-17 note is a stale artifact to be edited or struck.
2. **c2** — Narrator rule tension: DIALOGUE.md says "no purple figure on screen,
   ever"; WIZARD-GANG.md says "until the owner says otherwise." Treat as
   voice-only until he explicitly approves a figure.
3. **c3** — Narrator voice status: DIALOGUE.md marks N1/N2 VO-PENDING; the
   people page records N1 approved PERFECT 2026-10-08. Likely a date issue —
   recheck `VOICE_STATUS.md` for the live state.
4. **c4** — Echo voice: model sheet says UNKNOWN vs. WIZARD-GANG.md's
   Shotzi Blackheart lock. Resolved: the lock is the likeness; the voice isn't
   built yet.
5. **c5** — Onyx robe "green (sometimes)": open whether an alternate robe exists.
   Owner decision required.
6. **c6** — Sombra Negra's council role: TBD. Never invented — stays open.
7. **c7** — Static teeth: checked, no conflict (normal teeth everywhere;
   sharp teeth are Ashes-only).

## Maintenance

- When new canon locks (new episodes, new characters, new voice verdicts):
  edit `graph.json` directly — add nodes/edges, bump `version`, update `updated`.
- Update `contradictions` when a flag resolves; keep the audit trail.
- Re-run the validation queries below after any edit.
