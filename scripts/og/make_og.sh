#!/bin/bash
# Render the social share cards (1200x630) into site/og-en.png and site/og-zh.png.
# Needs Google Chrome. Run from the repo root: bash scripts/og/make_og.sh
set -euo pipefail
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
CARD="file://$(pwd)/scripts/og/card.html"
for lang in en zh; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --window-size=1200,630 --virtual-time-budget=3000 \
    --screenshot="site/og-$lang.png" "$CARD#$lang" 2>/dev/null
  echo "site/og-$lang.png"
done
