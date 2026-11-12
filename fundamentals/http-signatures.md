# HTTP signatures and authentication

Federation needs a way to authenticate a request and decide whether its sender is authorized. Many implementations use an [HTTP signature](../glossary.md#http-signature) over request components and verify it with a public key. Key ownership, delegation, forwarded activities, and authorization require additional checks; a valid signature alone does not prove that an embedded activity is permitted. The legacy draft and RFC 9421 use different formats. `[spec]` [ActivityPub security considerations](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations), [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421).

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

ActivityPub itself requires no particular scheme. `[spec]` ActivityPub leaves authentication open.

## What implementations do

Mastodon 4.7.3 accepts both legacy HTTP signatures and RFC 9421 signatures, requires signed inbox POSTs, and can require signed GETs; its federation document describes direction and algorithms. See [Mastodon security](../security/mastodon-4-7.md) and the [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md). `[documented]`

## Technical details

> Unknown: header lists signed per implementation, digest handling, clock skew limits and key rotation behaviour. See also [FEP-521a](../references/feps/fep-521a.md).

## Pitfalls

- Clock skew and missing `Digest` headers.
- Key not found after an actor moves or rotates keys.

## Sources

- [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421) — the standardised scheme
- [Signing HTTP Messages (draft-cavage)](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) — the older scheme in wide use
