# Guide: a minimal ActivityPub actor

A minimal interoperable server needs an actor document, delivery endpoints, authentication and follow handling. Peers may require WebFinger and HTTP signatures beyond the 2018 ActivityPub Recommendation. The exact requirements depend on the peer; this page is an outline, not a tested implementation. `[spec]` [ActivityPub §§4–5, 7.5 and B.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/); `[documented]` [Mastodon 4.7.3 federation requirements](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md).

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Before you start

Read [WebFinger](../fundamentals/webfinger.md), [ActivityPub server-to-server](../fundamentals/activitypub-s2s.md) and [HTTP signatures](../fundamentals/http-signatures.md).

## Task outline

1. Serve WebFinger and an actor document with a public key.
2. Accept signed POSTs at an inbox and verify them, with the fetch rules from [SSRF](../security/ssrf.md).
3. Handle `Follow` according to local policy, returning `Accept` or `Reject` as appropriate.
4. Deliver `Create` to followers' inboxes.

No code yet.

## Technical details

> Unknown: reference implementation to follow. snac is the proposed minimal case study.

## Open questions

- Which interoperability checks must pass before real servers will follow the actor?

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
