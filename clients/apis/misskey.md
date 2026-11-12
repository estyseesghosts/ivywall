# Misskey native client API

Misskey has a native HTTP and WebSocket API for its web client and other applications. It does not follow the Mastodon REST API's endpoint and data model conventions, even though both products federate with ActivityPub. This guide describes the contract visible in [Misskey 2026.10.1](../../references/software/misskey.md), and identifies where a client must check server policy rather than rely on an endpoint name.

## Before you start

Use the version-pinned [endpoint registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts) as the inventory, and [generated OpenAPI service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/openapi/OpenApiServerService.ts) for machine-readable request schemas. A named endpoint being present does not imply that a specific user has permission or that the operator enables its feature. `[source]` 2026.10.1.

## Requests and authentication

The native interface maps endpoint names under `/api/`; most calls are POST requests carrying JSON, while GET is allowed only for endpoints declaring it. File endpoints have separate upload handling. The server registers endpoint metadata, parameter schemas, and methods in `ApiServerService`; the API call layer resolves authentication, checks permissions and executes the registered handler. `[source]` [route registration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/ApiServerService.ts), [API calls](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/ApiCallService.ts).

Applications can use MiAuth or the OAuth authorization-code flow. The OAuth provider requires the S256 proof-key challenge and validates the redirect URI against client metadata. API requests can supply a token as a bearer credential or through the legacy `i` parameter; prefer an Authorization header where supported so credentials do not become part of a URL. These details describe this release, not a guarantee that another Misskey-derived server supports identical flows. `[source]` [OAuth provider](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/oauth/OAuth2ProviderService.ts), [API call handling](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/ApiCallService.ts).

Each endpoint declares its own authentication and permission requirements. For example, the timeline endpoint is user-bound; a token with insufficient permissions is not interchangeable with one that can read account data. Rate limits vary by endpoint and are backed by Redis in the production path. Avoid a single global assumption about all endpoints. `[source]` [timeline](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoints/notes/timeline.ts), [rate limiter](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/RateLimiterService.ts).

## Notes, timelines and notifications

The registry includes note creation, deletion, timeline variants, conversations, mentions, reactions, poll voting and search, plus following, drive, notifications and administration endpoints. It lists no general `notes/edit` endpoint in this release; that does not imply every fork or later release has the same limitation. Note IDs are local API identifiers, whereas remote notes additionally have a network URI. `[source]` [registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts), [note model](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts).

The home timeline accepts ID and date boundaries including `sinceId` and `untilId`; depending on configuration it uses materialized Redis timelines with database fallback or SQL directly. It is a view subject to visibility and relationships, not proof of a globally complete history. Notifications are read from Redis streams and have separate read state. `[source]` [timeline endpoint](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoints/notes/timeline.ts), [notification service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts).

## Live updates and media

The streaming service multiplexes channels over a WebSocket and uses Redis Pub/Sub to distribute events. App-authenticated streaming requires the `read:account` permission in this release. Incoming WebSocket payloads are limited to 1 MiB and compression is disabled in the inspected service. A connection interruption can lose live events; a client should reconcile against the relevant HTTP endpoints after reconnecting. The recovery recommendation is an engineering judgment, not a measured guarantee. `[source]` [streaming server](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/StreamingApiServerService.ts).

Drive endpoints manage uploads and file metadata; media bytes can be stored locally or in object storage. Preserve sensitivity and alternative text where available, and wait for the actual endpoint result rather than assuming that an attached URL is safe to render. `[source]` [Drive service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/DriveService.ts).

## Technical details

This request is handwritten from the timeline endpoint's parameter schema and is **not executed**. The token and host are fictional. `limit` is an example, not a universal value for every endpoint.

```http
POST /api/notes/timeline HTTP/1.1
Host: social.example
Authorization: Bearer <redacted>
Content-Type: application/json

{"limit": 20}
```

Responses contain Misskey-native note entities, not Mastodon `Status` objects. A client should retain Misskey-specific fields such as reaction and renote information in its own model instead of flattening them prematurely. Treat remote text, URLs and media as untrusted; [Misskey-flavored markup](../../glossary.md#mfm) requires a renderer appropriate to the application. `[source]` [note serialization](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/entities/NoteEntityService.ts), [MFM handling](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/MfmService.ts).

## Pitfalls

- **Calling Mastodon endpoints against Misskey:** implement an explicit native adapter; isolated route-name overlap is not complete API compatibility.
- **Treating a token as universal permission:** request and check endpoint permissions and handle instance policies and token revocation.
- **Losing events on reconnect:** use the live stream for updates and reconcile from HTTP; do not infer durable delivery from a WebSocket message.
- **Assuming API pagination gives a complete network history:** remote notes may never have been delivered to this server, and visibility filters apply.

## Open questions

> Unknown: actual behavior of this release under token revocation during a live connection, and exact gaps after reconnection, need controlled tests. No live API or cross-server compatibility run is claimed here.

## Sources

- [Misskey 2026.10.1 endpoint registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts) — native API inventory.
- [API route registration and call handling](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/ApiServerService.ts) — request handling and method checks.
- [OAuth provider](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/oauth/OAuth2ProviderService.ts) — authorization code and proof key validation.
- [Timeline endpoint](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoints/notes/timeline.ts) and [streaming service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/StreamingApiServerService.ts) — pagination and live connections.

