#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v marp >/dev/null 2>&1; then
  for deck in lecture_*.md; do
    marp "$deck" --html --allow-local-files -o "${deck%.md}.html"
  done
  echo "Built Marp HTML decks in slides/."
else
  echo "Marp CLI not found. Install with: npm install -g @marp-team/marp-cli"
  echo "The Markdown slide decks are still readable directly."
fi
