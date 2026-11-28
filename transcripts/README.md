# Transcripts

Every role's transcript, published with its results (`AMENDMENTS.md` 1,
`PROTOCOL.md`, "Roles": each role's provenance is recorded). They are the
evidence for the audits: `programs/AUDIT-1A.md` for the implementation
authors, and `results/BATCH-1A.md`, "Classifier provenance", for the
classifiers.

## Batch 1A

| file | role | agent |
|---|---|---|
| `harness-common.jsonl` | harness author, common part (phase 4) | Claude |
| `harness-absys.jsonl`, `harness-swi-prolog.jsonl`, `harness-python.jsonl`, `harness-algol-60.jsonl` | harness authors (phase 4), with every fix asked of them after qualification | Claude |
| `s-python-extended.jsonl` | author of Python *extended*'s S mechanisms (phase 4) | Claude |
| `stages-check-codex.log` | independent check of `harnesses/stages.json` | Codex |
| `implementation-<system>.jsonl` | implementation authors (phase 5) | Claude |
| `classifier-A-<system>.jsonl` | classifier A | Claude |
| `classifier-B-<system>.jsonl` | classifier B (`codex exec --json`) | Codex |
| `briefs/` | each role's brief, as rendered for it | |

A Claude transcript holds each prompt the agent was given, each message
sent to it while it worked (`queued_command`), and every message, tool
call and tool result of the agent. A Codex log holds its commands, file
changes and messages. Its brief went on standard input and is in
`briefs/`.

**Not published here.** The variant custodians' transcripts hold the
hidden variants. They are kept with the variants (`AMENDMENTS.md` 1). The
second custodian's transcript is published when wave-1b is revealed; the
first custodian's transcript is encrypted to the lost key and cannot be
opened.

## Redactions

Made by `tools/redact-transcripts.py`. Its docstring gives the rules,
which keep the agent's own work whole and remove only context the agent
tooling injected on the owner's behalf. The script screens its output for
what it is meant to remove and fails if any is left. Each removal inside a
message leaves a marker `[redacted by tools/redact-transcripts.py: KIND]`.

What was removed:

- **The owner's Claude memory index** (two entry titles), which the
  tooling put into every Claude agent's context. Four classifier-A agents
  disclose that it was there. Their disclosures are kept, and one agent's
  paraphrase of what the entries are about is replaced by a marker.
- **The tooling's own bookkeeping entries**: system-prompt snapshots, the
  lists of the owner's connected tools, MCP servers and their
  instructions, installed skills and agent types, the environment
  description, the account's organisation identifier, and file-edit
  bookkeeping. None of it is the agent's work. They are dropped whole, and
  the count is below.
- **One other injected reminder**, in `harness-python.jsonl`: a note that
  a file the agent read was empty. It was not on the list of reminders
  kept, so it is redacted.
- **The owner's home directory**, written `~`, and the account name, written
  `<owner>` (the owner column of `ls -l`, for instance).

Nothing written by an agent was removed, except the one paraphrase above.
No transcript held an email address, a credential, a token or a key, and
each was screened for them.

| transcript | bookkeeping entries dropped | other reminders redacted | paraphrase redacted |
|---|---|---|---|
| `harness-common.jsonl` | 57 | 0 | 0 |
| `harness-absys.jsonl` | 106 | 0 | 0 |
| `harness-swi-prolog.jsonl` | 287 | 0 | 0 |
| `harness-python.jsonl` | 139 | 1 | 0 |
| `harness-algol-60.jsonl` | 138 | 0 | 0 |
| `s-python-extended.jsonl` | 77 | 0 | 0 |
| `implementation-absys.jsonl` | 55 | 0 | 0 |
| `implementation-swi-prolog.jsonl` | 64 | 0 | 0 |
| `implementation-python.jsonl` | 95 | 0 | 0 |
| `implementation-algol-60.jsonl` | 104 | 0 | 0 |
| `classifier-A-absys.jsonl` | 57 | 0 | 1 |
| `classifier-A-swi-prolog.jsonl` | 63 | 0 | 0 |
| `classifier-A-python.jsonl` | 81 | 0 | 0 |
| `classifier-A-algol-60.jsonl` | 76 | 0 | 0 |
| Codex logs and briefs | — | — | — |

The bookkeeping count includes the entries kept as `queued_command`
messages: 1 for Absys, 6 for SWI-Prolog, 1 for Python and 4 for ALGOL 60,
all harness authors.

## Batch 1B

`batch-1B/`, by the same rules and the same script.

| file | role | agent |
|---|---|---|
| `implementation-<system>.jsonl` | implementation authors, batch 1B (audit: `programs/AUDIT-1B.md`) | Claude |
| `harness-absys.jsonl` | the Absys harness author, resumed for the measurement fix (`98baa62`). The file is the agent's whole transcript, so it begins with its batch 1A part, published in `batch-1A/` | Claude |
| `classifier-A-<system>-<problems>.jsonl` | classifier A, one agent per system and range of problems | Claude |
| `classifier-B-<system>-<problems>.jsonl` | classifier B (`codex exec --json`) | Codex |
| `briefs/` | each role's brief, as rendered for it | |

| transcript | bookkeeping entries dropped | paraphrase redacted |
|---|---|---|
| `implementation-absys.jsonl` | 60 | 2 |
| `implementation-swi-prolog.jsonl` | 71 | 0 |
| `implementation-python.jsonl` | 108 | 0 |
| `implementation-algol-60.jsonl` | 103 | 0 |
| `harness-absys.jsonl` | 118 | 0 |
| `classifier-A-absys-P04-P06-P08.jsonl` | 66 | 0 |
| `classifier-A-swi-prolog-P04.jsonl` | 49 | 0 |
| `classifier-A-swi-prolog-P05-P08.jsonl` | 94 | 0 |
| `classifier-A-python-P04-P06.jsonl` | 73 | 0 |
| `classifier-A-python-P07.jsonl` | 58 | 0 |
| `classifier-A-python-P08.jsonl` | 78 | 1 |
| `classifier-A-algol-60-P04-P06.jsonl` | 76 | 0 |
| `classifier-A-algol-60-P07-P08.jsonl` | 83 | 0 |
| `classifier-A-absys-P05.jsonl` | 72 | 0 |
| Codex logs and briefs | — | — |

As in batch 1A, the Claude agents disclose that the memory index was put
into their context (six of the fourteen). Those disclosures are kept.

## Correction to the batch 1A redaction

The batch 1A screen looked for one wording of what the memory index's
entries are about. Agents used others, and two were missed: one in
`batch-1A/implementation-absys.jsonl`, one in
`batch-1A/classifier-A-python.jsonl`. The same agents had also written
them into their notes, which were committed: `programs/absys/README.md`
(twice, batches 1A and 1B), `results/absys/classes/A/absys.notes.md` and
`results/python/classes/A/python.notes.md`, and, in batch 1B,
`results/python/classes-1B/A/parts/python-P08/python.notes.md`. The
script now lists every wording found and screens for the subject words
themselves, and each of these files has been redacted with the same
marker. Nothing else in them was changed. The earlier versions remain in
the repository's history.
