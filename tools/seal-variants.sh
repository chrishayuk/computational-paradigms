#!/usr/bin/env bash
# Seal one wave of hidden variants (PROTOCOL.md, "Hidden variants").
#
#   tools/seal-variants.sh WAVE RECIPIENT PLAINTEXT_DIR
#
# WAVE is a name such as wave-1. RECIPIENT is the owner's age public key
# (age1…). PLAINTEXT_DIR holds the custodian's files, outside the
# repository. The script:
#   1. writes a 128-bit random nonce as the first file of a tar archive of
#      PLAINTEXT_DIR, its files in sorted order;
#   2. records the SHA-256 of that archive (the plaintext);
#   3. encrypts it to RECIPIENT with age;
#   4. writes variants/WAVE/variants.tar.age and variants/WAVE/SHA256;
#   5. deletes the archive and PLAINTEXT_DIR.
# Only the ciphertext and the hash are kept. Nothing is printed of the
# plaintext.
set -euo pipefail
[ $# -eq 3 ] || { echo "usage: $0 WAVE RECIPIENT PLAINTEXT_DIR" >&2; exit 2; }
wave=$1; recipient=$2; src=$3
case "$recipient" in age1*) ;; *) echo "recipient must be an age public key (age1…)" >&2; exit 2;; esac
command -v age >/dev/null || { echo "age is not installed" >&2; exit 2; }
repo=$(cd "$(dirname "$0")/.." && pwd)
case "$(cd "$src" && pwd)" in "$repo"*) echo "PLAINTEXT_DIR must be outside the repository" >&2; exit 2;; esac
out="$repo/variants/$wave"
[ -e "$out/variants.tar.age" ] && { echo "$out already sealed" >&2; exit 2; }
mkdir -p "$out"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
head -c 16 /dev/urandom | xxd -p > "$src/0-NONCE"
tar --format ustar --uid 0 --gid 0 --uname root --gname root \
    -C "$src" -cf "$work/variants.tar" $(cd "$src" && LC_ALL=C find . -type f | LC_ALL=C sort)
hash=$(shasum -a 256 "$work/variants.tar" | cut -d' ' -f1)
age -r "$recipient" -o "$out/variants.tar.age" "$work/variants.tar"
printf '%s  variants.tar\n' "$hash" > "$out/SHA256"
printf '%s\n' "$recipient" > "$out/RECIPIENT"
rm -f "$work/variants.tar"
rm -rf "$src"
echo "sealed $wave: variants/$wave/variants.tar.age; plaintext SHA-256 in variants/$wave/SHA256"
