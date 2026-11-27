#!/bin/bash
# Run one role (PROTOCOL.md, "Roles") in its own Apple container.
#
#   sandbox/run-role.sh NAME IMAGE REF PROMPT_FILE OUT_DIR [claude|codex]
#
# NAME         a label for the run, e.g. harness-python
# IMAGE        an image built from sandbox/Containerfile.agent
# REF          the commit or tag of the public repository the role works on
# PROMPT_FILE  the role's brief, published in sandbox/briefs/
# OUT_DIR      a new, empty host directory for the run's record
#
# The container sees one thing from the host: a fresh clone of the public
# repository at REF, made from GitHub for this run alone, mounted at /work.
# Nothing else is mounted: not the home directory, not ~/.claude, not other
# roles' clones, not any key. Credentials enter as environment variables
# (Claude) or one read-only file (Codex auth). The agent's whole transcript
# is written by the host, from the container's output, to OUT_DIR, where
# the agent cannot read it back.
set -euo pipefail
NAME=$1 IMAGE=$2 REF=$3 PROMPT=$4 OUT=$5 AGENT=${6:-claude}
REPO=https://github.com/chrishayuk/computational-paradigms
[ -e "$OUT" ] && { echo "$OUT exists" >&2; exit 1; }
mkdir -p "$OUT"
git clone -q "$REPO" "$OUT/work"
git -C "$OUT/work" checkout -q --detach "$REF"
cp "$PROMPT" "$OUT/brief.md"
{
  echo "name: $NAME"
  echo "image: $IMAGE $(container image inspect "$IMAGE" | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["id"])')"
  echo "repository: $REPO $(git -C "$OUT/work" rev-parse HEAD)"
  echo "agent: $AGENT"
  echo "brief sha256: $(shasum -a 256 "$PROMPT" | cut -d' ' -f1)"
  echo "started: $(date -u +%FT%TZ)"
} > "$OUT/provenance.txt"
mounts=(--volume "$OUT/work:/work")
case $AGENT in
  claude)
    tok=${CP_TOKEN_FILE:-$HOME/.config/cp-sandbox/claude-token}
    [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] || CLAUDE_CODE_OAUTH_TOKEN=$(tr -d '[:space:]' < "$tok")
    export CLAUDE_CODE_OAUTH_TOKEN
    echo "model: ${CP_MODEL:-claude-opus-5-5}" >> "$OUT/provenance.txt"
    cmd=(claude -p "$(cat "$PROMPT")" --model "${CP_MODEL:-claude-opus-5-5}"
         --dangerously-skip-permissions --output-format stream-json --verbose)
    envs=(--env CLAUDE_CODE_OAUTH_TOKEN) ;;
  codex)
    mounts+=(--volume "$HOME/.codex/auth.json:/home/agent/.codex/auth.json:ro")
    cmd=(codex exec -s workspace-write -C /work --json "$(cat "$PROMPT")")
    envs=() ;;
esac
set +e
container run --rm --platform linux/amd64 --memory 8g --cpus 4 \
  "${mounts[@]}" "${envs[@]}" --workdir /work "$IMAGE" "${cmd[@]}" \
  > "$OUT/transcript.jsonl" 2> "$OUT/stderr.txt"
status=$?
set -e
echo "finished: $(date -u +%FT%TZ) exit $status" >> "$OUT/provenance.txt"
exit $status
