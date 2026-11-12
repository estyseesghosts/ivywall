# ActivityPub server-to-server

The server-to-server part of [ActivityPub](../glossary.md#activitypub) is how two servers exchange activities. The sender POSTs an activity to the recipient actor's **[inbox](../glossary.md#inbox)**; the receiver validates, stores and reacts to it. This is the part of the protocol every Fediverse server actually implements.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

Delivery by POST to inboxes, resolution of recipients from `to`, `cc`, `bto`, `bcc` and `audience`, shared inbox optimisation, and inbox forwarding for threads. `[spec]` ActivityPub, section 7. Authentication is left open by the spec.

## What implementations do

Servers authenticate deliveries with [HTTP signatures](../glossary.md#http-signature), which the spec does not require. See [authentication](http-signatures.md).

## Technical details

> Unknown: exact header sets, retry behaviour and ordering guarantees per implementation. To be filled by the [delivery](../federation/delivery/queues-and-retries.md) page and case studies.

## Pitfalls

- Treating the sender in the signature and the `actor` in the body as the same without checking.
- Assuming delivery order equals creation order.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
- [Mastodon FEDERATION.md mirror](../references/federation-docs/mastodon.md) — one implementation's stated behaviour
