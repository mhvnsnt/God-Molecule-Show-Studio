# Wave 9 — nijigenerate Setup-Wizard Headless Fix: RE-VERIFIED

**Date:** 2026-10-07
**Worker:** Lane C (Wave 9)
**Status:** ✅ FIX RE-CONFIRMED by live headless run with screenshot proof
(new rig, new run — same binary as Wave 8).

Wave 8 built nijigenerate from source (nijigenerate @ 3d266c3, LDC 1.36.0)
and live-tested the `hasDoneQuickSetup` preseed fix; see
`setup-wizard-fix/SETUP_WIZARD_FIX.md`. This wave re-ran the same test with
the same binary (`~/workspace/nijibuild/nijigenerate/out/nijigenerate`,
58MB) against a NEW rig (`sombra-battle/SombraBattle.inp`), plus a control
run.

## Test 1 — fix preseeded (2026-10-07 ~19:35 UTC)

```
export INOCHI_CONFIG_PATH=/tmp/niji-w9-config
printf '{"hasDoneQuickSetup": true, "firstrun_complete": true}' \
  > "$INOCHI_CONFIG_PATH/settings.json"
dbus-run-session -- xvfb-run -a -s "-screen 0 1280x800x24" \
  /home/hatch/workspace/nijibuild/nijigenerate/out/nijigenerate \
  /home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/sombra-battle/SombraBattle.inp
```

**Result:** editor launched, NO Quick Setup wizard. Notification bar reads
`…/sombra-battle/SombraBattle.inp opened successfully.` The Sombra puppet
renders in the viewport.
Proof: `nijigenerate_wizard_wave9_test1.png`.

## Test 2 — control, no preseed (2026-10-07 ~19:36 UTC)

Same command with `INOCHI_CONFIG_PATH=/tmp/niji-w9-config-control`
containing only `{"firstrun_complete": true}` (the WRONG key, per the Wave-7
root-cause analysis).

**Result:** the Quick Setup wizard APPEARS (Language / Color Theme /
UI Scale, "Next" button); the `.inp` argument is ignored — exactly the
Waves 3–6 headless block.
Proof: `nijigenerate_wizard_wave9_control.png`.

## Conclusion

The `hasDoneQuickSetup` preseed is the necessary and sufficient condition:
set it → wizard skipped AND the CLI `.inp` arg is honored (`app.d:156,163`
`incOpenProject`); omit it → wizard blocks and the arg is dropped. The
`firstrun_complete` key alone does nothing for the wizard. Reproducible
across two waves, two rigs, one binary.
