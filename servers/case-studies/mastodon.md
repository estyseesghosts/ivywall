# Mastodon 4.7.3

Mastodon is a multi-user social server with a Ruby on Rails application, background workers and a separate streaming service. Its federation pipeline turns signed remote requests into application records and then distributes work asynchronously; an accepted request is not a guarantee that a post appeared in a timeline. This case study follows the pinned 4.7.3 source, a historical version with known security fixes in later releases. Version and release details are in the [fact sheet](../../references/software/mastodon.md). `[source]`

## Architecture

The Rails process exposes the web UI, REST API and federation endpoints; PostgreSQL stores durable records. Redis supports queues, cached feeds and pub/sub, while **[Sidekiq](../../glossary.md#sidekiq)** executes background jobs. A separate Node service handles streaming connections. Media may use local or object storage, and full-text search can use Elasticsearch. These are distinct processes and persistence boundaries, not a single transaction. `[source]` [deployment configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/docker-compose.yml), [streaming service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/streaming/index.js), [Sidekiq configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/sidekiq.yml).

## Key code paths

| Stage | Pinned entry point | Consequence |
| --- | --- | --- |
| Receive | [`ActivityPub::InboxesController#create`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/activitypub/inboxes_controller.rb) | Checks payload size and request signature, queues processing, returns 202. An unknown actor's self-`Delete` or self-`Update` can be acknowledged early. `[source]` |
| Process | [`ActivityPub::ProcessingWorker#perform`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/processing_worker.rb), [`ProcessActivityService#call`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb) | The `ingress` queue retries up to eight times. The service parses, checks context and actor identity, handles relayed signatures and dispatches to an activity handler. Invalid JSON is discarded. `[source]` |
| Resolve | [`ActivityPub::FetchRemoteActorService`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_actor_service.rb), [`ActivityPub::FetchRemoteStatusService`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_status_service.rb) | Remote actor and status resolution are separate from accepting the original delivery. Fetching and identity checks are security boundaries. `[source]` |
| Create locally | [`PostStatusService#call`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb) | Preprocesses visibility, mentions, media and quote state, then saves a status in a database transaction before post-processing. `[source]` |
| Distribute | [`ActivityPub::DistributionWorker`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/distribution_worker.rb), [`DeliveryWorker`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb) | Selects inboxes from status reach, serializes an activity and delivers signed HTTP POSTs on the `push` queue, independently of local acceptance. `[source]` |
| Timeline | [`FanOutOnWriteService#call`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/fan_out_on_write_service.rb) | Batches local follower, list and notification work; public streaming distribution is conditional on visibility, boost and account state. `[source]` |
| Media | [`MediaAttachment`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/media_attachment.rb), [`PostProcessMediaWorker`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/post_process_media_worker.rb) | Upload and processing are not equivalent to publication; media has its own lifecycle and validation. `[source]` |

## API coverage

The application has a versioned Mastodon REST API with OAuth scopes, account, status, timeline, search, media and notification routes. It also has a separate WebSocket/server-sent-events streaming service. API versions are per endpoint: a v2 route for one resource does not imply a v2 equivalent for all resources. The [pinned routes](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/routes/api.rb) and [streaming implementation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/streaming/index.js) are the authority for this version. `[source]`

## Federation behaviour

Mastodon uses [ActivityPub server-to-server](../../fundamentals/activitypub-s2s.md), requires signed POSTs and can require signed GETs. Its own [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) describes discovery, signing, supported extensions and limits. A human-readable account address and the actor's URI are different identifiers; remote resolution and attribution must preserve that distinction. `[documented]`

Relayed activities require additional attribution handling: the processing service tries a linked-data signature and then an object integrity proof when the HTTP signer differs from the activity actor. A valid HTTP signature alone does not establish that the signer may act for every actor or object in the payload. See the [processing service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb). `[source]`

## Resource usage

Memory, throughput and storage are **unmeasured** here. Queue depth, follower distribution, media, database size and connection settings affect real deployments; no capacity figure can be inferred from this source review.

## Strengths, known bugs and tradeoffs

Named workers, services and serializers make boundaries discoverable, but a single interaction crosses several state stores and queues. A successful API response, persisted database row, local timeline update and remote delivery are separate events. This is an architectural inference from the paths above, not a measured reliability or performance comparison. `[source]`

Version 4.7.3 is affected by the later-disclosed [ActivityPub identifier verification advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j); the fix is in 4.7.4. Study this version as historical source, not as a deployment recommendation. `[documented]`

## Technical details

A typical inbound path is `POST /inbox` or a per-account inbox → signature and size checks → `ActivityPub::ProcessingWorker` (`ingress`) → `ProcessActivityService` → activity-specific handler. The controller queues the raw body after verifying the request and returns 202; processing can subsequently reject or ignore the activity. `Delete` and `Update` for a previously unknown actor can also receive 202 without queueing. `[source]` [inbox controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/activitypub/inboxes_controller.rb).

For outbound delivery, `DeliveryWorker` uses `application/activity+json`, signs on behalf of the source account, and may add `Collection-Synchronization`. It is configured for 16 retries on the `push` queue, adds jitter to exponential-style retry delay, and uses per-inbox availability tracking and a circuit breaker. Successful, permanent-failure and retryable outcomes are distinct; queueing is not receipt by a peer. `[source]` [delivery worker](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb).

Mastodon 4.7.3 compacts JSON-LD when an embedded signature calls for it, but otherwise avoids treating every incoming payload as fully processed JSON-LD; malformed JSON or unsupported contexts do not become activities. The linked-data signature and integrity-proof paths have different forwarding constraints. These are implementation choices, not a general ActivityPub rule. `[source]` [processing service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb).

For the detailed request and delivery sequence, see the [federation pipeline](../federation-pipelines/mastodon-4-7.md). For operational state and recovery, see [storage and recovery](../storage/mastodon-4-7.md). The [federation trust boundaries](../../security/mastodon-4-7.md) page covers signature and authorization distinctions.

## Sources

- [Mastodon 4.7.3 release](https://github.com/mastodon/mastodon/releases/tag/v4.7.3) — release and version context.
- [Pinned ActivityPub source tree](https://github.com/mastodon/mastodon/tree/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app) — controller, worker, model and service paths cited above.
- [Pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) — project's declared federation behavior.
- [Identifier verification advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j) — historical security issue and affected versions.
