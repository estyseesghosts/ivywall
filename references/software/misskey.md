# Misskey fact sheet

**Studied release:** Misskey 2026.10.1, commit [`4840fa6d576128ba916ba69169258ca177d40faf`](https://github.com/misskey-dev/misskey/tree/4840fa6d576128ba916ba69169258ca177d40faf). The commit timestamp is 2026-10-23; the precise release publication date has not been independently verified. This is a source study, not an interoperability test.

## Facts

| Fact | Value and evidence |
| ---- | ------------------ |
| Server | TypeScript backend with NestJS and Fastify. [source: backend dependencies](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/package.json) |
| Persistence | PostgreSQL through TypeORM; Redis is also used for queues, timelines and notification streams. [source: PostgreSQL configuration](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/postgres.ts), [timeline](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts), [notifications](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/NotificationService.ts) |
| Client API | Misskey-native `/api/` endpoints and WebSocket streaming; endpoint presence is not Mastodon API parity. [source: endpoint registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts) |
| Federation | ActivityPub, WebFinger, NodeInfo and HTTP signatures. [source: ActivityPub routes](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts), [discovery](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/WellKnownServerService.ts) |
| Inbox acknowledgment | Header and digest checks precede queueing and HTTP 202; signature verification and activity processing happen later. [source: inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts), [worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts) |
| Post updates | Incoming `Update` dispatch handles actors and `Question` polls, not general `Note` edits. [source: `ApInboxService.update`](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts) |

## Technical details

See the [Misskey case study](../../servers/case-studies/misskey.md) for the request and queue path, data model, limits and unresolved questions. The [federation document mirror](../federation-docs/misskey.md) describes a different checkout and is not evidence that all of its claims apply to this pinned release.

## Sources

- [Misskey 2026.10.1 source tree](https://github.com/misskey-dev/misskey/tree/4840fa6d576128ba916ba69169258ca177d40faf) — pinned implementation used for this fact sheet.
- [Misskey releases](https://github.com/misskey-dev/misskey/releases) — release history; exact publication date still needs verification.
