# Misskey 2026.10.1

Misskey is a social server with its own web client, native client API, and federation code. A local post becomes a database record, may be inserted into many timeline lists, and may be sent to other servers in background jobs. An accepted network request is only the beginning of that process. This page follows [the pinned release](../../references/software/misskey.md); it does not claim behavior for forks or later versions.

For deeper implementation paths, see the [native client API](../../clients/apis/misskey.md), [federation pipeline](../federation-pipelines/misskey.md), and [storage and recovery](../storage/misskey.md).

## Architecture

The TypeScript backend uses Fastify for HTTP and NestJS services, with PostgreSQL for durable relational entities and Redis for job queues, timeline lists, notifications and messaging. Media bytes may reside on local or S3-compatible storage. In clustered mode the primary and workers can run different server and queue roles; deployment options affect the process layout. These are code paths, not a measured capacity claim. `[source]` [startup](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/boot/master.ts), [configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/.config/example.yml), [queue workers](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts).

## Key code paths

### Receiving and sending

Inbox checks, the queue worker, dispatch, note creation and delivery with retries are traced step by step on the [federation pipeline](../federation-pipelines/misskey.md) page. In short: the route checks the signature headers, host and digest and returns `202`; the queue verifies the key and signer later, so failures can follow the acknowledgement. `[source]` [`ActivityPubServerService.inbox`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts), [`InboxProcessorService.process`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts).

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

`[source]` The table summarizes [`ApInboxService`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts#L93); it does not demonstrate interoperability with any particular peer.

Misskey represents emoji reactions using extensions to `Like`, exports quote information using multiple fields and an HTML link, and can include its own text format in addition to rendered HTML. Another implementation may ignore these extensions or preserve only part of the relationship; exact peer behavior needs a version-pinned test. Audience conversion uses `to` and `cc` to infer public, home, followers or specified visibility. `[source]` [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [audience conversion](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApAudienceService.ts).

### Audience, formatting and feature boundaries

Visibility mapping to `to`/`cc`, MFM handling and the extension terms are in the [Misskey federation document](../../references/federation-docs/misskey.md) (a later development snapshot); `localOnly` notes are not federated, and audience signals are not an enforceable erasure guarantee after a peer receives content.

`NoteEntityService.isVisibleForMe` includes a special assumption for a remote viewer and remote author when their relationship is not locally known. Its source explicitly says that the equivalent SQL visibility checks must remain synchronized. A server implementing different privacy assumptions should test this case rather than copy the assumption silently. `[source]` [visibility implementation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/entities/NoteEntityService.ts).

Channels, clips, antennas, chat, roles and user interface preferences are native product features; an ActivityPub representation of a post is not an export of all local collections or settings that contain it. Media metadata and bytes have separate lifecycles: `DriveService` handles storage and derivatives, while remote-file caching depends on deployment settings. `[source]` [API endpoint inventory](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts), [DriveService](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/DriveService.ts).

## Resource usage and tradeoffs

Memory, CPU, storage and network capacity are **unmeasured** here. Fan-out avoids reconstructing every feed solely at read time but can create work proportional to the recipients and lists involved; the source mechanism alone does not quantify its cost. Redis stores more than an expendable cache, so an operator should examine persistence and recovery behavior before treating it as disposable. `[source]` [fan-out implementation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts), [notification service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts).

## Technical details

Signing, queue limits and retry behaviour are on the [federation pipeline](../federation-pipelines/misskey.md) page; storage and recovery are on the [storage](../storage/misskey.md) page.

## Pitfalls and open questions

- A remote `Update Note` is not a general note edit in this release; a cached remote post can remain stale.
- Exact replay-window enforcement and a persistent ledger of previously processed activity IDs have not been established by this audit. Do not infer them from signature verification or note URI deduplication.
- The bundled [federation tests](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/test-federation/README.md) describe a two-Misskey setup. A version-pinned cross-software test with captured requests and assertions is still needed for peer compatibility claims.

## Sources

- [Misskey 2026.10.1 source tree](https://github.com/misskey-dev/misskey/tree/4840fa6d576128ba916ba69169258ca177d40faf) — implementation and configuration studied above.
- [ActivityPub Recommendation](https://www.w3.org/TR/activitypub/) — protocol context; it does not itself establish Misskey conformance.
- [Misskey federation test setup](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/test-federation/README.md) — scope and setup of upstream tests.
