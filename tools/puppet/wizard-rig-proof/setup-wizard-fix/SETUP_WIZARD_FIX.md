# nijigenerate Setup-Wizard Headless Fix — LIVE-TESTED

**Date:** 2026-10-07
**Worker:** Lane C (Wave 8)
**Status:** ✅ FIX VERIFIED by live headless run with screenshot proof.

## The fix

The setup wizard checks `hasDoneQuickSetup` (NOT `firstrun_complete` —
Wave-7 root-cause analysis, verified in source). Preseed it before launching:

```bash
export INOCHI_CONFIG_PATH=/tmp/niji-headless-config
mkdir -p "$INOCHI_CONFIG_PATH"
cat > "$INOCHI_CONFIG_PATH/settings.json" <<'EOF'
{"hasDoneQuickSetup": true, "firstrun_complete": true}
EOF
dbus-run-session -- xvfb-run -a /path/to/nijigenerate /path/to/model.inp
```

With `hasDoneQuickSetup=true`, the app skips the WelcomeWindow and
`incOpenProject(args[1])` opens the `.inp` directly from the CLI arg.
No xdotool needed.

**Source chain (verified in `/tmp/niji-src` @ 3d266c3):**
- `source/nijigenerate/windows/welcome.d:337`:
  `if (!incSettingsGet!bool("hasDoneQuickSetup", false)) step = 0;`
- `source/app.d:156,163`:
  `else if (incSettingsGet!bool("hasDoneQuickSetup", false) && args.length > 1) incOpenProject(args[1]);`
- `source/nijigenerate/core/path.d`: `INOCHI_CONFIG_PATH` env override;
  else `$HOME/.nijigenerate/settings.json` (legacy) or XDG.

## Live test (2026-10-07 ~18:18 UTC)

**Binary:** built from source (nijigenerate @ 3d266c3) with LDC 1.36.0.
Three local source patches were needed for the newer D frontend
(`auto ref` locals rejected by DMD 2.106+):
1. `nijilive/.../graph_builder.d:222`: `auto ref pass = resolvePass(hint);`
   → `addItemToPass(resolvePass(hint), zSort, builder);`
2. `nijigenerate/.../asyncderivedupdatedetails.d:99`:
   `ref const snapshot` → `const snapshot` (read-only, safe).
3. `nijigenerate/.../parameditor.d:110`: `auto ref pt` → `auto pt = &...`
   (pt is mutated; pointer preserves semantics).
Build deps: `dub add-local` for nijigenerate/nijilive/nijiui/nijiexpose/
i2d-imgui@0.8.0 (pinned c6a78f4a); `dub build --config=meta`, then
`dub build --compiler=ldc2 --build=release --config=linux-full`.
Binary: `~/workspace/nijibuild/nijigenerate/out/nijigenerate` (58MB).

**Test 1 — fix preseeded** (`INOCHI_CONFIG_PATH` with
`{"hasDoneQuickSetup": true}` + `StaticBattle.inp` arg, Xvfb + D-Bus):
→ **PASS.** Screenshot `nijigenerate_editor_gui-fixed.png` shows the
editor UI (File/Edit/View/Tools/Help, Edit Puppet tab) with the
StaticBattle puppet loaded in the viewport. **No wizard.**

**Test 2 — control** (empty `INOCHI_CONFIG_PATH`, same `.inp` arg):
→ Wizard appears as expected. Screenshot `nijigenerate_wizard_control.png`
shows the "NijiGenerate / Quick Setup" welcome window (Language, Color
Theme, UI Scale, Next button); the `.inp` is NOT loaded. This confirms
the test can detect the wizard and the fix is what skips it.

## Proof artifacts

- `setup-wizard-fix/nijigenerate_editor_gui-fixed.png` — editor open, no wizard, `.inp` loaded
- `setup-wizard-fix/nijigenerate_wizard_control.png` — wizard blocking (control)
- (Also copied to `ashes/proofs/nijigenerate_editor_gui-fixed.png`,
  superseding the Wave 3–6 `-blocked` screenshot.)

## Notes

- The app saves settings on exit; the preseed file must be valid JSON and
  the config dir writable. `~/.config/nijigenerate/settings.json` already
  carries `hasDoneQuickSetup:true` on this machine (seeded during testing).
- Headless requires Xvfb (OpenGL context); without it the app crashes with
  "No valid OpenGL context" (seen in earlier crashdumps).
- D-Bus session needed (`dbus-run-session`); without it there are
  `org.freedesktop.DBus.Error.AccessDenied` warnings but the app still runs.
