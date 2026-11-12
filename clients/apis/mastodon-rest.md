# Mastodon REST API

The Mastodon API is an HTTP interface for applications to work with accounts, posts and timelines on a user's server. It is a family of JSON endpoints, not the ActivityPub client-to-server protocol: a server translates between its client-facing representation and federation. Other servers implement subsets or variations, so the endpoint name alone is not a promise of identical behavior. This page describes the contract a client or compatible server must check, with Mastodon 4.7.3 source examples; it is not a compatibility claim for Misskey or any other implementation.

## Contract and capabilities

The official [API overview](https://docs.joinmastodon.org/api/) and per-method reference define Mastodon's documented interface. Versioned route prefixes such as `/api/v1` and `/api/v2` identify API families, not a guarantee that all implementations support every method. A server can add fields or omit an endpoint; clients should ignore unknown fields, handle missing optional features, and discover limits from instance information where available. `[documented]` [API guidelines](https://docs.joinmastodon.org/api/guidelines/); `[source]` Mastodon 4.7.3 [routes](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/routes.rb).

Treat server-local IDs as opaque strings, scoped to the server. A status ID in one server's API is not a global ActivityPub object identifier. Preserve IDs as strings in clients, including JavaScript clients that cannot represent every integer precisely. Follow server-provided pagination links rather than guessing IDs or assuming every endpoint has the same cursor semantics. `[documented]` [API guidelines](https://docs.joinmastodon.org/api/guidelines/).

## Authentication and permissions

Applications register with a server and use OAuth 2 access tokens. The authorization grant and requested scopes determine what a token may do; an application token is different from a token bound to a user. Request only necessary scopes and store tokens securely. For example, Mastodon 4.7.3's status controller requires `write` or `write:statuses` and a user for creation, while reading a status permits an unauthenticated request subject to visibility checks. `[source]` [status controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses_controller.rb#L7); `[documented]` [OAuth scopes](https://docs.joinmastodon.org/api/oauth-scopes/).

A valid token does not grant access to every object: a server must enforce the requesting account's visibility and relationship permissions. In Mastodon 4.7.3, an inaccessible status can be returned as 404, so a client should not infer deletion from that status alone. `[source]` [status controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses_controller.rb#L7).

## Technical details

### Posting and retrying

The following request is hand-written from the documented method and has not been run. The token and idempotency key are placeholders; send a bearer token only over HTTPS.

```http
POST /api/v1/statuses HTTP/1.1
Host: social.example
Authorization: Bearer <redacted-user-token>
Content-Type: application/json
Idempotency-Key: example-client-operation-1

{"status":"Hello, fediverse!","visibility":"public"}
```

In Mastodon 4.7.3, the controller passes `Idempotency-Key` to `PostStatusService`, which locks on account and key and records the resulting status ID in Redis for 3,600 seconds. Reuse the same key for retries of the same operation; do not assume a different implementation retains keys for this duration, or that a retry after expiry cannot create another post. Parameters also include reply, media, poll, language, content warning, scheduling and visibility fields; restrictions and result types are documented per endpoint. `[source]` [controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses_controller.rb#L7) and [service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb#L246); `[documented]` [status methods](https://docs.joinmastodon.org/methods/statuses/).

### Reading and pagination

The home timeline is a user-authenticated list, not a complete global feed. Mastodon 4.7.3 accepts `max_id`, `since_id`, `min_id` and `limit` on its home timeline and generates pagination links using its pagination concern. When present, `Link` header relations identify the next and previous pages; retain the whole supplied URL and do not assume all methods paginate identically. `[source]` [home timeline controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/timelines/home_controller.rb), [pagination concern](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/concerns/api/pagination.rb); `[documented]` [timeline methods](https://docs.joinmastodon.org/methods/timelines/).

The API also offers streaming updates, but a live stream is not a complete durable history: clients need to handle reconnects and reconcile through the appropriate REST endpoint. `[documented]` [streaming API](https://docs.joinmastodon.org/methods/streaming/). Whether a server offers a particular stream or extension is implementation-specific.

## Pitfalls

- **Duplicate posts after a timeout:** reuse an idempotency key for a retry when the server supports it, and account for expiry and uncertain responses.
- **Missing content after a 404:** check authentication and visibility as well as deletion. Do not expose private content based on cached responses after account or permission changes.
- **Skipped or repeated items:** process `Link` relations and deduplicate by server-local ID; collections may change while paginating.
- **Broken rendering:** status content is HTML from potentially untrusted users. Sanitize before rendering and do not treat remote content as trusted markup.
- **False compatibility:** a version string or one successful endpoint does not establish coverage of scopes, posting, media, pagination, streaming and error semantics. Test the actual server and version.

## Sources

- [Mastodon API documentation](https://docs.joinmastodon.org/api/) — API overview and authentication
- [API guidelines](https://docs.joinmastodon.org/api/guidelines/) — identifiers, pagination and client guidance
- [OAuth scopes](https://docs.joinmastodon.org/api/oauth-scopes/) — permissions and scope hierarchy
- [Status methods](https://docs.joinmastodon.org/methods/statuses/) and [timeline methods](https://docs.joinmastodon.org/methods/timelines/) — endpoint contracts
- [Mastodon 4.7.3 status controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses_controller.rb#L7) and [posting service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb#L246) — source-level authentication, posting and idempotency
- [Mastodon 4.7.3 home timeline controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/timelines/home_controller.rb) and [pagination concern](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/concerns/api/pagination.rb) — pagination implementation
