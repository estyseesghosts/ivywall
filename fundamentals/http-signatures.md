# HTTP signatures and authentication

Federation needs a way to tell who sent a request. ActivityPub leaves the method open, so servers sign requests with the sending actor's key (an **[HTTP signature](../glossary.md#http-signature)**) and receivers fetch the public key from the actor document. A valid signature proves the key holder sent the request; it does not by itself prove the embedded activity is permitted, so receivers also check actor ownership and authority. `[spec]` [ActivityPub security considerations](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations).

Two incompatible schemes are in use, and two digest formats.

## Schemes and digests

| | Legacy signatures | HTTP Message Signatures |
| - | ----------------- | ----------------------- |
| Document | draft-cavage-http-signatures `[spec]` | [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421) `[spec]` |
| Header | `Signature: keyId="…",headers="(request-target) host date digest",signature="…"` | `Signature-Input` plus `Signature` |
| Body integrity | `Digest: SHA-256=<base64>` (RFC 3230) | `Content-Digest: sha-256=:<base64>:` ([RFC 9530](https://www.rfc-editor.org/rfc/rfc9530)) |

RFC 9530 obsoletes RFC 3230 and its `Digest` field. `Content-Digest` hashes the message content; `Repr-Digest` hashes the representation. A receiver that supports both must hash the exact raw bytes it received, not a re-serialised copy, and must reject a body whose digest does not match. `[spec]` RFC 9530.

## What implementations do

Rows are labelled with the evidence level used in each project's [federation document](../references/federation-docs/index.md). Mastodon's own table of versions and algorithms is in its [mirrored document](../references/federation-docs/mastodon.md).

| Software | Verifies | Signs | Notable |
| -------- | -------- | ----- | ------- |
| Mastodon | legacy and RFC 9421 (4.5 onward) `[documented]` | legacy; RFC 9421 per its table | its docs say `Content-Digest` must be present and signed for RFC 9421 and that it intends to move away from the draft `[documented]` [Mastodon security](https://docs.joinmastodon.org/spec/security/) |
| NodeBB | both `[source-verified]` | RFC 9421 first, then a draft-signed retry if that fails | the retry can deliver an activity twice; receivers must deduplicate |
| Misskey | legacy | legacy (`rsa-sha256`) | checks the body digest at the endpoint, verifies the signature later in a queue `[inferred]` |
| Mbin | legacy only `[source-verified]` | legacy | a digest mismatch is only logged; `Date` freshness is a TODO |
| Pixelfed | legacy `[source-verified]` | legacy | rejects a `Date` more than one day from the server clock |
| Wafrn | legacy plus `RsaSignature2017` `[source-verified]` | legacy | one hour clock skew; digest checked |
| WriteFreely | **does not verify** inbound signatures `[source-verified]` | legacy | sends the request unsigned if signing fails |

A sender that supports only one scheme loses peers that support only the other. Sign with what the receiver verifies, and send both digest fields where the receiver's scheme needs them. Signed `GET`s ("authorized fetch") are a separate setting that many servers can require; fetching an unknown reply parent or refreshing an actor then needs a signature made as a local actor, as an instance actor, or none.

## Observed in the laboratory

`[reported]` ([problem log items 17 and 20](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md)): a strict PEM parser rejected Akkoma's `publicKeyPem`, which ended in two newlines, with HTTP 500 for every Akkoma-signed activity; trimming it let 646 stuck deliveries complete. Be strict about key ownership and signature validity and tolerant of harmless formatting. A receiver that kept a stale cached key for 24 hours after a failed verification was fixed by one forced refresh with a cooldown. See also [first-contact races](../federation/failure-modes/first-contact-races.md).

## Pitfalls

- Clock skew and a missing or stale `Date`: some receivers reject, some never check.
- Hashing a re-serialised body instead of the raw bytes.
- A key that cannot be found after an actor moves or rotates keys; see [FEP-521a](../references/feps/fep-521a.md).
- Treating a valid signature as authority; see [wrong-domain activity ids](../federation/failure-modes/wrong-domain-activity-ids.md).

> Unknown: signed-header lists and clock-skew limits for Misskey, Catodon and Lemmy.

## Sources

- [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421) — the standardised scheme
- [RFC 9530: Digest Fields](https://www.rfc-editor.org/rfc/rfc9530) — `Content-Digest` and `Repr-Digest`, replacing RFC 3230
- [Signing HTTP Messages (draft-cavage)](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) — the legacy scheme
- [Mastodon security documentation](https://docs.joinmastodon.org/spec/security/) — legacy and RFC 9421 requirements for requests to Mastodon
