# Wave 7 — nijigenerate Setup-Wizard Headless Block: Status & Root Cause

**Date:** 2026-10-07  
**Worker:** Lane C (Wave 7)  
**Status:** ROOT CAUSE IDENTIFIED via source analysis; not yet tested (no binary available)

## Previous waves (Waves 3–6)

- Ran nijigenerate under Xvfb+D-Bus, screenshot-verified the editor launches.
- The first-run Quick Setup wizard could not be dismissed.
- Tried: `firstrun_complete=true` in settings, xdotool clicks/keys (no window manager, synthetic input doesn't register), CLI `.inp` argument (ignored).
- Proof: `ashes/proofs/nijigenerate_editor_gui-blocked.png`.

## Wave 7 root-cause analysis

Cloned `https://github.com/nijigenerate/nijigenerate` (2026-10-07) and grepped the D source.

**The wizard does NOT check `firstrun_complete`.** It checks `hasDoneQuickSetup`:

- `source/nijigenerate/windows/welcome.d:337`: `if (!incSettingsGet!bool("hasDoneQuickSetup", false)) step = 0;` — forces the wizard to step 0.
- `source/nijigenerate/windows/welcome.d:207,321`: sets `hasDoneQuickSetup=true` when the user completes/dismisses the wizard.
- `source/app.d:156,163`: `else if (incSettingsGet!bool("hasDoneQuickSetup", false) && args.length > 1) incOpenProject(args[1]);` — **only opens the `.inp` from CLI if `hasDoneQuickSetup` is true.** This is why "the CLI ignores a `.inp` argument" — the arg is only honored after setup.

**Previous waves set the wrong key.** `firstrun_complete` is a different flag (`source/nijigenerate/core/window.d:747` — controls Armed Parameters panel visibility, not the wizard).

## The fix (for a future worker WITH the binary)

Settings live in JSON at:
- Linux: `$XDG_CONFIG_HOME/.nijigenerate/settings.json` (fallback `~/.config/.nijigenerate/settings.json`)
- Override via env var: `INOCHI_CONFIG_PATH=/path/to/config` (`source/nijigenerate/core/path.d:22,78`)

**Preseed before launching:**

```bash
export INOCHI_CONFIG_PATH=/tmp/niji-headless-config
mkdir -p "$INOCHI_CONFIG_PATH"
cat > "$INOCHI_CONFIG_PATH/settings.json" <<'EOF'
{"hasDoneQuickSetup": true, "firstrun_complete": true}
EOF
xvfb-run -a ./nijigenerate /path/to/model.inp
```

With `hasDoneQuickSetup=true`, the app skips the WelcomeWindow and `incOpenProject(args[1])` opens the `.inp` directly. No xdotool needed.

## What was NOT tested

- No nijigenerate binary exists in the workspace (previous waves' binary is gone).
- No official Linux binary is published (README: "No official stable build provided"; Windows-only via FileCR/itch.io).
- Building from source requires DMD/LDC + dub + ~dozens of D dependencies (nijilive, nijiui, nijiexpose, i2d-imgui pinned to `c6a78f4a`). Not installed here; a full build was out of scope for this wave.
- The `INOCHI_CONFIG_PATH` + `hasDoneQuickSetup` recipe is derived from source reading, not from a live run. It should work, but a future worker must verify with a real binary.

## Recommended next steps

1. Get a binary: build from source on a machine with the D toolchain, or find a community Linux build.
2. Run the preseed recipe above under `xvfb-run`.
3. Screenshot-verify the `.inp` opens without the wizard.
4. If the wizard still appears, check `settings.json` wasn't overwritten (the app saves on exit; ensure the file is valid JSON and the app has write permission to the config dir).
