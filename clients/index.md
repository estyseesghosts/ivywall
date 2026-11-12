# Clients

Client development has its own problems, separate from federation. Supporting the Mastodon API does not mean a client can treat Mastodon, Akkoma, GoToSocial and Pixelfed identically, and Misskey and Loops have their own APIs. This section covers the client-facing APIs, how to authenticate and discover capabilities, and how to build one client that supports several software families without shrinking to Mastodon's feature set.

## Pages

Available:

- [Mastodon REST API](apis/mastodon-rest.md) — authentication, posting, pagination, and compatibility boundaries.
- [Misskey native API](apis/misskey.md) — endpoints, authentication, streaming, and client integration.
- [Streaming and recovery](architecture/streaming-and-recovery.md) — stream mechanics for Mastodon and Misskey and a reconnect-and-reconcile method.
- [Client authentication with OAuth](authentication/oauth.md) — one login flow for native and browser clients from RFC 9700, 8252 and 10017.

Not yet covered:

- Other servers' API extensions (Pleroma/Akkoma, Pixelfed, Loops).
- Authentication — per-server support for PKCE, refresh rotation and revocation; MiAuth and token storage walkthroughs.
- Architecture — an internal capability model, separate API adapters, lossless representations, predictable fallbacks; pagination, caching, offline timelines, multi-account support, background notifications, media upload, and a translation reference for a client that speaks both the Mastodon and Misskey APIs.
- Rendering — safe HTML and MFM rendering.
- Case studies — Tusky, Fedilab, Phanpy, Tokodon, Ice Cubes, native Misskey clients.

## Notes and open questions

> Unknown: how each candidate client handles capabilities in code; each case study needs a pinned source reading before it is written.

## Sources

- [Mastodon API documentation](https://docs.joinmastodon.org/api/) — REST, streaming and OAuth baseline
- [Misskey Hub API documentation](https://misskey-hub.net/en/docs/for-developers/api/) — POST-based HTTP endpoints, MiAuth and OAuth
