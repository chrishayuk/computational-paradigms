# Problems

| | problem | status in draft 0.2 |
|---|---|---|
| P01–P09 | the original nine | revised after review |
| P10 | [state replacement](10-state-replacement.md) | proposed in review; written |
| P11 | [irreversible effects](11-irreversible-effects.md) | proposed in review; written, reduced |
| P12 | [large alternative space](12-large-alternative-space.md) | proposed in review; written |
| P13 | deterministic scale | proposed in review; not written |
| P14 | a stateful process over a message stream | proposed in review; not written |
| P15 | nondeterministic merge and committed choice | proposed in review; not written |

Which proposals are kept is decided before the freeze. After it, a new
problem goes only into a separate, dated supplementary suite
(`PROTOCOL.md`).

## The proposals not yet written

- **P13, deterministic scale.** Sum ⟨1 … n⟩, and reverse a sequence of n,
  for n = 10³, 10⁴, 10⁵. Record how steps and store grow with n, within
  each system. This shows the bookkeeping cost of suspension and of
  data-directed resumption, where imperative code and Prolog are expected
  to do well.
- **P14, a process over a message stream.** A counter receives ɪɴᴄ, ɪɴᴄ,
  ʀᴇᴀᴅ(r₁), ɪɴᴄ, ʀᴇᴀᴅ(r₂), the messages arriving as stages. Valid: r₁ = 2,
  r₂ = 3. This is the native pattern of Concurrent Prolog, concurrent
  constraint programming and Oz.
- **P15, merge and committed choice.**
  - Merge ⟨1, 2⟩ and ⟨3, 4⟩: valid, any one of the six interleavings, or
    all six.
  - A fairness variant merges an unbounded stream with ⟨9⟩, and 9 must
    appear in a finite prefix.
  - A mutual-exclusion variant: two requests for one resource, of which
    exactly one is granted.

## The proposal dropped

**Retries** were proposed under P11 and dropped. The case was an operation
that fails transiently and must be delivered exactly once. It would test a
failure-injecting stub and idempotence, not how partially specified
computations are represented or resolved.
