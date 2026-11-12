# NodeBB 4.16.7

NodeBB is a forum server with topics, replies, categories and plugins. Its federation layer maps that forum model onto ActivityPub, including category `Group` actors; it does not store every incoming activity as a generic ActivityStreams log. This source study concerns [NodeBB 4.16.7](../../references/software/nodebb.md), not other releases or a live interoperability test.

## Architecture

The backend is JavaScript on Node.js, with Express routes, Socket.IO updates and a plugin system. Separate modules implement users, topics, posts, permissions and ActivityPub. Database adapters expose an object, set and sorted-set interface over Redis, MongoDB or PostgreSQL. Cache, sessions, pub/sub, uploads and federation jobs have their own persistence and deployment needs. `[source]` [runtime dependencies](https://github.com/NodeBB/NodeBB/blob/v4.16.7/install/package.json), [database selector](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/database/index.js), [startup](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/start.js), [pub/sub](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/pubsub.js).

MongoDB and PostgreSQL emulate the key-oriented interface rather than exposing an identical domain-normalized schema. PostgreSQL's adapter includes `legacy_hash`, `legacy_zset`, `legacy_set`, `legacy_list` and related structures; a sorted set's key, score and value are explicit storage fields. Backup and performance characteristics must be measured for the chosen backend, not inferred to be identical. `[source]` [PostgreSQL adapter](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/database/postgres.js), [Mongo adapter](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/database/mongo.js).

## Key code paths

### Receiving and mapping federation

1. ActivityPub routes select the instance, user or category inbox. Middleware verifies signed POSTs, resolves the signing key's owner, checks actor/origin consistency, filters policy and checks required fields. `[source]` [routes](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/activitypub.js), [middleware](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/middleware/activitypub.js).
2. The controller invokes a per-activity plugin hook and dispatches to a handler. A public `Create` can be normalized into a topic and post after author, recipient, relation and permissions checks; private notes have a separate mapping. Unsupported activity types do not become automatically supported just because they are valid ActivityStreams. `[source]` [controller](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/controllers/activitypub/index.js), [inbox](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/inbox.js).
3. Remote thread assertion checks context and parent relationships, can fetch missing ancestors, and avoids re-creating known posts. Access restrictions, blocked domains, network failures or traversal bounds can leave a conversation incomplete. `[source]` [remote note logic](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/notes.js), [context traversal](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/contexts.js).

### Outgoing delivery

Local forum actions build activities and recipients; remote actors can advertise shared inboxes, and final destinations are deduplicated. A database-backed retry queue stores activity deliveries; the send pool selects due jobs and workers sign HTTP requests. In this release the sender attempts RFC 9421 first and falls back to the older signature draft on failure. A local post or queued item is not proof of remote acceptance. `[source]` [outgoing activities](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/out.js), [enqueue](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/index.js), [send pool](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/send.js), [HTTP worker](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/sendWorker.js).

### Storage and identity

Local users, posts and categories have local numeric identifiers; remote actors and post objects use their ActivityPub URIs in keys and references. Topic/post structures and sorted sets support discussion order, while cached remote actors hold discovery and key data. For example, the retry queue uses `ap:retry:queue` and keyed payload objects. These examples are not a complete schema or a cross-backend transactional guarantee. `[source]` [actor implementation](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/actors.js), [post assertion](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/notes.js), [enqueue](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/index.js).

## API coverage

NodeBB provides its own read and write APIs and an interactive Socket.IO client. ActivityPub federation is server-to-server; the ActivityPub controller returns 405 for its client inbox GET path. Do not assume its endpoints provide full Mastodon REST or ActivityPub client-to-server compatibility. `[source]` [write API router](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/write/index.js), [ActivityPub controller](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/controllers/activitypub/index.js), [Socket.IO](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/socket.io/index.js).

## Federation behaviour

NodeBB presents local users and categories as actors, maps category participation onto forum permissions and supports WebFinger and NodeInfo discovery. It recognizes several remote post types, including `Note`, `Article`, `Page`, `Question` and `Video`, but type recognition is not proof that every field survives conversion into a forum post. Remote lookup checks the actor and WebFinger backreference, including split domains. `[source]` [actor resolver](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/actors.js), [object projection](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/notes.js), [well-known routes](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/well-known.js).

The signature module verifies both RFC 9421 and draft HTTP signatures and handles digest and timing validation. Domain blocking, actor binding, category privileges and filtering are distinct checks; a cryptographically valid request is not automatically authorized to mutate every target. `[source]` [signatures](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/signatures.js), [middleware](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/middleware/activitypub.js), [instance policy](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/instances.js).

## Resource usage and tradeoffs

No CPU, memory, delivery-throughput or database-size benchmark has been run for this study. Distinct inboxes, context traversal, topic size, rendering and backend-specific sorted-set operations are plausible workload dimensions; benchmark them with the chosen database and plugin configuration. A backup plan must include the database, uploads, configuration, secrets and plugin versions; verify a restore on an isolated instance before upgrading. `[source]` [upgrade process](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/upgrade.js), [upload handling](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/file.js).

## Strengths, known risks and tradeoffs

The forum model brings categories, privileges and threaded views to federation, but translating remote objects can lose properties and the mapping depends on local permissions. The plugin hooks make modification possible but can change an operator's effective behavior. The short activity-ID deduplication window is not a durable exactly-once ledger. `[source]` [middleware](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/middleware/activitypub.js), [plugin-capable controller](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/controllers/activitypub/index.js).

A source-review concern is that the send queue ID is based on actor and destination rather than the activity ID. `[hypothesis]` Different activities queued to one actor/destination could overwrite one another before delivery; reproduce with a paused sender, inspect queued payloads and compare final peer state before calling this a demonstrated loss. Another review target is multiple job-runner processes: in-flight tracking uses process-local state. `[source]` [enqueue](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/index.js), [send pool](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/send.js).

## Technical details

Public federation routes include `/inbox`, `/uid/:uid`, `/category/:cid`, and their relevant actor endpoints. A single inbox delivery can produce permission checks, actor resolution, post creation, notifications and subsequent Group announcements; not every incoming operation traverses the same path. Route, object and handler behavior are pinned to this version. `[source]` [routes](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/activitypub.js), [inbox handlers](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/inbox.js).

Test next: capture duplicate `Create` and `Undo`, concurrent distinct activities for the same destination, backfill with missing/private ancestors, and interrupted queue recovery. Record the exact tag, backend, plugin set, payload IDs and final state; none of these scenarios is claimed as observed here.

## Sources

- [NodeBB 4.16.7 source](https://github.com/NodeBB/NodeBB/tree/v4.16.7) — tagged architecture, database adapters and federation implementation.
- [ActivityPub inbox](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/inbox.js), [middleware](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/middleware/activitypub.js) and [notes](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/notes.js) — authentication, activity handling and thread mapping.
- [Delivery enqueue](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/index.js) and [send pool](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/send.js) — recipients, queued work and review targets.
