# Sandbox

How every role after the freeze is isolated (`PROTOCOL.md`, "Roles"). Each
harness author, implementation author and classifier runs as a headless
agent in its own [Apple container](https://github.com/apple/container),
a Linux x86_64 virtual machine (under Rosetta on an arm64 Mac).

The container sees from the host only a fresh clone of this public
repository, made from GitHub for that run, at the commit the role works
on. It does not see the owner's home directory, other agents' sessions or
transcripts, other roles' working copies, the variant custodian's
transcript, or the key that opens the hidden variants. A role's whole
transcript is written by the host from the container's output, outside
the clone, so the agent cannot read it back. What a role writes enters the
repository only through a commit on its own branch, merged after it ends.

| file | what it is |
|---|---|
| `Containerfile.systems` | the pinned Absys and ALGOL 60 builds and x1sim (`PINS.md`), cloned from GitHub at their commits and built with Rust 1.98.0 |
| `Containerfile.agent` | a role's image: a pinned system image, the Claude Code and Codex CLIs, an unprivileged user |
| `run-role.sh` | runs one role, and records its provenance, brief and transcript |
| `briefs/` | the brief each role was given, verbatim |

## Images

| image | base | id |
|---|---|---|
| `cp-systems:spec-1.0` | `rust:1.98.0-bookworm` `sha256:82150a52ec202c1b14d7817e14516c392bb7f5cfebd88f1ed531cb37ebd39922` | `08ccf0f27d55…` |
| `cp-agent-systems:spec-1.0` | `cp-systems:spec-1.0` | `23fefb8016c5…` |
| `cp-agent-swi-prolog:spec-1.0` | `swipl:11.0.1` (pinned digest) | `bbe4166e4219…` |
| `cp-agent-python:spec-1.0` | `python:3.13.7` (pinned digest) | `65d15cef3fa5…` |

Agent CLIs: Claude Code 2.1.332, codex-cli 0.166.0. The pinned CI images
fix SWI-Prolog and CPython. The Absys and ALGOL 60 repositories' CI uses
"stable" Rust; the sandbox fixes 1.98.0, the release current at the
freeze.

## Provenance

Each run's `provenance.txt` (image id, repository commit, agent and model,
the brief's SHA-256, start and end) is kept with the role's output, and
published with the result it produced.

## Network and credentials

Role containers sit on `cp-roles`, a host-only network with no route out.
The one way out is `egress-proxy.py` on the host, which accepts only HTTPS
CONNECT, to `api.anthropic.com` (Claude roles) or OpenAI's API (Codex
roles), and logs every request. GitHub is refused, so a role can neither
push nor publish. A Claude role receives only its token, as an
environment variable; Codex's credentials are mounted only into Codex
roles. A credential the agent needs is necessarily readable by it; the
proxy limits where it can be sent.

## Isolation tests

`isolation-test.sh IMAGE DIR` sets a role up as `run-role.sh` does, plants
canaries on the host (another role's working copy, the role's own
transcript file, stand-ins for the key and the custodian's transcript),
and checks from inside: unprivileged, no root; exactly one host directory
mounted; no host home; no canary; no age secret key anywhere in the
image; no Claude session store; no Codex credentials in a Claude role; no
git or GitHub credentials; no direct route to the internet or the host;
the proxy refuses GitHub, a `git push` and plain HTTP, and allows the
Anthropic API; the hidden variants are present only as ciphertext. On 27
November 2026 all 16 checks passed in all three images. (The first run
failed "no age secret key": the Claude Code binary contains the bare
prefix `AGE-SECRET-KEY-1`. The check now matches a whole key.)

## Syntax checking before a program is fixed

`PROTOCOL.md`, phase 5: programs are "fixed before any of them is run".
Checking a program's syntax, without executing any of it, is not running
it. So:

| | |
|---|---|
| **syntax check** | permitted before a program is fixed, with the harness's `check`, which parses or compiles and executes nothing |
| **execution** | none, of any kind, before the primary program is committed |
| **tuning on results** | never (`PROTOCOL.md`, "Writing a program", rule 7) |
| **transcription fixes** | after results, as rule 7 says, each recorded as a diff with its reason |

An implementation author's container has the system and its `check`, so
the restriction on executing is enforced by audit: every command the
author ran is in its transcript, and any execution other than `check` is
reported as a breach of protocol with the program it touched. A program
that fails to run in its primary run keeps that result; a corrected
transcription is reported beside it, never in its place.
