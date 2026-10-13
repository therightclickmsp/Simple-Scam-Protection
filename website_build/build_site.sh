#!/usr/bin/env bash
# Rebuilds the static website in ../static_site (rules from the Windows app + compiled CSS) and checks it.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 website_build/export_rules.py
TAILWIND="${TAILWIND:-frontend/node_modules/.bin/tailwindcss}"
"$TAILWIND" -c website_build/tailwind.config.js -i website_build/input.css -o static_site/assets/site.css --minify
python3 website_build/parity_test.py
echo "Static site ready in static_site/ - upload everything inside that folder to your web host."
