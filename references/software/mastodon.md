# Mastodon 4.7.3 fact sheet

This fact sheet identifies the exact source used by the [Mastodon case study](../../servers/case-studies/mastodon.md). It describes a historical release, not every Mastodon deployment or later version.

**Release:** 4.7.3, 1 October 2026. **Commit:** [`8ff11c2bb7b9f0714e947b10fa3629c6542c7121`](https://github.com/mastodon/mastodon/commit/8ff11c2bb7b9f0714e947b10fa3629c6542c7121). `[source]` [release](https://github.com/mastodon/mastodon/releases/tag/v4.7.3).

## Facts

| Fact | Value | Evidence |
| --- | --- | --- |
| Primary application | Ruby on Rails | `[source]` [Gemfile](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/Gemfile) |
| Durable database | PostgreSQL | `[source]` [database configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/database.yml) |
| Jobs and cache | Sidekiq and Redis | `[source]` [Sidekiq configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/sidekiq.yml), [deployment configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/docker-compose.yml) |
| Streaming | Separate Node service, WebSocket and server-sent events | `[source]` [streaming implementation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/streaming/index.js) |
| Client interfaces | Versioned REST routes, OAuth, and streaming | `[source]` [API routes](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/routes/api.rb), [OAuth routes](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/routes.rb) |
| Federation | ActivityPub server-to-server; WebFinger, HTTP signatures, NodeInfo | `[documented]` [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) |
| HTTP signature verification | Cavage HTTP signatures and RFC 9421; algorithm and direction vary | `[documented]` [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) |
| Historical security status | Affected by the ActivityPub identifier verification issue fixed in 4.7.4 | `[documented]` [security advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j) |

## Technical details

The 4.7.3 federation document says POST requests require HTTP signatures; installations may require signatures on GET requests. It documents inbound RSA and Ed25519 RFC 9421 verification and outbound RFC 9421 fallback when the older signature format receives a 400 or 401 response. It lists support for FEP-67ff, f1d5, 8fcf, 5feb, 044f and 3b86, and describes the narrower inbound-only FEP-521a key and FEP-8b32 proof support. Consult the [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) for the exact version and direction, rather than treating the names as a feature matrix. `[documented]`

The source checkout is available locally as the `v4.7.3` Git tag. Its release commit was checked with `git rev-list -n 1 v4.7.3`; no live server, interoperability test or resource benchmark was run for this fact sheet. `[source]`

## Sources

- [Mastodon 4.7.3 release](https://github.com/mastodon/mastodon/releases/tag/v4.7.3) — version and release date.
- [Mastodon source at the release commit](https://github.com/mastodon/mastodon/tree/8ff11c2bb7b9f0714e947b10fa3629c6542c7121) — source paths listed in the table.
- [Pinned FEDERATION.md](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) — protocols, FEPs, signatures and limits.
- [Identifier verification advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j) — affected and fixed versions.

