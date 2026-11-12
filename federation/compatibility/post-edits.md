# Compatibility: post edits

Editing a post can change what a remote reader sees after the original post has already been delivered. Whether that change arrives and is applied depends on the receiving server's `Update` handling. [Mastodon 4.7.3](../../references/software/mastodon.md) and [Misskey 2026.10.1](../../references/software/misskey.md) have materially different handling of ordinary note edits; these are source-level findings, not a live test result.

## Summary

| Software | Version | Emits | Accepts | Notes |
| -------- | ------- | ----- | ------- | ----- |
| Mastodon | 4.7.3 | native | native | Local edits create snapshots and queue a federation update; incoming supported status updates pass through ownership and age checks. `[source]` [edit service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/update_status_service.rb), [update handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/update.rb). |
| Misskey | 2026.10.1 | untested | ignored | The inbound dispatcher handles actors and `Question` updates but skips other resolved object types, including ordinary `Note`; no general `notes/edit` endpoint appears in the endpoint registry. `[source]` [dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [endpoint registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts). |

Values are defined in the [glossary](../../glossary.md#compatibility-values).

## Information lost in translation

A Mastodon edit can leave an already imported ordinary note unchanged on Misskey when its inbound dispatcher skips the `Update`. This is a source-derived implication; delivery timing, later re-fetching and client caches have not been tested here. Even if an update succeeds, a single current representation is not evidence that every previous edit or deletion was replicated. `[source]` [Misskey dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [Mastodon update service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/update_status_service.rb).

## Technical details

Mastodon's local edit service snapshots the previous and new versions inside a transaction, then queues local distribution and `ActivityPub::StatusUpdateDistributionWorker`. Its inbound `Update` handler matches the object's host to the actor, locates a status belonging to that actor, and invokes status-update processing. If the object is unknown, the handler can attempt a Create path for an out-of-order update, but skips old unknown objects and unknown objects from suspended accounts. `[source]` [edit service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/update_status_service.rb), [incoming update](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/update.rb).

Misskey resolves the incoming object and first verifies the activity actor matches the remote actor. It updates actors or `Question` objects, returning a skip result for other types. A `Question` may have its own edit behavior and must be tested separately. `[source]` [ApInboxService.update](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts).

## Test procedure

No live interoperability result is claimed. On isolated pinned instances, follow a fixture account, publish a public text-only note on Mastodon, wait until the original is visible on Misskey, and edit it. Capture the `Update` activity and HTTP acknowledgment, wait for the receiving queue to drain, then inspect the remote stored post and API response. Repeat with a poll, an update delivered before the original, a temporary delivery failure and a later refetch. Record both the state and timing: a 202 acknowledgment does not establish that the edit was applied.

## Sources

- [Mastodon 4.7.3 edit service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/update_status_service.rb) and [incoming update handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/update.rb) — local edits, queueing and incoming checks.
- [Misskey 2026.10.1 inbox dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts) and [endpoint registry](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/api/endpoint-list.ts) — incoming update types and registered client endpoints.
