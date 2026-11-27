# Hidden variants

Sealed sets of hidden variants (`PROTOCOL.md`, "Hidden variants"). One
folder per wave:

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

## Wave 1

The first comparison: Absys, SWI-Prolog, Python and ALGOL 60. Sealed on
27 November 2026, before the freeze, by a custodian agent with its own
context. 138 variants over P01–P16, at least two for every sub-problem
with constants. Three sub-problems (P04d, P04f, P08b) have no constant to
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
