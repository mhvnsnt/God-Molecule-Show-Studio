#!/bin/sh
# fetch-animlab.sh — fetch AnimLab Linux .deb + Android .apk from itch.io
# Usage: ./fetch-animlab.sh "<itch download-page URL>"
#   The download-page URL is $1 because its tokens expire in ~30 min —
#   NEVER hardcode a download link. Get a fresh one from the itch page:
#   set price $0.00 -> "No thanks, just take me to the downloads".
#   Requires: curl (or wget), sha256sum, grep/sed.
# Output: animlab_<version>_amd64.deb + animlab_<version>.apk in ./animlab-bin/
#   plus SHA-256 printed for each. Upload both to the repo Release named below.
# Release to upload to: AnimLab v0.2.26 (tag: animlab-v0.2.26)
#   — create it with: gh release create animlab-v0.2.26 --title "AnimLab v0.2.26" --notes "AnimLab v0.2.26 binaries (Linux .deb + Android .apk), fetched via tools/animlab/fetch-animlab.sh"
set -eu
URL="${1:-}"
if [ -z "$URL" ]; then
  echo "usage: $0 "<itch download-page URL>"" >&2
  echo "Get a fresh URL from the itch AnimLab page ($0 checkout, tokens expire in ~30 min)." >&2
  exit 1
fi
# Commented fallback: Arttista direct download URL (same author family of tools).
# Uncomment and use as $1 if the AnimLab page itself is unreachable:
#   https://arttista.itch.io/arttista/download/19179272
#   NOTE: that URL fetches Arttista, NOT AnimLab — it is a fallback fetch route
#   only if the AnimLab download page is down, and what it downloads must be
#   labelled Arttista, never AnimLab.
OUTDIR="animlab-bin"
mkdir -p "$OUTDIR"
echo "Fetching download page..."
PAGE="$OUTDIR/download-page.html"
curl -fsSL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" "$URL" -o "$PAGE"   || wget -q -U "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" "$URL" -O "$PAGE"
# Extract the Linux .deb and Android .apk links from the page.
DEB_URL=$(grep -oE 'https://[^"'"'"' ]+\.deb' "$PAGE" | grep -iv arm64 | head -n 1 || true)
APK_URL=$(grep -oE 'https://[^"'"'"' ]+\.apk' "$PAGE" | head -n 1 || true)
if [ -z "$DEB_URL" ]; then echo "ERROR: no Linux .deb link found on the page (token may have expired — fetch a fresh URL)." >&2; exit 1; fi
if [ -z "$APK_URL" ]; then echo "ERROR: no Android .apk link found on the page (token may have expired — fetch a fresh URL)." >&2; exit 1; fi
echo "Linux .deb: $DEB_URL"
echo "Android .apk: $APK_URL"
curl -fL -o "$OUTDIR/animlab_linux_amd64.deb" "$DEB_URL"
curl -fL -o "$OUTDIR/animlab_android.apk" "$APK_URL"
echo "--- sizes ---"
ls -l "$OUTDIR/animlab_linux_amd64.deb" "$OUTDIR/animlab_android.apk"
echo "--- sha256 ---"
sha256sum "$OUTDIR/animlab_linux_amd64.deb" "$OUTDIR/animlab_android.apk"
echo "--- expected sizes (v0.2.26, itch page 2026-11-20) ---"
echo "Linux .deb ~75 MB; Android .apk ~66 MB. If sizes are far off, the download is wrong — do not upload."
echo "Upload both files to repo Release: animlab-v0.2.26 (tag animlab-v0.2.26)."
echo "Done. Binaries are in $OUTDIR/ — NOT committed to the tree."
