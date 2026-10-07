# RVC / Applio — voice-cloning path for the Wizard Gang cast (Wave 2 wiring)

Date: 2026-10-07. Repo: god-molecule (character/creative lane).

## Licenses (verified 2026-10-07 at upstream LICENSE files)
- **RVC** (`RVC-Project/Retrieval-based-Voice-Conversion-WebUI`): **MIT** © 2023 liujing04 — commercial-safe, the training path for tight likeness matches.
- **Applio** (`IAHispano/Applio`): **MIT** © 2026 AI Hispano — commercial-safe, the easy WebUI on-ramp. Recommended FIRST stop before raw RVC.

Both replace the rejected stock-Piper approximation and the non-commercial Coqui XTTS-v2 weights for based-on characters (owner law: AI voices must be TIGHT to the real people).

## Wiring status
- **Applio**: docs-path integration (Wave 2). The Applio distribution is a large download (WebUI + model weights); install on a workstation/GPU box, not this sandbox. Path: download the Applio release for the OS → launch WebUI → train or inference-convert with owner-consented reference audio.
- **RVC**: upstream repo shallow-cloned to `tools/voice/upstream/rvc/` (Wave 2). Training needs a GPU box; inference (voice conversion with a trained `.pth`) runs on CPU via the repo's `infer` CLI.

## Wizard-cast voice plan (owner-consented cloning only)
1. Static → Enzo Amore likeness (first proof — `voice-clone-work/` already holds Enzo refs + cb_weights).
2. Narrator → Bill $aber. 3. Cipher → Lio Rush's 2026 "Blackheart" (feral — zoned out, whisper-to-shriek, word-loops; owner lock 2026-10-07). 4. Echo → Shotzi Blackheart. 5. Hollow → Super Dragon. 6. Sombra Negra → Damian Priest. 7. Kiko → Keiji Mutoh / Great Muta.
- Theory (Black 20-year-old NY woman, exact voice TBD) and Onyx (voice TBD): NO cloning until the owner approves a voice target. A character with no acceptable matched voice stays silent — never a placeholder.

## Owner-consent rule
Clone ONLY voices the owner has approved targets for (the list above). Never clone a voice from unconsented audio. Reference clips live in `~/workspace/voice-clone-work/refs/`.

## Proof (Wave 2)
- `tools/voice/upstream/rvc/` — shallow clone present (HEAD 81eed5e); `LICENSE` reads MIT © 2023 liujing04; `configs/`, `infer/` CLI, training WebUI all present.
- `tools/animation/upstream/dragonbones-js/` — shallow clone present (HEAD 64b6c69); `LICENSE` reads MIT © 2012-2025 The DragonBones team; runtimes: Cocos, Egret, Hilo, Phaser, Pixi.
