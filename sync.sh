#!/usr/bin/env bash
# One-command sync: add all changes, commit with timestamp or custom message, and push.

set -e

cd "$(dirname "$0")"

if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing to sync — working tree is clean."
  exit 0
fi

TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
COMMIT_MSG="${1:-sync: $TIMESTAMP}"

git add -A
git commit -m "$COMMIT_MSG"
git push origin main

echo ""
echo "Synced successfully at $TIMESTAMP"