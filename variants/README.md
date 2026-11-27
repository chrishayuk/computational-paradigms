# Hidden variants

Sets of hidden variants (`PROTOCOL.md`, "Hidden variants"), kept from
everyone who writes programs until the wave's programs and results are
committed. **Wave 1 is `wave-1b`** (below). The first wave-1 set,
`wave-1`, can no longer be opened.

## Wave 1b: the set in use

Made on 27 November 2026, after the freeze and before any program of the
study was written, by a new custodian agent with its own context, which
had not seen the first set. It replaces `wave-1`, whose key was lost
(below). The specification is unchanged.

121 variants over P01–P16, counted as for `wave-1`: P01 6, P02 3, P03 12,
P04 8, P05 6, P06 12, P07 14, P08 4, P09 10, P10 8, P11 8, P12 8, P13 2,
P14 2, P15 8, P16 10. Every sub-problem with stage constants has at least
two. Four sub-problems have none: their stages name only relations and
unknowns, or their only constants are vocabulary. Only the constants of a
problem's stages are varied, the ones rule 6 has a program keep in one
marked place; constants inside the definitions, sizes and arrival orders
are not. The custodian derived each variant's valid outcomes stage by
stage, and a checking script, included in the set, recomputes every one
independently (396 checks, all passed).

The set is not encrypted. The plaintext is kept by the owner outside the
repository, packed as one tar file with a 128-bit nonce (`0-NONCE`), by
`tools/commit-variants.sh`. Only its SHA-256 is published:

    eed639961517e7eb8e43ee75b46d09b1563575f1e12e79059ae9f23e499ed9b3

When the wave is opened, the tar is published here, and anyone can check
it:

    shasum -a 256 variants-wave-1b.tar    # must equal wave-1b/SHA256

The custodian's working transcript, which holds the plaintext, is kept by
the owner beside it. Agents that write programs run under the owner's
account and are told not to read either; their transcripts are published
with the results, and would show it.

## Wave 1: the first set, unopenable

The rest of this file describes the first set as it was sealed. It was
encrypted with age to the owner's key. Before any program was written,
the owner protected that key with a passphrase, which was then lost. The
archive cannot be decrypted, by the owner or anyone else, and is kept
unchanged as part of `spec-1.0`. Its count was 120; the hash of its
plaintext stays as committed.

### How it was kept

One folder per wave:

| file | what it is |
|---|---|
| `variants.tar.age` | the variants and their valid outcomes, a tar archive encrypted with [age](https://age-encryption.org) to the owner's public key |
| `SHA256` | the SHA-256 of the plaintext archive |
| `RECIPIENT` | the public key it was encrypted to |

The archive's first file, `0-NONCE`, is 128 random bits, so that a small
space of constants cannot be recovered from the hash.

**How a wave is sealed.** The variant custodian, an agent with its own
context that writes no programs, writes the variants and their valid
outcomes outside the repository. It then runs `tools/seal-variants.sh`,
which adds the nonce, hashes the archive, encrypts it, and deletes the
plaintext. Its report says what it made (how many variants per problem),
never their constants. No one who writes or runs programs, nor the
specification author, has seen the plaintext.

**How a wave is opened.** After every primary program of the wave and its
results are committed, the owner decrypts the archive locally, into the
verifier's environment, with the private key, which never enters a
conversation or the repository. The verifier checks the hash, publishes
the plaintext beside the ciphertext, and runs every program on the
variants.

Anyone can check a published plaintext:

    shasum -a 256 variants.tar    # must equal SHA256

### Wave 1 as sealed

The first comparison: Absys, SWI-Prolog, Python and ALGOL 60. Sealed on
27 November 2026, before the freeze, by a custodian agent with its own
context. 120 variants over P01–P16, at least two for every sub-problem
with constants. A variant is one complete set of substituted constants
with its own stage-by-stage valid outcomes. One that serves several
sub-problems (P02, P13, P14, P15a1/a2, P15b/b2), or gives its constants per
size n (P12, P13, P16), is counted once. *(The custodian's first report
said 138, an addition error; its own per-problem table, and its
reconciliation, give 120.)* Three sub-problems (P04d, P04f, P08b) have no constant to
vary, and have none. Sizes and arrival orders were not varied. Each
variant's valid outcomes were derived stage by stage and confirmed by a
checking script, sealed with them. Plaintext SHA-256:
`63d25bad472e72520355919fef5cae0ffd6c1cf671d831dc3820fc62e2ba027e`.

The custodian's own working transcript, which holds the plaintext, is
kept by the owner outside the repository, away from every other agent.
It is deleted, or kept as private, at the owner's choice.

Execution of wave 1 is in batches (P01–P03, P04–P08, P09–P12, P13–P16).
The batches do not change the protocol. Wave 1's variants are opened
only after the primary programs and results of all four systems on every
problem are committed.
