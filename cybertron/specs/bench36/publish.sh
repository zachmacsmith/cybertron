#!/usr/bin/env bash
# Publish finished bench36 runs to the public dataset through the privacy gate (review 36c). Usage: publish.sh RUN_DIR [RUN_DIR...]
# Adds this machine's Claude Code account, organisation, session and container ids and the account email to the gate's denylist,
# stages, audits the staging, and pushes only if the audit is clean. claude_sessions/ and checkpoints are never published (NEVER).
set -euo pipefail
cd "$(dirname "$0")/../../.."
export CYBERTRON_PRIVATE_STRINGS="${CLAUDE_CODE_ACCOUNT_UUID:-},${CLAUDE_CODE_ORGANIZATION_UUID:-},${CLAUDE_CODE_SESSION_ID:-},${CLAUDE_CODE_REMOTE_SESSION_ID:-},${CLAUDE_CODE_CONTAINER_ID:-},${CLAUDE_CODE_USER_EMAIL:-}"
stage="cybertron/out/_publish/bench36_$(date -u +%Y%m%dT%H%M%S)"
python -m cybertron publish "$@" --staging "$stage" --tags bench36,takeover --allow-dirty
python -m cybertron publish --audit "$stage"
python -m cybertron publish "$@" --staging "$stage" --tags bench36,takeover --allow-dirty --push \
  --message "bench36 (review 36b first batch): $(for r in "$@"; do basename "$(dirname "$r")"; done | tr '\n' ' ')"
