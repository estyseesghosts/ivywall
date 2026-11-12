# Mastodon REST API

The Mastodon REST and streaming API is the de facto client API of the Fediverse. Many servers (Akkoma, GoToSocial, Pixelfed, snac and others) reimplement part of it, so a client written against Mastodon often works elsewhere, with gaps.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Behavior

OAuth 2 with scopes, versioned endpoints (`/api/v1`, `/api/v2`), `Link`-header pagination, and a streaming endpoint. `[documented]` Mastodon API docs.

## Technical details

> Unknown: which endpoints each non-Mastodon server implements, and where they diverge. This is the basis for the capability model in [Clients](../index.md).

## Pitfalls

- Assuming the server reports an accurate version string.
- Assuming every endpoint behaves the same across servers.

## Sources

- [Mastodon API documentation](https://docs.joinmastodon.org/api/) — the API reference
