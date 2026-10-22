#!/usr/bin/env bash
# Publish finished bench36 runs to the public dataset through the privacy gate (review 36c). Usage: [CARDS=cards.yaml] publish.sh RUN_DIR...
# 1. Copies each run (without checkpoints and claude_sessions/, which are never published) to cybertron/out/_pubsrc/<spec>/<run>
#    and replaces this machine's Claude Code session, container, account and organisation ids in every text file with
#    "<redacted>": the claude CLI's error streams quote the session id (36c 12:20, caught by the gate).
# 2. Stages from the copies with the same ids and the account email on the gate's denylist, audits the staging, and pushes only
#    if the audit is clean.
set -euo pipefail
cd "$(dirname "$0")/../../.."
IDS=("${CLAUDE_CODE_SESSION_ID:-}" "${CLAUDE_CODE_REMOTE_SESSION_ID:-}" "${CLAUDE_CODE_CONTAINER_ID:-}" "${CLAUDE_CODE_ACCOUNT_UUID:-}"
     "${CLAUDE_CODE_ORGANIZATION_UUID:-}" "${CLAUDE_CODE_USER_EMAIL:-}")
export CYBERTRON_PRIVATE_STRINGS="$(IFS=,; echo "${IDS[*]}")"
srcs=()
for r in "$@"; do
  r="${r%/}"; spec="$(basename "$(dirname "$r")")"; name="$(basename "$r")"
  dst="cybertron/out/_pubsrc/$spec/$name"
  rm -rf "$dst"; mkdir -p "$dst"
  python3 -c "import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2], dirs_exist_ok=True, ignore=shutil.ignore_patterns('checkpoints', 'claude_sessions', '*.pkl'))" "$r" "$dst"
  for v in "${IDS[@]}"; do
    [ ${#v} -ge 6 ] || continue
    grep -rlF --null "$v" "$dst" | xargs -0 -r sed -i "s/$(printf '%s' "$v" | sed 's/[.[\*^$/]/\\&/g')/<redacted>/g" || true
  done
  srcs+=("$dst")
done
stage="cybertron/out/_publish/bench36_$(date -u +%Y%m%dT%H%M%S)"
python -m cybertron publish "${srcs[@]}" --staging "$stage" --tags bench36,takeover --allow-dirty ${CARDS:+--card $CARDS}
python -m cybertron publish --audit "$stage"
python -m cybertron publish "${srcs[@]}" --staging "${stage}_push" --tags bench36,takeover --allow-dirty ${CARDS:+--card $CARDS} --push \
  --message "bench36 (review 36b first batch): $(for r in "${srcs[@]}"; do basename "$r"; done | tr '\n' ' ')"
