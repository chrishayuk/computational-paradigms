# P14. A process over a message stream

**Probes:** whether a computation can persist as a process with its own
state, receiving messages as they arrive and answering between them.

## Vocabulary

A **counter** holds a count, 0 at first. It receives messages:

- ɪɴᴄ adds one to the count;
- ʀᴇᴀᴅ(r) makes r equal to the count when the message is received.

Messages are taken in the order they arrive.

## P14a. Messages as stages

| stage | message | valid outcomes |
|---|---|---|
| 1 | ɪɴᴄ | no unknowns |
| 2 | ɪɴᴄ | no unknowns |
| 3 | ʀᴇᴀᴅ(r₁) | r₁ = 2 |
| 4 | ɪɴᴄ | r₁ = 2 |
| 5 | ʀᴇᴀᴅ(r₂) | r₁ = 2, r₂ = 3 |

## P14b. Messages as one sequence

One stage: the counter receives the sequence ⟨ɪɴᴄ, ɪɴᴄ, ʀᴇᴀᴅ(r₁), ɪɴᴄ,
ʀᴇᴀᴅ(r₂)⟩. Valid outcome: r₁ = 2, r₂ = 3.

## P14c. A stream that stays open

The stages of P14a, then:

| stage | message | valid outcomes |
|---|---|---|
| 6 | ɪɴᴄ | r₁ = 2, r₂ = 3 |
| 7 | ʀᴇᴀᴅ(r₃) | r₁ = 2, r₂ = 3, r₃ = 4 |

No stage closes the stream. The counter must still accept messages after
any stage.

## Observations

- How the count is held between messages: as a process's state, as the tail
  of a stream not yet bound, as a value replaced, or recomputed from all
  the messages so far.
- Whether each stage is received into the running process, or the messages
  so far are reposed (restart cost).
- Whether r₁ is reported at stage 3, before later messages arrive.
- P14c: whether the computation is *suspended* waiting for messages, or
  *finished* and restarted.
