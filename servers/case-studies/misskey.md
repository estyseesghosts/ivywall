# Misskey 2026.10.1

Misskey is a social server with its own web client, native client API, and federation code. A local post becomes a database record, may be inserted into many timeline lists, and may be sent to other servers in background jobs. An accepted network request is only the beginning of that process. This page follows [the pinned release](../../references/software/misskey.md); it does not claim behavior for forks or later versions.

For deeper implementation paths, see the [native client API](../../clients/apis/misskey.md), [federation pipeline](../federation-pipelines/misskey.md), and [storage and recovery](../storage/misskey.md).

## Architecture

The TypeScript backend uses Fastify for HTTP and NestJS services, with PostgreSQL for durable relational entities and Redis for job queues, timeline lists, notifications and messaging. Media bytes may reside on local or S3-compatible storage. In clustered mode the primary and workers can run different server and queue roles; deployment options affect the process layout. These are code paths, not a measured capacity claim. `[source]` [startup](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/boot/master.ts), [configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/.config/example.yml), [queue workers](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts).

## Key code paths

### Receiving an activity

An **[actor](../../glossary.md#actor)** is an account or service represented on the network. Other servers send activities to an actor's **[inbox](../../glossary.md#inbox)**. The ActivityPub route checks that federation is enabled, parses the HTTP signature, requires `host` and `digest` among signed headers, checks that the host matches its configured host, and verifies the SHA-256 digest against the raw request body. An absent actor is rejected. It then enqueues the activity and returns `202 Accepted`. `[source]` [`ActivityPubServerService.inbox`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts).

The queue worker resolves the signing key, checks federation policy and verifies the HTTP signature and the relationship between the signer and activity actor. It can fall back to a valid `RsaSignature2017` linked-data signature when the HTTP signature or signer check fails. If an activity has an ID, the worker checks its host against the signer. Failures can therefore occur *after* the 202 response. A 202 is not evidence of a persisted post or notification. `[source]` [`InboxProcessorService.process`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts).

`ApInboxService` dispatches recognized activity types. In a `Create` path, the server resolves the object, checks attribution and uses an object lock and existence checks before creating the remote note. A unique remote URI in the note model is another duplicate defense; this does not give every activity exactly-once semantics. Remote replies can require fetching a parent, so missing or inaccessible objects can prevent creation. `[source]` [dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [remote notes](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts), [note model](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts).

### Sending and retrying

A local note enters `NoteCreateService`, which persists it and performs downstream timeline and federation work. The renderer creates an ActivityStreams representation: a normal note becomes a `Create`; an eligible pure renote becomes an `Announce`. Delivery resolves inbox targets, can coalesce followers onto a shared inbox, and queues signed HTTP requests. A successful local write is not proof that remote servers received or applied it. `[source]` [note creation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NoteCreateService.ts), [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [delivery worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/DeliverProcessorService.ts).

Queue workers distinguish retryable failures from unrecoverable ones. The configured defaults are 128 concurrent delivery jobs and 16 inbox jobs per worker, with rate limits of 128 and 32 per second respectively. The retry function uses exponential backoff with jitter and an eight-hour base cap. These settings are not a global limit across multiple workers or a measured throughput. `[source]` [`QueueProcessorService`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts).

### Feeds and notifications

The note model stores local IDs, author and reply relationships, visibility, media IDs and a remote URI when applicable. Timeline fan-out can write note IDs into Redis lists; the timeline endpoint can use those lists with SQL fallback, or use SQL when fan-out is disabled. Notification records are written to Redis Streams with trimming, rather than simply inferred from PostgreSQL note rows. Backup and recovery plans must account for Redis persistence and the acceptable loss window. `[source]` [note model](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts), [timeline service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts), [timeline endpoint](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoints/notes/timeline.ts), [notification service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts).

## API coverage

The native API registers endpoint families for notes, accounts, following, notifications, media and administration. The endpoint registry includes `notes/create` and `notes/delete`; it does not list a general `notes/edit`. Streaming uses a WebSocket service. A client should discover and handle the features and permissions of this API rather than infer Mastodon API compatibility from the fact that both servers federate. `[source]` [endpoint registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts), [streaming service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/StreamingApiServerService.ts).

## Federation behaviour

| Incoming activity | Handling in this release |
| --- | --- |
| `Create` | Resolves supported post objects and attempts to create a local representation, subject to validation. |
| `Update` | Updates an actor or a `Question` poll; the dispatcher skips other object types, including ordinary `Note` edits. |
| `Delete` | Processes supported owned notes and actors; an actor delete triggers account cleanup. |
| `Follow`, `Accept`, `Reject` | Handles supported follow and follow-request cases, not arbitrary embedded activities. |
| `Like`, `Announce`, `Undo` | Maps supported interactions into local reaction, renote or reversal operations; behavior depends on object and existing state. |
| `Add`, `Remove`, `Move`, `Block`, `Flag` | Has specialized handlers, not general-purpose operations for every possible target. |

`[source]` The table summarizes [`ApInboxService`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts); it does not demonstrate interoperability with any particular peer.

Misskey represents emoji reactions using extensions to `Like`, exports quote information using multiple fields and an HTML link, and can include its own text format in addition to rendered HTML. Another implementation may ignore these extensions or preserve only part of the relationship; exact peer behavior needs a version-pinned test. Audience conversion uses `to` and `cc` to infer public, home, followers or specified visibility. `[source]` [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [audience conversion](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApAudienceService.ts).

### Audience, formatting and feature boundaries

Native note visibility is `public`, `home`, `followers` or `specified`; `localOnly` suppresses federation. The ActivityPub renderer places the Public URI in `to` for public notes and in `cc` for home notes, while followers-only notes target the followers collection. These are audience signals, not an enforceable erasure guarantee after a peer receives content. `[source]` [audience renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [note creation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NoteCreateService.ts).

`NoteEntityService.isVisibleForMe` includes a special assumption for a remote viewer and remote author when their relationship is not locally known. Its source explicitly says that the equivalent SQL visibility checks must remain synchronized. A server implementing different privacy assumptions should test this case rather than copy the assumption silently. `[source]` [visibility implementation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/entities/NoteEntityService.ts).

Misskey Flavored Markdown (MFM) can be carried as `_misskey_content` and `source` with `text/x.misskeymarkdown`, alongside rendered HTML. Import may convert HTML into an approximation when recognized source is unavailable; arbitrary formatting therefore cannot be assumed to round-trip losslessly. Local-only custom emoji are filtered out of ActivityPub emoji tags. `[source]` [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [remote note importer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts).

Channels, clips, antennas, chat, roles and user interface preferences are native product features; an ActivityPub representation of a post is not an export of all local collections or settings that contain it. Media metadata and bytes have separate lifecycles: `DriveService` handles storage and derivatives, while remote-file caching depends on deployment settings. `[source]` [API endpoint inventory](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts), [DriveService](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/DriveService.ts).

## Resource usage and tradeoffs

Memory, CPU, storage and network capacity are **unmeasured** here. Fan-out avoids reconstructing every feed solely at read time but can create work proportional to the recipients and lists involved; the source mechanism alone does not quantify its cost. Redis stores more than an expendable cache, so an operator should examine persistence and recovery behavior before treating it as disposable. `[source]` [fan-out implementation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts), [notification service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts).

## Technical details

Outbound HTTP requests use RSA-SHA256 signatures. GET requests sign `(request-target)`, `date`, and `host`; POST requests also sign `digest`. Key resolution and verification on receipt are separate from request parsing at the route. `[source]` [`ApRequestService`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRequestService.ts), [inbox worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts).

## Pitfalls and open questions

- A 202 response means queue acceptance, not successful signature verification or object creation. Inspect queue outcomes and resulting state.
- A remote `Update Note` is not a general note edit in this release; a cached remote post can remain stale.
- Exact replay-window enforcement and a persistent ledger of previously processed activity IDs have not been established by this audit. Do not infer them from signature verification or note URI deduplication.
- The bundled [federation tests](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/test-federation/README.md) describe a two-Misskey setup. A version-pinned cross-software test with captured requests and assertions is still needed for peer compatibility claims.

## Sources

- [Misskey 2026.10.1 source tree](https://github.com/misskey-dev/misskey/tree/4840fa6d576128ba916ba69169258ca177d40faf) — implementation and configuration studied above.
- [ActivityPub Recommendation](https://www.w3.org/TR/activitypub/) — protocol context; it does not itself establish Misskey conformance.
- [Misskey federation test setup](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/test-federation/README.md) — scope and setup of upstream tests.
