# Mastodon 4.7.3 storage and recovery

A Mastodon server stores durable social data, queued work, cached timelines and media in different systems. Recovering only the SQL database can bring accounts and posts back while leaving media, work in flight or encryption keys unavailable. This page maps those boundaries in [Mastodon 4.7.3](../../references/software/mastodon.md); it is not a tested backup procedure for every deployment.

## Before you start

Inventory the database, Redis, local or object storage, secrets, optional search index and worker configuration for the particular instance. Test recovery in isolation against a representative backup; source inspection is not evidence of a successful restore. The [case study](../case-studies/mastodon.md) describes the service architecture. `[source]` [deployment configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/docker-compose.yml).

## Understand each store

| Store | Role in 4.7.3 | Recovery implication |
| --- | --- | --- |
| PostgreSQL | Account, status, follow, notification and media metadata are represented by relational records. `[source]` [account](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/account.rb), [status](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/status.rb), [follow](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/follow.rb) | Back up and restore consistently; data lost from the primary store is not recreated by rebuilding feeds. |
| Redis | Background jobs and retry state, feed data and transient coordination depend on Redis. `[source]` [feed manager](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/feed_manager.rb), [worker configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/sidekiq.yml) | Rebuilding a cache is different from recovering queued deliveries. Decide explicitly whether loss of in-flight work is acceptable. |
| Media storage | Attachment metadata and files have separate lifecycles. `[source]` [media model](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/media_attachment.rb) | Preserve local uploads and object-storage configuration together with the database. A remote cached file may be unavailable for refetch. |
| Search index | Optional indexed search is derived from records. `[source]` [search configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/initializers/chewy.rb) | Verify the reindex procedure and its cost for the installation; index recovery is not database recovery. |
| Encryption secrets | Local keypair material uses encrypted fields. `[source]` [keypair](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/keypair.rb), [encryption configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/initializers/active_record_encryption.rb) | Preserve the matching encryption configuration securely; a database dump alone may not recover usable signing keys. |

## IDs, feeds and consistency

A remote actor and a local login are distinct concepts: an account record can represent an actor without representing a local user. A status has a local database identifier; remote objects additionally need a stable network URI. Boosts, replies, follows, polls and quotes have their own relationships rather than all being plain text. `[source]` [account](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/account.rb), [status](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/status.rb), [quote](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/quote.rb).

Home and list feed entries are maintained in Redis. In this release `FeedManager::MAX_ITEMS` is 800 and `REBLOG_FALLOFF` is 80; the latter controls boost aggregation behavior. The feed reader paginates stored IDs and retrieves status records; a bounded home feed is not an unlimited historical query over every followed account. `[source]` [feed manager](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/feed_manager.rb), [feed reader](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/feed.rb).

Conversation reconstruction is best effort over objects the server knows or can fetch; it cannot prove the absence of replies on other servers. Remote objects, media and timeline entries can arrive or disappear at different times. `[source]` [reply fetching](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_all_replies_service.rb), [remote status fetching](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_status_service.rb).

## Technical details

Mastodon includes a feed maintenance command that rebuilds home and list feeds. This is a recovery tool for derived feed state, not a substitute for a database or media backup. The command's flags, runtime and impact should be checked against the installed version before use. `[source]` [feeds CLI](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/lib/mastodon/cli/feeds.rb).

Remote-media cleanup and retention are separate from local media durability. The vacuum implementation has an orphan-cleanup path and configurable remote-media retention; check the applicable settings and source before assuming a remote file can be fetched again. `[source]` [media vacuum](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/vacuum/media_attachments_vacuum.rb).

## Pitfalls and open questions

A SQL restore without its matching keys or media may appear successful while leaving posts, attachments or signatures unusable. Restoring a Redis snapshot independently of the database can also replay stale jobs; a recovery plan should define consistency and whether queued effects can be repeated. These are engineering risks, not measured restore outcomes. No restore time, storage footprint, production query ranking or throughput has been measured here.

## Sources

- [Mastodon 4.7.3 account and status models](https://github.com/mastodon/mastodon/tree/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models) — relational entities.
- [Feed manager](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/feed_manager.rb) and [feeds CLI](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/lib/mastodon/cli/feeds.rb) — feed limits and maintenance.
- [Keypair](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/keypair.rb) and [encryption configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/initializers/active_record_encryption.rb) — key storage.
- [Media vacuum](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/vacuum/media_attachments_vacuum.rb) — remote and orphaned media cleanup.
