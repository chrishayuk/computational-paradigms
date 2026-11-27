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
