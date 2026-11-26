# Problems

| | problem | status in draft 0.3 |
|---|---|---|
| P01–P09 | the original nine | revised after review 1 |
| P10 | [state replacement](10-state-replacement.md) | added after review 1 |
| P11 | [irreversible effects](11-irreversible-effects.md) | added after review 1, reduced, with explicit commitment |
| P12 | [large alternative space](12-large-alternative-space.md) | added after review 1 |
| P13 | [deterministic scale](13-deterministic-scale.md) | added after review 1, prescribed and native |
| P14 | [a process over a message stream](14-message-stream.md) | added after review 1 |
| P15 | [merge and committed choice](15-merge-and-committed-choice.md) | added after review 1 |

All fifteen are in the primary suite. P14 and P15 exercise capabilities
that Absys is expected to lack, which is why they are included before any
system has been run. After the freeze, a new problem goes only into a
separate, dated supplementary suite (`PROTOCOL.md`).

## The proposal dropped

**Retries** were proposed under P11 and dropped. The case was an operation
that fails transiently and must be delivered exactly once. It would test a
failure-injecting stub and idempotence, not how partially specified
computations are represented or resolved.
