#!/usr/bin/env bash
# Fails if a tracked file holds a local path or is a generated binary.
# Run locally before committing, and in CI on every push.
set -u
cd "$(dirname "$0")/.." || exit 2
bad=0
paths=$(git grep -nIE '(/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+/|/private/tmp/|C:\\Users\\)' -- . ':!tools/check-hygiene.sh' || true)
if [ -n "$paths" ]; then
  echo "local paths in tracked files:"; echo "$paths"; bad=1
fi
binaries=$(git ls-files | grep -E '(__pycache__/|\.pyc$|\.pyo$|\.so$|\.dylib$|\.o$|\.DS_Store$|\.class$)' || true)
if [ -n "$binaries" ]; then
  echo "generated or binary files tracked:"; echo "$binaries"; bad=1
fi
[ $bad -eq 0 ] && echo "hygiene: no local paths, no generated binaries"
exit $bad
