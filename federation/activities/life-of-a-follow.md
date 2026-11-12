# Life of a remote follow

A follow across servers starts as a request, not proof that posts will arrive. The target may require approval, reject it, or accept it while delivery fails later. This page traces the source paths for [Mastodon 4.7.3](../../references/software/mastodon.md) and identifies the corresponding [Misskey 2026.10.1](../../references/software/misskey.md) boundaries; it is a source-derived walkthrough, not captured traffic or a tested pair of servers.

## Actors and starting state

Alice is a local Mastodon user; Bob is on a remote server. Alice knows `bob@b.example` but has not yet followed Bob. A server resolves the handle using [WebFinger](../../fundamentals/webfinger.md), fetches the remote actor and records its identity and inbox. Handle discovery and authenticated retrieval can fail independently; the actor URI is distinct from a server-local database ID. `[source]` Mastodon 4.7.3 [account resolver](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/resolve_account_service.rb) and [actor fetcher](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_actor_service.rb).

## Step by step

1. **Create the outgoing request.** Mastodon's `FollowService` checks availability, blocks and migration state. For an ActivityPub target it records a `FollowRequest` even when the target is not locked, serializes a `Follow`, and enqueues `ActivityPub::DeliveryWorker` for the remote actor's inbox. An existing follow or request is reused instead of blindly creating another. Local-only follows have a different path. `[source]` [follow service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/follow_service.rb).
2. **Deliver asynchronously.** The worker sends a signed HTTP POST. A successful local API response is not a remote acceptance: a network error can leave delivery queued or eventually exhausted. See [delivery and retries](../delivery/queues-and-retries.md) and the [Mastodon case study](../../servers/case-studies/mastodon.md). `[source]` [delivery worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb).
3. **Process on the target.** For an incoming Follow to a Mastodon 4.7.3 local actor, the handler checks the target and policy. It creates a `FollowRequest`; a locked target or silenced requester gets a follow-request notification for review, while an eligible open account is authorized and gets a follow notification. Existing requests and follows have special repeat-handling; a blocked or moved target is rejected. `[source]` [incoming Follow handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/follow.rb).
4. **Accept or reject.** Mastodon's authorization service turns a request into a follow and queues an `Accept` to the requesting remote actor. Manual approval delays this step; a rejection has different state and must not be treated as acceptance. `[source]` [authorization service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/authorize_follow_service.rb), [rejection service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/reject_follow_service.rb).
5. **Complete on the requester.** Mastodon's incoming `Accept` handler looks up the pending follow request and authorizes it; an unrelated or missing request cannot be treated as a new follow. It may enqueue a remote-account refresh for the first local follower. The follow relationship does not imply any specific historical post was delivered. `[source]` [Accept handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/accept.rb).

Misskey 2026.10.1 also models following and follow requests in a dedicated service and dispatches incoming activities through its inbox service. Its exact notification, authorization, and delivery paths are implementation-specific; a Mastodon-to-Misskey transition has not been captured here. `[source]` [Misskey follow service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/UserFollowingService.ts), [inbox dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts).

## Technical details

This is a handwritten, unexecuted ActivityStreams example based on [ActivityPub §7.5](https://www.w3.org/TR/activitypub/#follow-activity-inbox); IDs are fictional. Authentication headers are omitted, and real peers can require signed requests.

```json
{"@context":"https://www.w3.org/ns/activitystreams", "id":"https://a.example/activities/1", "type":"Follow", "actor":"https://a.example/users/alice", "object":"https://b.example/users/bob"}
```

An `Accept` identifies Bob as actor and refers to that Follow, either by ID or in the form supported by the receiving implementation. Preserve the original activity ID for retries and later `Undo`; the request, its acceptance and a later unfollow are separate asynchronous events. `[spec]` ActivityPub §§6.5, 7.5–7.7, 7.12.

## Pitfalls

- **Pending forever:** check the outgoing delivery job, signature and the target's approval queue before retrying or recreating a request.
- **Repeated requests:** retries and `Undo` can race. Test duplicate IDs and reversed order, not only the happy path; neither implementation is a general exactly-once messaging system.
- **Accepted but no posts:** inspect subsequent publication and delivery separately; a follow is not a guaranteed history transfer.
- **Claiming an interoperability result:** reproduce the scenario with pinned server versions, signed requests, queue logs and relationship state before labeling any peer as compatible or broken.

## Sources

- [ActivityPub Recommendation §§6.5 and 7.5–7.7](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — Follow and Accept semantics.
- [Mastodon 4.7.3 FollowService](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/follow_service.rb), [incoming Follow](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/follow.rb) and [Accept](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/accept.rb) — request and acceptance paths.
- [Misskey 2026.10.1 UserFollowingService](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/UserFollowingService.ts) — follow and follow-request operations.
