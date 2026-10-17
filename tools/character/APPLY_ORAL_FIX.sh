#!/usr/bin/env bash
# Apply Grok oral protrusion fix into a local clone of TRIPPEDD-Production-studios-
# Usage:
#   ./APPLY_ORAL_FIX.sh /path/to/TRIPPEDD-Production-studios-
# Or from repo root after extracting the tarball next to this script:
#   ./APPLY_ORAL_FIX.sh .
set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/TRIPPEDD-oral-fix"

if [[ ! -d "$ROOT/.git" ]]; then
  echo "FAIL: $ROOT is not a git repo root"
  exit 1
fi
if [[ ! -f "$BUNDLE_DIR/tools/character/build_mars_oral_bridge.py" ]]; then
  echo "FAIL: bundle missing at $BUNDLE_DIR"
  exit 1
fi

mkdir -p "$ROOT/tools/character" "$ROOT/production_conversations"
cp -f "$BUNDLE_DIR/tools/character/build_mars_oral_bridge.py" "$ROOT/tools/character/"
cp -f "$BUNDLE_DIR/tools/character/survey_oral_aperture.py" "$ROOT/tools/character/"
cp -f "$BUNDLE_DIR/production_conversations/2026-09-11-oral-protrusion-gate.md" "$ROOT/production_conversations/"

cd "$ROOT"
git add \
  tools/character/build_mars_oral_bridge.py \
  tools/character/survey_oral_aperture.py \
  production_conversations/2026-09-11-oral-protrusion-gate.md

git status
echo ""
echo "Ready to commit. Run:"
echo "  git commit -m 'Oral placement fix: recess behind lip plane, inward solidify, protrusion fail-closed gate + aperture survey'"
echo "  git push origin main"
