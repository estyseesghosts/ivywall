# Lemmy 0.19.21

Lemmy is a federated discussion server organized around communities, posts, nested comments and votes. Its community-oriented model changes how federation is routed: a community is an actor that can redistribute activity to its followers. This study follows [0.19.21 at its pinned commit](../../references/software/lemmy.md), not later 1.0 development. Code analysis does not establish a live compatibility result or a capacity benchmark.

## Architecture

The backend is a Rust workspace using Actix Web, Tokio, Diesel and PostgreSQL. Its standard web frontend is a separate `lemmy-ui` service; pict-rs handles image processing and storage. Federation processing uses the `activitypub-federation` library and Lemmy-specific object and activity mappings. `[source]` [workspace manifest](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/Cargo.toml), [server assembly](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/src/lib.rs), [ActivityPub integration](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/lib.rs).

PostgreSQL stores communities, accounts, posts, comments, relationships, votes, activity records and federation queue state. Database views combine base rows and aggregates for client responses. The design's query plans, index coverage and contention require measurement on the actual data distribution; precomputed counts alone do not prove a query is cheap. `[source]` [schema](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/db_schema/src/schema.rs), [post views](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/db_views/src/post_view.rs).

## Key code paths

### Incoming community activity

A peer sends ActivityPub JSON to an inbox; the integration delegates transport signature verification to the federation library and applies activity-specific authorization. The incoming enums distinguish shared, person and group activities; a community `Announce` can wrap an activity that is then dispatched. Handler-specific checks involve actor and object origins, community, bans and moderator authority. A valid signature identifies a key holder; it does not by itself authorize a moderation action. `[source]` [HTTP integration](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/http/mod.rs), [activity variants](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activity_lists.rs), [community announce](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activities/community/announce.rs).

A `Create` or `Update` of a supported post object is checked and mapped to a relational post. A comment's `inReplyTo` chain can require dereferencing missing parents, within fetch and depth limits. A server's incomplete view of a thread is not proof that no other replies exist. `[source]` [post handler](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activities/create_or_update/post.rs), [comment object](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/objects/comment.rs), [note protocol](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/protocol/objects/note.rs).

### Outgoing activity and queue

A local post API handler validates and persists the post, then submits activity work for federation. The federation sender records outgoing activity and recipient selection in PostgreSQL; destination workers group recipient inboxes, send and track per-instance progress. Source reading does not establish an atomic transactional outbox across the initial API write and every later activity insertion, so a crash at a boundary deserves explicit testing. `[source]` [post creation](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/api_crud/src/post/create.rs), [activity submission](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/api_common/src/send_activity.rs), [federation worker](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/federate/src/worker.rs).

The per-destination sender can complete requests out of order while preserving progress bookkeeping; retries and checkpoints mean a crash may result in repeat sends. Duplicate activity IDs have database handling, but that does not make different IDs targeting the same object an exactly-once mutation. `[source]` [worker](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/federate/src/worker.rs), [received activity persistence](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/db_schema/src/impls/activity.rs), [inbox selection](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/federate/src/inboxes.rs).

## API coverage

The backend routes expose the Lemmy-specific `/api/v3` API, with endpoints for posts, comments, communities, accounts and moderation; a client should use those contracts rather than infer a full Mastodon-compatible API from ActivityPub support. Authenticated remote-object resolution can trigger network fetching, whereas anonymous lookups are constrained to local knowledge. `[source]` [HTTP routes](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/src/api_routes_http.rs), [object resolution](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/api/resolve_object.rs).

## Federation behaviour

| Model | Representation and boundary in 0.19.21 |
| --- | --- |
| User and community | `Person` and `Group`; local-only communities are a separate non-federated visibility mode. |
| Post and comment | Post as `Page`; comment as `Note` with a parent. The post parser recognizes other object types, but normalization is not lossless preservation of their native semantics. |
| Votes | `Like` and `Dislike` represent votes, with downvotes subject to server settings. |
| Community distribution | Community `Announce` is a distribution operation, not automatically a personal microblog boost. The code includes compatibility forms for post announcements. |
| Private messages | A `ChatMessage` path exists; routing and access policy do not constitute end-to-end encryption. |

`[source]` [community](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/objects/community.rs), [post wire type](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/protocol/objects/page.rs), [activity variants](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activity_lists.rs), [private message](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activities/create_or_update/private_message.rs). No comprehensive FEP conformance or cross-peer result is claimed.

## Operations and security

Migrations are embedded Diesel migrations, and replaceable database functions/triggers are maintained alongside them. Backups should cover PostgreSQL, configuration/secrets and pict-rs data; restoring only the database can leave media references unresolved. Verify restoration of federation queue checkpoints as well as content. This is an operational recommendation derived from the storage boundaries, not an automatic cross-service snapshot. `[source]` [schema setup](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/db_schema/src/schema_setup.rs), [image routes](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/routes/src/images.rs).

The 0.19.21 upstream release describes fixes for federation authorization, server-side request forgery and TLS validation, and states that this release adds no migrations. Historical flaws and their fixes are reasons to test the exact version and upgrade path, not evidence that all authorization or fetch risks are eliminated. `[documented]` [0.19.21 release](https://join-lemmy.org/news/2026-10-26_-_Lemmy_Release_v0.19.21_-_Security_Fixes).

## Resource usage and tradeoffs

Memory, CPU, storage and delivery throughput are **unmeasured** here. Destination-specific sending and shared inbox grouping can reduce redundant network work, but database queries, post ranking, image processing and large communities remain distinct workloads. The cost and scaling limits need measured query plans, queue age, destination count and failure tests on representative hardware.

## Technical details and open questions

Test duplicate deliveries, out-of-order edits/deletes, invalid moderator authority, missing ancestors, alternate object types and remote URL redirects with isolated instances. Confirm actual signature-library canonicalization and key rollover behavior against the locked dependency; this page does not infer them from the existence of HTTP signature support.

## Sources

- [Lemmy 0.19.21 source tree](https://github.com/LemmyNet/lemmy/tree/2ff971f205880f2638d5ce8dd979063dbd1dd6da) — exact studied implementation.
- [Activity dispatcher](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activity_lists.rs) and [community announce](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activities/community/announce.rs) — community federation.
- [Federation worker](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/federate/src/worker.rs) — delivery and checkpoints.
- [0.19.21 release announcement](https://join-lemmy.org/news/2026-10-26_-_Lemmy_Release_v0.19.21_-_Security_Fixes) — security changes and migration note.
