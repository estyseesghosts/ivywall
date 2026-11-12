# HTTP signatures and authentication

Federation needs a way to authenticate a request and decide whether its sender is authorized. Many implementations use an [HTTP signature](../glossary.md#http-signature) over request components and verify it with a public key. Key ownership, delegation, forwarded activities, and authorization require additional checks; a valid signature alone does not prove that an embedded activity is permitted. The legacy draft and RFC 9421 use different formats. `[spec]` [ActivityPub security considerations](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations), [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421).

> **Coverage incomplete.** The scheme history and the laboratory observations are cited. Not yet covered: the header lists each studied server signs and checks, digest handling, clock-skew limits and key rotation behaviour. Statements without an evidence label are general background.

## What the specification requires

ActivityPub itself requires no particular scheme. `[spec]` ActivityPub leaves authentication open.

## What implementations do

Mastodon 4.7.3 accepts both legacy HTTP signatures and RFC 9421 signatures, requires signed inbox POSTs, and can require signed GETs; its federation document describes direction and algorithms. See [Mastodon security](../security/mastodon-4-7.md) and the [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md). `[documented]`

## Technical details

> Unknown: header lists signed per implementation, digest handling, clock skew limits and key rotation behaviour. See also [FEP-521a](../references/feps/fep-521a.md).

## Pitfalls

- Clock skew and missing `Digest` headers.
- Key not found after an actor moves or rotates keys.

## Observed behaviour in interoperability tests

`[reported]` from the October 2026 laboratory: Akkoma published `publicKeyPem` ending in two newline characters, and a strict PEM parser in a test server's federation library rejected it with HTTP 500 for every Akkoma-signed activity; after trimming and re-adding one newline, 646 stuck deliveries completed on retry. A receiver should be strict about key ownership and signature validity and tolerant of harmless formatting. A test receiver also kept a stale cached key for 24 hours after verification failed; a bounded forced refresh with a cooldown fixed it, matching Mastodon's behaviour. Mastodon can require signed `GET`s, which matters for fetching unknown reply parents and actor refreshes, so a server needs to distinguish requests made as a local actor, as an instance actor, and anonymously. See [problem log items 17 and 20](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) and [first-contact races](../federation/failure-modes/first-contact-races.md).

## Sources

- [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421) — the standardised scheme
- [Signing HTTP Messages (draft-cavage)](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) — the older scheme in wide use
- [Federation bench problem log, items 17 and 20](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — Akkoma PEM whitespace and stale key refresh
