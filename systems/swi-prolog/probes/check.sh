#!/usr/bin/env bash
# Compare a run.sh output with an expected file.
#
# Prints the full diff (I and D lines) for information, then the diff of
# the I lines alone. Exits 1 only if the I lines differ, 2 on usage error,
# 0 otherwise. D lines never cause a failure.
#
# Usage: probes/check.sh OUTPUT EXPECTED
set -u
if [ $# -ne 2 ] || [ ! -r "$1" ] || [ ! -r "$2" ]; then
  echo "usage: $0 OUTPUT EXPECTED" >&2
  exit 2
fi
out=$1 exp=$2
tmp=$(mktemp -d) || exit 2
trap 'rm -rf "$tmp"' EXIT

echo "=== full diff (expected vs output); D lines are informational ==="
diff "$exp" "$out" && echo "(no differences)"

grep '^I|' "$exp" > "$tmp/exp.I"
grep '^I|' "$out" > "$tmp/out.I"
echo
echo "=== platform-independent (I) lines ==="
if diff "$tmp/exp.I" "$tmp/out.I"; then
  echo "I lines identical ($(wc -l < "$tmp/exp.I" | tr -d ' ') lines)"
  exit 0
else
  echo "I lines differ"
  exit 1
fi
