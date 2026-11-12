# Guide: a minimal ActivityPub actor

The smallest useful server: one account that other servers can find, follow, and read. It needs WebFinger, an actor document, an inbox that verifies signatures, and the ability to answer `Follow` with `Accept`.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Before you start

Read [WebFinger](../fundamentals/webfinger.md), [ActivityPub server-to-server](../fundamentals/activitypub-s2s.md) and [HTTP signatures](../fundamentals/http-signatures.md).

## Task outline

1. Serve WebFinger and an actor document with a public key.
2. Accept signed POSTs at an inbox and verify them, with the fetch rules from [SSRF](../security/ssrf.md).
3. Handle `Follow` by replying `Accept`.
4. Deliver `Create` to followers' inboxes.

No code yet.

## Technical details

> Unknown: reference implementation to follow. snac is the proposed minimal case study.

## Open questions

- Which interoperability checks must pass before real servers will follow the actor?

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
