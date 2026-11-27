#!/bin/bash
# Negative tests of the sandbox: a role's container must not reach what it
# is not given. Sets a role up exactly as run-role.sh does (same mount,
# network, user, proxy), plants canaries on the host that it must not see,
# and runs checks inside it. Prints one line per check; exits non-zero if
# any check fails.
#
#   sandbox/isolation-test.sh IMAGE OUT_DIR
set -uo pipefail
IMAGE=$1 OUT=$2
GW=192.168.128.1
C=$(head -c 16 /dev/urandom | xxd -p)       # this run's canary string
[ -e "$OUT" ] && { echo "$OUT exists" >&2; exit 1; }
mkdir -p "$OUT/role-a" "$OUT/role-b/work"
git clone -q https://github.com/chrishayuk/computational-paradigms "$OUT/role-a/work"
# Canaries: another role's working copy, the role's own run record beside
# its clone, and stand-ins for the key and the custodian's transcript.
echo "canary-$C other role"  > "$OUT/role-b/work/secret.txt"
echo "canary-$C transcript"  > "$OUT/role-a/transcript.jsonl"
echo "AGE-SECRET-KEY-1CANARY$C" > "$OUT/cp-variants.key"
echo "canary-$C custodian"   > "$OUT/custodian-transcript.tar"

cat > "$OUT/role-a/work/.isolation-checks.sh" <<EOF
pass() { echo "PASS  \$1"; }; fail() { echo "FAIL  \$1"; }
check() { if eval "\$2" >/dev/null 2>&1; then pass "\$1"; else fail "\$1"; fi; }
check "runs as an unprivileged user"            '[ "\$(id -u)" != 0 ]'
check "cannot become root"                      '! sudo -n true'
check "exactly one host directory is mounted"   '[ "\$(grep -c -E "virtiofs|9p" /proc/mounts)" = 1 ] && grep -q " /work " /proc/mounts'
check "no host home directory"                  '[ ! -e /Users ] && [ ! -e /home/christopherhay ]'
check "no other role's files (canary)"          '! grep -rqs "canary-$C" / --exclude-dir=proc --exclude-dir=sys --exclude=.isolation-checks.sh'
check "no age secret key anywhere"              '! grep -rqsE "AGE-SECRET-KEY-1[02-9AC-HJ-NP-Z]{58}" / --exclude-dir=proc --exclude-dir=sys --exclude=.isolation-checks.sh'
check "no Claude session store"                 '[ -z "\$(find / -path /proc -prune -o -path "*/.claude/projects/*" -print 2>/dev/null | head -1)" ]'
check "no Codex credentials in a Claude role"   '[ ! -e /home/agent/.codex/auth.json ]'
check "no git or GitHub credentials"            '! git config --global --get credential.helper && [ ! -e ~/.git-credentials ] && [ ! -e ~/.config/gh ] && [ -z "\${GH_TOKEN:-}\${GITHUB_TOKEN:-}" ]'
check "no direct route to the internet"         '! curl -s -m 8 --noproxy "*" https://github.com'
check "no direct route to the host's LAN"       '! curl -s -m 5 --noproxy "*" http://$GW:22'
check "proxy refuses GitHub"                    '[ "\$(curl -s -m 8 -o /dev/null -w "%{http_connect}" -x http://$GW:3128 https://github.com)" = 403 ]'
check "proxy refuses a git push"                '! GIT_TERMINAL_PROMPT=0 git -c http.proxy=http://$GW:3128 -C /work push -q https://github.com/chrishayuk/computational-paradigms HEAD:refs/heads/isolation-test'
check "proxy refuses plain HTTP"                '[ "\$(curl -s -m 8 -o /dev/null -w "%{http_code}" -x http://$GW:3128 http://example.com)" = 405 ]'
check "proxy allows the Anthropic API"          '[ "\$(curl -s -m 15 -o /dev/null -w "%{http_code}" -x http://$GW:3128 https://api.anthropic.com/v1/messages)" != 000 ]'
check "the hidden variants are only ciphertext" 'head -c 21 /work/variants/wave-1/variants.tar.age | grep -q "age-encryption.org/v1"'
echo "env names holding secrets: \$(env | cut -d= -f1 | grep -i -E "token|key|secret|pass" | tr "\n" " ")"
EOF

container run --rm --platform linux/amd64 --network cp-roles \
  --volume "$OUT/role-a/work:/work" --env CLAUDE_CODE_OAUTH_TOKEN=not-a-token \
  --workdir /work "$IMAGE" bash /work/.isolation-checks.sh 2>&1 | grep -v '^\[' | tee "$OUT/result.txt"
grep -q '^FAIL' "$OUT/result.txt" && exit 1 || exit 0
