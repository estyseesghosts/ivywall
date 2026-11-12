# FEP-521a: representing actors' public keys

FEP-521a describes how an actor publishes its public keys so that more than one key, and newer key types, can be used. It matters for [authentication](../../fundamentals/http-signatures.md) and for key rotation, because the older `publicKey` property usually holds a single key.

## Record

| Field | Value |
| ----- | ----- |
| Number | FEP-521a |
| Title | Representing actor's public keys |
| Status | **FINAL**, finalized 2025-06-14 `[spec]` |
| Type | implementation |
| Received | 2023-07-08 |
| Author | silverpill |
| Status checked | 2026-11-11, at FEP repository commit `bae8b04520` |

## What it defines

- Each key is an object of type `Multikey` with `id` (an absolute URI, preferably the actor id plus a fragment), `controller` (must equal the actor id) and `publicKeyMultibase` (multibase base-58-btc of a multicodec prefix and the key).
- Keys intended for signing ActivityPub objects go in the actor's `assertionMethod` array; consumers should ignore non-conforming entries there.
- An actor may have no keys. Any key type with a registered multicodec prefix is allowed.
- The rationale notes that `publicKey` is deprecated in the current Security Vocabulary. `[spec]`

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://www.w3.org/ns/cid/v1"],
  "type": "Person",
  "id": "https://server.example/users/alice",
  "assertionMethod": [{
    "id": "https://server.example/users/alice#ed25519-key",
    "type": "Multikey",
    "controller": "https://server.example/users/alice",
    "publicKeyMultibase": "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
  }]
}
```

Example copied from the FEP; it is not a capture from a server.

## Who publishes and reads it

> Unknown: which studied servers publish `Multikey` entries or read `assertionMethod`. The community-written federation documents list their own key handling; none of that is verified here. Most servers in the studied set still use `publicKey` with an RSA PEM for HTTP signatures.

## Technical details

This FEP is about key representation, not signature format. It does not say which signature scheme requests use; see [HTTP signatures](../../fundamentals/http-signatures.md).

## Sources

- [FEP-521a proposal](https://codeberg.org/fediverse/fep/src/commit/bae8b04520f72ceba74b4cdae043693f98bfad3f/fep/521a/fep-521a.md) — text and status, at the checked commit
