# Fundamentals

The protocol layer every Fediverse server and client builds on: the data model, how servers deliver to each other, how accounts are discovered, and how requests are authenticated. These pages describe what the specifications require, what implementations commonly do, and where the two differ, with real HTTP requests and JSON. They are the foundation the rest of the wiki links back to.

## Pages

Pages:

- [ActivityStreams 2.0](activitystreams.md) — data model; JSON-LD handling per server not yet covered.
- [ActivityPub server-to-server](activitypub-s2s.md) — delivery, addressing and federation responsibilities.
- [ActivityPub client-to-server](activitypub-c2s.md) — the standard client protocol and server responsibilities.
- [WebFinger](webfinger.md) — RFC 7033 lookup and laboratory observations.
- [NodeInfo](nodeinfo.md) — discovery document; per-server fields not yet covered.
- [HTTP signatures and authentication](http-signatures.md) — signature schemes and observed behaviour; per-server header lists not yet covered.
- [Identity and account handles](identity.md) — handles, actor ids and moves; per-server `Move` handling not yet covered.
- [Extensions and FEPs](extensions.md) — how extensions work; the per-extension table lives in the compatibility and FEP records.

Not yet covered (each topic above has a page; these gaps remain):

- Remote object resolution and actor lookup, per server.
- OAuth for apps and signed-fetch ("authorized fetch") behaviour per server.
- Collections and paging beyond the outline in the ActivityPub pages.
- LitePub conventions and software-specific vocabularies beyond FEPs.

## Notes and open questions

> Unknown: which Mastodon extensions are strictly required for interoperability versus merely common. Pages are added as the research is verified against pinned source.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — the base protocol and its security considerations
- [ActivityStreams 2.0 Core](https://www.w3.org/TR/activitystreams-core/) — the data model
- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — extension proposals

