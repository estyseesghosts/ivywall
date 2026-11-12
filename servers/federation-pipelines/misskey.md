# Misskey federation pipeline

A federated request to Misskey goes through a short HTTP validation path and then a background processing path. The HTTP acknowledgement is therefore not proof that a post was stored or displayed. Outgoing posts take the reverse path: Misskey persists local state, renders an activity, chooses remote destinations and queues signed requests. This page traces [Misskey 2026.10.1](../../references/software/misskey.md), not a universal ActivityPub implementation.

## Before you start

Read the [ActivityPub server-to-server contract](../../fundamentals/activitypub-s2s.md) for the protocol distinction between actors, objects and activities. An **[inbox](../../glossary.md#inbox)** is an activity delivery endpoint; this page's behavior is grounded in the 2026.10.1 source and has not been reproduced against a live peer.

## Incoming requests

1. A peer POSTs to the shared inbox or a user inbox. The route limits the body to 64 KiB, checks signature metadata and required signed headers, compares the host, checks the digest against the raw body and requires an activity actor. It enqueues work and returns `202`; cryptographic verification and domain effects occur later. `[source]` [inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts#L109).
2. The inbox worker checks federation policy, resolves key material and verifies the HTTP signature and its relationship to the activity actor. It can use `RsaSignature2017` linked-data signature verification as a fallback for supported relayed activities. The activity ID host is checked against the relevant actor. A failure here can follow a 202 acknowledgement. `[source]` [inbox worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts#L66).
3. The dispatcher handles supported types. For a post creation it resolves the object, checks ownership and audience, uses a URI lock and checks for an existing note. The remote-note service resolves ancestors, content, attachments, mentions and polls before calling normal note creation. A missing or inaccessible parent can prevent or delay a reply's creation. `[source]` [dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts#L93), [remote note](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts).
4. Note creation can persist the result, fan it out to eligible timelines, and cause notifications or stream updates. Exactly which effects occur depends on activity type, visibility, relationships and local policy. A URI uniqueness constraint and duplicate checks help avoid duplicate notes; they are not a general exactly-once guarantee. `[source]` [note creation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NoteCreateService.ts#L443), [note model](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts).

## Outbound delivery

A local note is saved by `NoteCreateService` and rendered as a `Create` or, for an eligible pure renote, an `Announce`. Recipient selection includes followers and direct recipients; shared inbox URLs can coalesce delivery to multiple recipients at a remote host. The queue serializes the activity and digest and schedules delivery jobs. A worker signs and sends each request, then classifies failures for retry or permanent failure. `[source]` [note creation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NoteCreateService.ts#L443), [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [queue](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/QueueService.ts), [delivery worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/DeliverProcessorService.ts#L53).

Outbound HTTP signatures use RSA-SHA256. The request creator signs `(request-target)`, `date` and `host` for GET and includes `digest` for POST. A key's association with the activity actor is essential to the receiver's authorization decision; a valid transport signature alone does not establish authorization for arbitrary embedded content. `[source]` [request signing](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRequestService.ts), [inbox worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts#L66).

## Technical details

The default outbound delivery attempt limit is 12; inbox processing defaults to eight attempts. Queue worker defaults are 128 concurrent delivery jobs and 16 inbox jobs, subject to configuration. The backoff function grows exponentially, caps the base delay at eight hours and adds jitter. These are per-worker configuration defaults, not a global capacity or a service-level delivery guarantee. `[source]` [queue defaults](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/QueueService.ts), [worker configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts).

| Incoming activity | Scope in the dispatcher |
| --- | --- |
| `Create` | Resolve and import supported post objects after attribution and ownership checks. |
| `Update` | Handle actor updates and `Question` poll updates; ordinary `Note` edits are not processed as general post updates. |
| `Delete` | Delete a supported note owned by the actor or process an actor deletion. |
| `Follow`, `Accept`, `Reject` | Handle follows and supported follow responses; not arbitrary activity acceptance. |
| `Like`, `Announce`, `Undo` | Translate recognized interactions and reversals into local operations. |
| `Add`, `Remove`, `Move`, `Block`, `Flag` | Specialized handlers; the presence of a handler does not imply support for every target. |

`[source]` [incoming dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts#L93). This is an implementation inventory, not a cross-server test matrix.

## Pitfalls

- **Treating 202 as a completed delivery:** inspect worker failures, signature checks, policy and actual resulting state.
- **Assuming messages are ordered:** retries and missing dependencies can produce a different order from their creation; test updates and deletes against absent objects.
- **Assuming retries are unlimited:** worker and job settings bound attempts; permanent errors can stop retrying.
- **Treating a deduplicated note as universal replay protection:** other activity types have their own state checks. The examined paths do not establish a complete persistent replay ledger or a verified maximum signature age.
- **Overstating post edit support:** in this release `Update` of a `Note` is skipped by the dispatcher, although actor and poll updates have paths.

## Open questions

> Unknown: end-to-end latency, retry outcomes under an actual remote outage, and exact cross-server behavior for each activity require captured traffic and controlled multi-server tests. No such test has been run for this page.

## Sources

- [Inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts#L109) and [inbox worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts#L66) — staged input validation and authentication.
- [Incoming dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts#L93) and [remote note service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts) — activity handling and resolution.
- [Queue service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/QueueService.ts) and [queue processor](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts) — attempt limits, concurrency and backoff.
- [Delivery worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/DeliverProcessorService.ts#L53) and [request signer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRequestService.ts) — outbound delivery and signing.
