# Servers

Server engineering is where this wiki aims to be more useful than protocol documentation: how to store actors, objects and relationships, where validation, persistence, moderation and delivery happen in the pipeline, and what it costs. Each implementation gets a source-level case study recording architecture, storage, key code paths, API coverage, federation behaviour, measured resource use and tradeoffs. Projects are never ranked globally; a bad fit for a large public instance can be an excellent reference for a single-user server.

## Pages

Case studies:

- [Akkoma case study](case-studies/akkoma.md) — version-pinned architecture and federation.
- [GoToSocial case study](case-studies/gotosocial.md) — version-pinned architecture and federation.
- [Lemmy case study](case-studies/lemmy.md) — version-pinned architecture and federation.
- [Loops case study](case-studies/loops-server.md) — version-pinned architecture and federation.
- [NodeBB case study](case-studies/nodebb.md) — version-pinned architecture and federation.
- [Pixelfed case study](case-studies/pixelfed.md) — version-pinned architecture and federation.
- [Wafrn case study](case-studies/wafrn.md) — version-pinned architecture and federation.
- [WriteFreely case study](case-studies/writefreely.md) — version-pinned architecture and federation.
- [Mastodon 4.7.3](case-studies/mastodon.md) — architecture, federation and operational paths.
- [Misskey 2026.10.1](case-studies/misskey.md) — architecture, native API and federation paths.
- [Mastodon federation pipeline](federation-pipelines/mastodon-4-7.md) and [Misskey federation pipeline](federation-pipelines/misskey.md) — receipt and delivery.
- [Mastodon storage](storage/mastodon-4-7.md) and [Misskey storage](storage/misskey.md) — persistence, queues, caches and recovery.

Not yet covered (the Mastodon and Misskey storage and pipeline pages and the ten case studies above exist):

- Storage and pipeline pages for the other studied servers; single-user versus multi-user designs; worker separation; database contention.
- Architecture decisions compared with measurements: synchronous versus queued inbox, relational versus key-value storage, eager versus lazy remote fetching, cache versus authoritative state, push versus pull recovery.
- Performance — caching of profiles, keys, posts and media; search; media pipelines; delivery throughput, p95 latency, queue growth, recovery after outages. Nothing has been measured yet.
- Further case studies — Pleroma, snac, Sharkey, Iceshrimp.NET, Hollo, Friendica, PieFed, Mbin, PeerTube and Bonfire.

## Notes and open questions

The case studies describe specific source revisions. Live interoperability, recovery and capacity findings require separately documented tests.

## Sources

- [Mastodon source](https://github.com/mastodon/mastodon) — Rails and Sidekiq reference implementation
- [Misskey source](https://github.com/misskey-dev/misskey) — native API, streaming, reactions
- [GoToSocial documentation](https://docs.gotosocial.org/) — headless Go server and federation controls
- [snac2 source](https://codeberg.org/grunfink/snac2) — minimal C implementation
