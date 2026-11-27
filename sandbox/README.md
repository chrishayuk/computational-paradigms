# Sandbox

How roles after the freeze are run (`PROTOCOL.md`, "Roles").

**Agents.** Each harness author, implementation author and classifier is a
separate agent with its own context, given only its brief (`briefs/`,
verbatim) and its own fresh clone of this public repository, at the
commit it works on, in which it writes. It enters the repository only
through a commit on its own branch, merged after it ends. Agents run on
the owner's machine, under the owner's account. They are told to read
nothing outside their clone and the pinned system sources, but this is
not enforced: other agent sessions on the machine were readable. None of
those sessions contains the hidden variants' plaintext. The variants are
age ciphertext and the custodian's transcript is encrypted to the
owner's key. The harness authors, who write no program and use no
constants, ran while that key was an unprotected file in the owner's home
directory; implementation authors start only after it is
passphrase-protected, so that no agent can decrypt either.

**Systems.** Programs are run in the pinned images, on Linux x86_64 under
Apple's `container` (Rosetta on an arm64 Mac).

| file | what it is |
|---|---|
| `Containerfile.systems` | the pinned Absys and ALGOL 60 builds and x1sim (`PINS.md`), cloned from GitHub at their commits and built with Rust 1.98.0 |
| `Containerfile.agent` | adds an unprivileged user (and agent CLIs, unused) to a pinned image |
| `briefs/` | the brief each role was given, verbatim |

## Images

| image | base | id |
|---|---|---|
| `cp-systems:spec-1.0` | `rust:1.98.0-bookworm` `sha256:82150a52ec202c1b14d7817e14516c392bb7f5cfebd88f1ed531cb37ebd39922` | `08ccf0f27d55…` |
| `cp-agent-systems:spec-1.0` | `cp-systems:spec-1.0` | `23fefb8016c5…` |
| `cp-agent-swi-prolog:spec-1.0` | `swipl:11.0.1` (pinned digest) | `bbe4166e4219…` |
| `cp-agent-python:spec-1.0` | `python:3.13.7` (pinned digest) | `65d15cef3fa5…` |

The pinned CI images fix SWI-Prolog and CPython. The Absys and ALGOL 60 repositories' CI uses
"stable" Rust; the sandbox fixes 1.98.0, the release current at the
freeze.

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

The restriction on executing is enforced by audit: every command an
implementation author ran is in its transcript, and any execution other
than `check` is reported as a breach of protocol with the program it
touched. A program that fails to run in its primary run keeps that result; a corrected
transcription is reported beside it, never in its place.
