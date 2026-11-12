# Delivery queues and retries

Federation crosses unreliable networks. A server can save a post locally while remote delivery is still pending, repeatedly failing, or permanently abandoned. Queues separate local work from network latency, but retries introduce duplicate deliveries and do not guarantee ordering. This page compares source behavior in [Mastodon 4.7.3](../../references/software/mastodon.md) and [Misskey 2026.10.1](../../references/software/misskey.md); no throughput measurements or cross-server test results are implied.

## Before you start

ActivityPub recommends asynchronous delivery and retries for network failures but does not prescribe a universal queue, schedule or exactly-once guarantee. `[spec]` [ActivityPub §7.1 and security considerations](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery). Track receipt, queueing, validation, persistence, fan-out and display as separate stages; an inbox HTTP acknowledgment alone does not show that every stage succeeded.

## Pick and deduplicate destinations

Mastodon computes reach and queues deliveries to remote inbox URLs. Misskey's delivery manager similarly assembles targets and can use a shared inbox to reduce duplicate HTTP requests. Distinct remote inboxes are a useful predictor of network fan-out, but follower enumeration and local timeline distribution still cost work. This is a source-derived mechanism, not a benchmark. `[source]` [Mastodon distribution](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/distribution_worker.rb), [Misskey delivery manager](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApDeliverManagerService.ts).

## Handle failure without claiming delivery

| Behavior | Mastodon 4.7.3 | Misskey 2026.10.1 |
| --- | --- | --- |
| Outgoing worker | Sidekiq `push` queue, configured for 16 retries; tracks destination availability and uses a stoplight around sending. | BullMQ delivery worker; default 128 concurrent jobs and 128 jobs/second per worker, configurable. |
| Backoff | Worker defines a fourth-power delay plus jitter; Sidekiq also applies its jitter. | HTTP-related strategy uses exponential delay with a base capped at eight hours, then adds up to 20% jitter. |
| Intake | Processing happens in background after inbox receipt. | Header/digest checks precede queueing and `202`; signature and activity processing occur in the inbox worker. |

`[source]` [Mastodon delivery worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb), [Mastodon processing worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/processing_worker.rb), [Misskey queue processor](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts), [Misskey inbox route](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/server/ActivityPubServerService.ts). Per-worker settings are not a cluster-wide rate limit; configuration and worker count change aggregate behavior.

## Technical details

A retried `Create` may be delivered more than once, so preserve its activity and object identity across attempts. Mastodon and Misskey both have object-specific duplicate protections, including URI-based checks; that is not a promise that every verb has exactly-once side effects. `[source]` [Mastodon Create handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/create.rb), [Misskey inbox dispatcher](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts).

Delivery of separate jobs is not a global ordering guarantee. A receiver needs explicit policy for `Update` or `Delete` before `Create`, repeat activities, stale retries and missing referenced objects. A practical test should submit each ordering and duplicate to isolated instances, record the exact versions and payload IDs, then compare queue logs and final database/API state. This is a proposed test, not an observed result. See [the post lifecycle](../activities/life-of-a-post.md).

## Pitfalls

- **An HTTP 202 is treated as completed work:** inspect the downstream worker and persistence result as well as the inbound response.
- **A retry creates a new identity:** reuse the original activity identity; design receiver side effects to tolerate duplicates.
- **A short outage overwhelms recovery:** monitor queue age, retry counts, destination failures and worker capacity. Adjust backoff and concurrency from measured workload, not an assumed universal setting.
- **An indefinitely unavailable destination consumes resources:** define and observe give-up and recovery policies. A finite retry budget trades resource use for possible missed delivery.
- **Newer updates arrive first:** test reordering, tombstones and cache reconciliation; do not assume queue insertion order produces global network order.

## Open questions

No reproducible benchmark or trace here establishes delivery latency, loss under worker crashes, or Mastodon-to-Misskey recovery behavior. Test at pinned commits with varied distinct inbox counts, failures, concurrency and restart timing before making capacity claims.

## Sources

- [ActivityPub Recommendation §7.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery) — delivery and retry recommendations.
- [Mastodon 4.7.3 delivery worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb) — retry and destination handling.
- [Misskey 2026.10.1 queue processor](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/queue/QueueProcessorService.ts) — worker concurrency and retry strategy.
- [Misskey delivery manager](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApDeliverManagerService.ts) — recipient selection and delivery grouping.
