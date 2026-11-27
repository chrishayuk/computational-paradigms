#!/bin/bash
# Commit to a set of hidden variants without publishing them.
#
#   tools/commit-variants.sh WAVE PLAINTEXT_DIR
#
# Adds a 128-bit nonce (0-NONCE) to PLAINTEXT_DIR, packs it into
# PLAINTEXT_DIR.tar beside it, and writes the tar's SHA-256 to
# variants/WAVE/SHA256. The plaintext and the tar stay where they are,
# outside the repository, until the wave is opened: then the tar is
# published and anyone can check it against the committed hash.
set -euo pipefail
WAVE=$1 DIR=${2%/}
ROOT=$(git rev-parse --show-toplevel)
case "$(cd "$DIR" && pwd)/" in "$ROOT"/*) echo "plaintext must be outside the repository" >&2; exit 1;; esac
[ -e "$DIR/0-NONCE" ] && { echo "$DIR already committed" >&2; exit 1; }
head -c 16 /dev/urandom | xxd -p > "$DIR/0-NONCE"
(cd "$DIR" && find . -type f | LC_ALL=C sort | tar -cf "$DIR.tar" -T -)
mkdir -p "$ROOT/variants/$WAVE"
shasum -a 256 "$DIR.tar" | cut -d' ' -f1 > "$ROOT/variants/$WAVE/SHA256"
chmod -R go-rwx "$DIR" "$DIR.tar"
echo "variants/$WAVE/SHA256: $(cat "$ROOT/variants/$WAVE/SHA256")"
