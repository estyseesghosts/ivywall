# Servers

Server engineering is where this wiki aims to be more useful than protocol documentation: how to store actors, objects and relationships, where validation, persistence, moderation and delivery happen in the pipeline, and what it costs. Each implementation gets a source-level case study recording architecture, storage, key code paths, API coverage, federation behaviour, measured resource use and tradeoffs. Projects are never ranked globally; a bad fit for a large public instance can be an excellent reference for a single-user server.

## Pages

Case studies:

- [Mastodon 4.7.3](case-studies/mastodon.md) — architecture, federation and operational paths.
- [Misskey 2026.10.1](case-studies/misskey.md) — architecture, native API and federation paths.

Still planned:

- Architecture and storage — schema design for actors, objects and activities; single-user versus multi-user designs; worker separation; database contention.
- Federation pipelines — inbox validation, persistence, moderation and delivery stages; queues, retries, ordering, fan-out; consistency when updates arrive before creates.
- Performance — caching of profiles, keys, posts and media; search; media pipelines; delivery throughput, p95 latency, queue growth, recovery after outages.
- Further case studies — Pleroma, Akkoma, GoToSocial, snac, Pixelfed, Loops, Wafrn, Sharkey, Iceshrimp.NET, Hollo, Friendica, Lemmy, PieFed, Mbin, PeerTube, NodeBB, Bonfire.

## Notes and open questions

Version-pinned engineering research already exists locally for Mastodon, Misskey, Akkoma, Lemmy, Loops, NodeBB, Pixelfed and Wafrn. Case studies are written from it once re-verified against upstream source at the pinned commit.

## Sources

- [Mastodon source](https://github.com/mastodon/mastodon) — Rails and Sidekiq reference implementation
- [Misskey source](https://github.com/misskey-dev/misskey) — native API, streaming, reactions
- [GoToSocial documentation](https://docs.gotosocial.org/) — headless Go server and federation controls
- [snac2 source](https://codeberg.org/grunfink/snac2) — minimal C implementation

