# Fundamentals

The protocol layer every Fediverse server and client builds on: the data model, how servers deliver to each other, how accounts are discovered, and how requests are authenticated. These pages describe what the specifications require, what implementations commonly do, and where the two differ, with real HTTP requests and JSON. They are the foundation the rest of the wiki links back to.

## Pages

Pages:

- [ActivityStreams 2.0](activitystreams.md) — stub.
- [ActivityPub server-to-server](activitypub-s2s.md) — delivery, addressing and federation responsibilities.
- [ActivityPub client-to-server](activitypub-c2s.md) — the standard client protocol and server responsibilities.
- [WebFinger](webfinger.md) — stub.
- [NodeInfo](nodeinfo.md) — stub.
- [HTTP signatures and authentication](http-signatures.md) — stub.
- [Identity and account handles](identity.md) — stub.
- [Extensions and FEPs](extensions.md) — stub.

Still planned, in priority order:

- ActivityStreams 2.0 — actors, objects, activities, collections, JSON-LD contexts.
- ActivityPub server-to-server — inbox and outbox delivery, shared inboxes, recipient resolution, forwarding.
- ActivityPub client-to-server — the standard client protocol and why few servers implement it.
- Discovery — WebFinger, NodeInfo, actor lookup, remote object resolution.
- Authentication — HTTP signatures, signed fetches, key discovery and rotation, OAuth.
- Identity — actor ids, account handles, multiple domains, migration.
- Extensions — FEPs, LitePub conventions, software-specific vocabularies.

## Notes and open questions

> Unknown: which Mastodon extensions are strictly required for interoperability versus merely common. Pages are added as the research is verified against pinned source.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — the base protocol and its security considerations
- [ActivityStreams 2.0 Core](https://www.w3.org/TR/activitystreams-core/) — the data model
- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — extension proposals

