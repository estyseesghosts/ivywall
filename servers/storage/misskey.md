# Misskey storage, timelines and recovery

Misskey's durable social graph and notes are stored in PostgreSQL, but Redis also carries queue state, materialized timelines and recent notification data. This matters when designing backups: restoring a database alone may restore accounts and notes while leaving other user-visible state missing. This page follows [Misskey 2026.10.1](../../references/software/misskey.md); it does not claim a tested restore procedure or measured capacity.

## Before you start

Understand which stores the deployment uses, their persistence settings and the accepted loss window. The sample configuration identifies PostgreSQL, Redis, optional object storage, fan-out and other operational settings. `[source]` [configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/.config/example.yml), [database initialization](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/postgres.ts).

## Store identities and social objects

A local user has a null `host`; a remote user has a host and network URI. A local note's `uri` is null, whereas a remote note has its ActivityPub URI and an internal local ID. This separation lets the application use local IDs in joins and API pagination while it finds a federated object by URI. The remote note URI has a uniqueness constraint; the following table has a unique follower/followee pair. `[source]` [user](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/User.ts), [note](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts), [following](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Following.ts).

The note stores reply and renote links, visibility and recipient data, content warning, attachments, tags and denormalized reaction counts. Following and individual reactions have their own relationship records. These are domain objects: receiving an activity usually changes application state; it is not evidence of a complete immutable activity log. `[source]` [note entity](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts), [reaction entity](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/NoteReaction.ts).

## Read feeds and notifications

Timeline fan-out writes IDs into Redis lists for multiple views. The home timeline can read those lists with SQL fallback or use SQL when fan-out is disabled. Replies use stored note relationships, while follows use indexed edges. Neither strategy proves that all remote activity has reached this server. `[source]` [fan-out](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts), [timeline endpoint](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoints/notes/timeline.ts).

Notification payloads are stored in Redis streams with trimming, alongside separate read markers; live delivery uses Pub/Sub. Thus Redis is not merely a disposable acceleration layer in this release. Whether a particular notification can be reconstructed after loss has not been established here. `[source]` [notification implementation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts), [notification types](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Notification.ts).

## Technical details

| Store | Examples in 2026.10.1 | Recovery implication |
| --- | --- | --- |
| PostgreSQL | Users, notes, follow and reaction edges, file metadata, migrations | Preserve a consistent database snapshot and verify migrations. |
| Redis | BullMQ jobs, feed lists, notification streams and read markers, Pub/Sub | Configure persistence and recovery to match the desired queue and notification loss window. Pub/Sub itself is not an archive. |
| Local or S3-compatible storage | Media bytes and derivatives, depending on configuration | Capture the actual media store and its corresponding configuration; metadata alone is insufficient to restore bytes. |

`[source]` [PostgreSQL configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/postgres.ts), [queues](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/QueueService.ts), [Drive service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/DriveService.ts).

As an operational design recommendation, inventory database, Redis, media, secrets and configuration together; test restoration into an isolated deployment with the same software version before relying on the backup. Coordinating snapshots and deciding whether queued work should be replayed require deployment-specific procedures. No crash-consistency or restore test was performed for this page.

## Pitfalls

- **Backup only PostgreSQL:** notification and queue state may have a different loss window. Decide explicitly whether to preserve or accept that loss.
- **Assume indexes prove a query is fast:** inspect actual plans and production-shaped data; the presence of an index is not a benchmark.
- **Confuse a URI with an API ID:** use the mapping stored for a remote object and do not use one instance's local ID as a global identifier.
- **Assume every asynchronous side effect is atomic with a note write:** trace the Redis, queue and database boundaries under failure before designing replay or repair.

## Open questions

> Unknown: memory, disk and throughput at representative sizes, exact recovery after a crash between PostgreSQL and Redis operations, and the completeness of reconstructed notifications. These require measured workload and restore tests.

## Sources

- [Misskey 2026.10.1 note](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Note.ts), [user](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/User.ts) and [following](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/Following.ts) entities — object identities and relationships.
- [Timeline implementation](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts) and [notification service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts) — Redis data structures and read paths.
- [PostgreSQL configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/postgres.ts) and [sample configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/.config/example.yml) — migrations and operational settings.
