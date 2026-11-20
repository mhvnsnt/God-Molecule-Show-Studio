#!/usr/bin/env bash
# fetch-verify.sh — pull all 10 Harmony + free-stack tools from the two
# verified releases and check size + SHA-256.
#
# Releases (mhvnsnt/dream-girl):
#   harmony-equivalents-20261120  (id 452975939) — Synfig, Glaxnimate, Enve, Wick
#   production-stack-free-20261120 (id 452720539) — AniCraft, Pencil2D, Rigby2D,
#                                                    Olive, Kdenlive, Douga
# Binaries land in tools/free-stack/bin/ (next to this script).
# Already-downloaded binaries whose size + SHA-256 verify are NOT re-downloaded.
# Any mismatch fails loudly — never silently keep a bad binary.
#
# Usage:
#   bash tools/free-stack/fetch-verify.sh            # fetch + verify all 10
#   bash tools/free-stack/fetch-verify.sh --verify   # verify only, no downloads
# Requires: gh (logged in), sha256sum, stat. No purchases, no accounts, no card.
# GPU-dependent runs (Rigby2D EGL, Kdenlive OpenGL) go via the GPU route:
# Kaggle GPU / Colab / Lightning AI / Oracle (coordinator owns the routing).
set -euo pipefail

REPO="mhvnsnt/dream-girl"
REL_HARMONY="harmony-equivalents-20261120"
REL_FREESTACK="production-stack-free-20261120"
BIN_DIR="$(cd "$(dirname "$0")/bin" && pwd)"
mkdir -p "$BIN_DIR"

VERIFY_ONLY=0
if [ "${1:-}" = "--verify" ]; then VERIFY_ONLY=1; fi

# name | release | size (bytes) | sha256 | gh pattern
TOOLS=(
  "SynfigStudio-1.5.5-linux64.appimage|$REL_HARMONY|115539968|b85aabc26f690a0c150d2143c656c17f358b73abbedf8d01007f15a7a95740e9|SynfigStudio-1.5.5-linux64.appimage"
  "glaxnimate-x86_64.AppImage|$REL_HARMONY|182682816|e0f39cf67b79e80cdbbe8b3d858cab8a7b142e1c17f5944eb09af55fbc4a6347|glaxnimate-x86_64.AppImage"
  "enve.AppImage|$REL_HARMONY|150658760|00b7081f0dfb8545c6eee31034407305cf63c630a002bd391fa1504eab01b1c0|enve.AppImage"
  "Wick.Editor-1.19.0.AppImage|$REL_HARMONY|216087317|92ff24c6f162e0144108d6dd47bf5f6d6ca6972d405c21b73c6da3a7d35f059b|Wick.Editor-1.19.0.AppImage"
  "anicraft-0.2.1-linux-x86_64.AppImage|$REL_FREESTACK|19024376|352456384d1e82f373d836dcbcd9f1473b1603c5c9c7b185d763218470091b31|anicraft-0.2.1-linux-x86_64.AppImage"
  "pencil2d-linux-amd64-v0.7.2.AppImage|$REL_FREESTACK|60471800|4034b036258b6a13d4540911ebce085f31ee18a9dacf438845ac71998d42ff91|pencil2d-linux-amd64-v0.7.2.AppImage"
  "Rigby2D_0.5.1_amd64.AppImage|$REL_FREESTACK|96979448|27afa7de71a43e2fe45f27e605176a62b9a559db4b7f5f00f3a105870bdbd6ee|Rigby2D_0.5.1_amd64.AppImage"
  "Olive-8ac191ce-Linux-x86_64.AppImage|$REL_FREESTACK|154107880|30a6c0d18dfb4ff77addd06984348656fd69d153cfa913eb3cde56a60aa14160|Olive-8ac191ce-Linux-x86_64.AppImage"
  "kdenlive-26.08.3-x86_64.AppImage|$REL_FREESTACK|214346232|2c8322edfc86605e4c98a78a019310d9b4fc46bb8e94e6fe313dc7dd987e7671|kdenlive-26.08.3-x86_64.AppImage"
  "douga-windows.zip|$REL_FREESTACK|3766009|bf3bd41c5593736caf4b7d74ebcf4c00c52766691c3596f3d3c7b34a9ea0b774|*douga-windows.zip"
)

fail=0
verify_one() {
  local file="$1" expect_size="$2" expect_sha="$3"
  if [ ! -f "$file" ]; then echo "MISSING: $file"; return 1; fi
  local size sha
  size="$(stat -c%s "$file")"
  sha="$(sha256sum "$file" | awk '{print $1}')"
  if [ "$size" != "$expect_size" ]; then
    echo "FAIL size: $file got $size want $expect_size"; return 1
  fi
  if [ "$sha" != "$expect_sha" ]; then
    echo "FAIL sha256: $file got $sha want $expect_sha"; return 1
  fi
  echo "OK: $(basename "$file") ($size B, sha256 match)"
  return 0
}

for entry in "${TOOLS[@]}"; do
  IFS='|' read -r name release size sha pattern <<< "$entry"
  # Douga's release asset carries a browser-download timestamp prefix;
  # resolve whatever file we already have for it.
  target="$BIN_DIR/$name"
  if [ "$name" = "douga-windows.zip" ]; then
    found="$(ls "$BIN_DIR"/*douga-windows.zip 2>/dev/null | head -n 1 || true)"
    [ -n "${found:-}" ] && target="$found"
  fi
  if verify_one "$target" "$size" "$sha" 2>/dev/null; then
    echo "  cached + verified — skipping download: $name"
    continue
  fi
  if [ "$VERIFY_ONLY" = "1" ]; then
    echo "FAIL: $name not present/verified (verify-only mode)"
    fail=1; continue
  fi
  echo "Fetching $name from $release ..."
  rm -f "$target"
  gh release download "$release" --repo "$REPO" --pattern "$pattern" --dir "$BIN_DIR" --clobber
  if [ "$name" = "douga-windows.zip" ]; then
    target="$(ls "$BIN_DIR"/*douga-windows.zip | head -n 1)"
  fi
  if ! verify_one "$target" "$size" "$sha"; then
    echo "FAIL: $name failed verification after download — see above"
    fail=1; continue
  fi
done

# AppImages must be executable; the zip stays as-is (Windows-only tool).
chmod +x "$BIN_DIR"/*.AppImage 2>/dev/null || true

if [ "$fail" != "0" ]; then
  echo "fetch-verify: FAILURES — see lines above" >&2
  exit 1
fi
echo "fetch-verify: all 10 tools verified in $BIN_DIR"
