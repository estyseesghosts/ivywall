# Life of a federated post

A post is a sequence of local persistence, fan-out, network delivery and remote processing, not one atomic transaction across servers. This walkthrough follows a public post from Mastodon 4.7.3 to a Misskey 2026.10.1 inbox using their source. The sequence is inferred from code, not an observed end-to-end test; each deployment can also apply local policy. See the [Mastodon](../../servers/case-studies/mastodon.md) and [Misskey](../../servers/case-studies/misskey.md) studies for the pinned releases.

## Actors and starting state

Alice has an account on a Mastodon server. Bob follows her from a Misskey server; the relationship is already accepted and Alice's server has Bob's remote actor and inbox information. Alice submits a public, text-only original post using a user-authorized Mastodon client. An actor is the network representation of an account; its [inbox](../../glossary.md#inbox) is where activities are delivered.

## Step by step

Each step is traced in code on the [Mastodon federation pipeline](../../servers/federation-pipelines/mastodon-4-7.md) (sender) and the [Misskey federation pipeline](../../servers/federation-pipelines/misskey.md) (receiver); only the cross-server consequences are listed here.

1. **Client request.** `POST /api/v1/statuses` stores a local `Status`. A success response is not proof of remote receipt. See the [client API](../../clients/apis/mastodon-rest.md) for retry behaviour.
2. **Local distribution.** Feeds, notifications and streaming for local viewers are scheduled separately from remote delivery.
3. **Build deliveries.** The post becomes a `Create` of a `Note`; inbox URLs are deduplicated, so a server with many followers gets one shared-inbox POST, not one per follower.
4. **Send.** A worker signs and POSTs to each inbox, with retries and failure tracking. A queued job or HTTP success is not proof the recipient displayed the post. See [delivery and retries](../delivery/queues-and-retries.md).
5. **Receive.** The receiving inbox checks the signature headers and digest, queues the activity and answers `202`; key and actor verification run later, so a failure can follow the `202`.
6. **Persist and show.** The `Create` handler resolves the object, avoids duplicates with a URI lock and existence check, and creates the remote note. Timeline fan-out and read-side visibility are separate: a stored activity does not ensure Bob's client shows it. Media and referenced objects may need more fetches.

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

## Deletion is not instant everywhere

In the October 2026 [laboratory](../../testing/interoperability/bench-evidence.md), eight delete checks failed at first and a later read-only scan found every marker gone from the destination home timelines. That shows delayed timeline cleanup, not removal from every cache or downstream server. `[reported]` [run summary](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L54-L58), [recheck log](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-run5-log.md#L43-L48). Residue in a delete-before-create churn test is a different problem: see [a deleted post reappears](../failure-modes/delete-before-create.md). Keep activity ids, delivery order, queue state and final stored state, not timeline visibility alone.

## Sources

- [ActivityPub Recommendation](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — addressing, Create and server-to-server delivery.
- [Mastodon 4.7.3 posting service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb) and [federation distribution](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/distribution_worker.rb#L11) — source-side persistence and fan-out.
- [Misskey 2026.10.1 inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts) and [inbox processor](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/processors/InboxProcessorService.ts#L66) — receiving and asynchronous authentication.
- [Run 5 federation benchmark](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L54-L58) — reported timeline deletion checks and later recheck.
