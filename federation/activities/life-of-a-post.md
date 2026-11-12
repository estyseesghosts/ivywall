# Life of a federated post

A post is a sequence of local persistence, fan-out, network delivery and remote processing, not one atomic transaction across servers. This walkthrough follows a public post from Mastodon 4.7.3 to a Misskey 2026.10.1 inbox using their source. The sequence is inferred from code, not an observed end-to-end test; each deployment can also apply local policy. See the [Mastodon](../../servers/case-studies/mastodon.md) and [Misskey](../../servers/case-studies/misskey.md) studies for the pinned releases.

## Actors and starting state

Alice has an account on a Mastodon server. Bob follows her from a Misskey server; the relationship is already accepted and Alice's server has Bob's remote actor and inbox information. Alice submits a public, text-only original post using a user-authorized Mastodon client. An actor is the network representation of an account; its [inbox](../../glossary.md#inbox) is where activities are delivered.

## Step by step

1. **Client request.** `POST /api/v1/statuses` requires a user token with the appropriate write scope. The controller passes text, audience, optional reply/media/poll parameters and `Idempotency-Key` to `PostStatusService`. The service validates the submission and stores a local `Status`; a local success response is not proof of remote receipt. `[source]` [controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses_controller.rb), [posting service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb). See the [client API](../../clients/apis/mastodon-rest.md) for retry behavior.
2. **Local distribution.** Mastodon schedules local distribution separately from remote delivery. Its distribution worker and fan-out service put eligible status references into local feed structures and perform related notifications and streaming work. Visibility, filters, audience and relationship state influence who can see the result. `[source]` [distribution worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/distribution_worker.rb), [fan-out service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/fan_out_on_write_service.rb).
3. **Build deliveries.** ActivityPub distribution serializes an original post as `Create` with a `Note` and chooses recipients from its reach. Inbox URLs can be deduplicated, including shared inboxes where appropriate; a server with many recipients need not receive one identical POST per follower. `[source]` [federation distribution worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/distribution_worker.rb#L11), [raw distribution worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/raw_distribution_worker.rb#L13).
4. **Send.** A delivery worker signs and sends the request to each selected destination, with retries and failure tracking. A destination can be slow, unreachable or reject the request; a queued job or HTTP success is not proof that a recipient displayed the post. `[source]` [delivery worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb#L11).
5. **Receive on Misskey.** Misskey's inbox route checks federation configuration, signed headers and body digest, enqueues the activity and responds `202`. The inbox worker then resolves the signing key, verifies the signature and actor relationship, and applies federation policy. A 202 can therefore precede a later failure. `[source]` [inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts), [inbox worker](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts#L66).
6. **Persist and show.** The `Create` handler resolves and validates the object, uses a URI lock and existence checks to avoid duplicate notes, then creates the supported remote note. Feed fan-out and read-side visibility are separate: an accepted or stored activity does not ensure Bob's client will show it. Media and referenced objects may require further network fetches. `[source]` [inbox dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [remote note service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts), [timeline service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/FanoutTimelineService.ts).

## Technical details

This minimal payload is handwritten from the ActivityPub data model and was not sent to either server. Actual payloads and headers vary with the release and post. `Public` is an audience marker, not an inbox URL. HTTP signature and digest headers are omitted here, not optional in the studied receiving path. `[spec]` [ActivityPub §§5.6, 7](https://www.w3.org/TR/2018/REC-activitypub-20180123/).

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://a.example/activities/123",
  "type": "Create",
  "actor": "https://a.example/users/alice",
  "to": ["https://www.w3.org/ns/activitystreams#Public"],
  "cc": ["https://a.example/users/alice/followers"],
  "object": {
    "id": "https://a.example/users/alice/statuses/123",
    "type": "Note",
    "attributedTo": "https://a.example/users/alice",
    "to": ["https://www.w3.org/ns/activitystreams#Public"],
    "cc": ["https://a.example/users/alice/followers"],
    "content": "<p>Hello</p>"
  }
}
```

The activity and object IDs serve different purposes. Retrying delivery with the same activity ID supports deduplication, but URI locking for a Note is not a general exactly-once guarantee. `Update` and `Delete` can arrive late or out of order, and a remote server may not implement every object update. Misskey 2026.10.1's dispatcher does not process a general incoming `Update` of a `Note`; see its [case study](../../servers/case-studies/misskey.md). `[source]` [Misskey dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts).

## Pitfalls

- **A 202 is not a persisted post.** Inspect queue processing, signature and policy decisions after the response.
- **A stored post is not visible to everyone.** Check addressing, follow state, visibility and read-side filters.
- **A reply can be missing.** Parent resolution, authorization or delivery can fail independently; a server's copy of a conversation is incomplete.
- **A deletion is not a distributed erasure guarantee.** Peers retain control of their own storage and may have copied content.
- **Do not infer throughput from source.** Measure queue depth, distinct destination inboxes, retry rates and feed fan-out under a stated workload.

## Deletion and delayed convergence in a laboratory run

The 19 October 2026 Pinetree/Birchtree run 5 report lists eight feature checks where a deleted marker remained visible at the original check. The operator reports a later read-only scan found those markers absent from every tested destination user's home timeline. That recheck supports delayed disappearance from those timelines; it does not establish deletion from every cache, database, or downstream server. `[reported]` [run summary](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L54-L58), [recheck log](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-run5-log.md#L43-L48).

The same report separately records residue in a delete-before-create churn test, with a suspected ordering mechanism for the Birchtree nodes. That is a different scenario from the eight delayed timeline checks; the report does not classify all other nodes' residue. The run identifies Pinetree build `f58be005c558f650` and Birchtree build `e24d75aea1085a06`, but not exact peer versions for every row. A new test should retain activity IDs and record delivery order, queue and final stored state as well as timeline visibility. `[reported]` [run setup and churn](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L83-L88).

## Sources

- [ActivityPub Recommendation](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — addressing, Create and server-to-server delivery.
- [Mastodon 4.7.3 posting service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb) and [federation distribution](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/distribution_worker.rb#L11) — source-side persistence and fan-out.
- [Misskey 2026.10.1 inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts) and [inbox processor](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts#L66) — receiving and asynchronous authentication.
- [Run 5 federation benchmark](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L54-L58) — reported timeline deletion checks and later recheck.
