# Clients

Client development has its own problems, separate from federation. Supporting the Mastodon API does not mean a client can treat Mastodon, Akkoma, GoToSocial and Pixelfed identically, and Misskey and Loops have their own APIs. This section covers the client-facing APIs, how to authenticate and discover capabilities, and how to build one client that supports several software families without shrinking to Mastodon's feature set.

## Pages

No topic pages yet. Planned:

- API families — Mastodon REST and streaming, Misskey HTTP and WebSocket, Pleroma/Akkoma extensions, Pixelfed additions, Loops REST.
- Authentication — OAuth scopes, MiAuth, token storage.
- Architecture — an internal capability model, separate API adapters, lossless representations, predictable fallbacks; pagination, caching, offline timelines, multi-account support, live updates, background notifications, media upload.
- Rendering — safe HTML and MFM rendering.
- Case studies — Tusky, Fedilab, Phanpy, Tokodon, Ice Cubes, native Misskey clients.

## Notes and open questions

> Unknown: how each candidate client handles capabilities in code; each case study needs a pinned source reading before it is written.

## Sources

- [Mastodon API documentation](https://docs.joinmastodon.org/api/) — REST, streaming and OAuth baseline
- [Misskey Hub API documentation](https://misskey-hub.net/en/docs/for-developers/api/) — POST-based HTTP endpoints, MiAuth and OAuth
