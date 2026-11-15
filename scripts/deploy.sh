#!/bin/bash
# Validate, build and deploy the site to Cloudflare Pages.
# Needs: python3 + pyyaml, and wrangler logged in (or CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID set).
# SITE_URL controls canonical links and share images; switch it once the custom domain is live.
set -euo pipefail
SITE_URL="${SITE_URL:-https://agentrealtaskbench.pages.dev}"
python3 scripts/validate.py --check
python3 scripts/validate_data.py
python3 scripts/build_site.py --base-url "$SITE_URL"
python3 scripts/check_links.py
npx -y wrangler@4 pages deploy dist --project-name agentrealtaskbench --branch main \
  --commit-hash "$(git rev-parse HEAD)" --commit-dirty="$([ -n "$(git status --porcelain)" ] && echo true || echo false)"
