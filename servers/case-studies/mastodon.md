# Mastodon 4.7.3

Mastodon is a multi-user social server with a Ruby on Rails application, background workers and a separate streaming service. Its federation pipeline turns signed remote requests into application records and then distributes work asynchronously; an accepted request is not a guarantee that a post appeared in a timeline. This case study follows the pinned 4.7.3 source, a historical version with known security fixes in later releases. Version and release details are in the [fact sheet](../../references/software/mastodon.md). `[source]`

## Architecture

The Rails process exposes the web UI, REST API and federation endpoints; PostgreSQL stores durable records. Redis supports queues, cached feeds and pub/sub, while **[Sidekiq](../../glossary.md#sidekiq)** executes background jobs. A separate Node service handles streaming connections. Media may use local or object storage, and full-text search can use Elasticsearch. These are distinct processes and persistence boundaries, not a single transaction. `[source]` [deployment configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/docker-compose.yml), [streaming service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/streaming/index.js), [Sidekiq configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/sidekiq.yml).

## Key code paths

The request-by-request sequences are on the [federation pipeline](../federation-pipelines/mastodon-4-7.md) page. Entry points, all `[source]`:

| Stage | Pinned entry point |
| --- | --- |
| Receive | [`ActivityPub::InboxesController#create`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/activitypub/inboxes_controller.rb#L12) |
| Process | [`ActivityPub::ProcessingWorker#perform`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/processing_worker.rb#L8), [`ProcessActivityService#call`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb) |
| Resolve | [`ActivityPub::FetchRemoteActorService`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_actor_service.rb), [`ActivityPub::FetchRemoteStatusService`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_status_service.rb) |
| Create locally | [`PostStatusService#call`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/post_status_service.rb#L51) |
| Distribute | [`ActivityPub::DistributionWorker`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/distribution_worker.rb), [`DeliveryWorker`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/activitypub/delivery_worker.rb#L25) |
| Timeline | [`FanOutOnWriteService#call`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/fan_out_on_write_service.rb#L12) |
| Media | [`MediaAttachment`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/media_attachment.rb), [`PostProcessMediaWorker`](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/workers/post_process_media_worker.rb) |

## API coverage

The application has a versioned Mastodon REST API with OAuth scopes, account, status, timeline, search, media and notification routes. It also has a separate WebSocket/server-sent-events streaming service. API versions are per endpoint: a v2 route for one resource does not imply a v2 equivalent for all resources. The [pinned routes](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/routes/api.rb) and [streaming implementation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/streaming/index.js) are the authority for this version. `[source]`

## Federation behaviour

Mastodon uses [ActivityPub server-to-server](../../fundamentals/activitypub-s2s.md), requires signed POSTs and can require signed GETs. Its own [pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) describes discovery, signing, supported extensions and limits. A human-readable account address and the actor's URI are different identifiers; remote resolution and attribution must preserve that distinction. `[documented]`

Relayed activities require additional attribution handling: the processing service tries a linked-data signature and then an object integrity proof when the HTTP signer differs from the activity actor. A valid HTTP signature alone does not establish that the signer may act for every actor or object in the payload. See the [processing service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb). `[source]`

### Representation, visibility and operational limits

A local `Status` may be a post, reply or boost; the ActivityPub serializer chooses `Note` or `Question` and adds audience, media, tags, content warning and language as applicable. A client's local status ID and an ActivityPub object's URI are different identifiers. `public`, `unlisted`, `private`, and `direct` are not equivalent access modes: unlisted content still addresses the ActivityStreams Public audience in `cc`, while read authorization for private and direct posts depends on the viewer's relationship or mention. Once a remote server receives content, local deletion cannot force every remote copy to disappear. `[source]` [Note serializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/note_serializer.rb), [audience mapping](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/tag_manager.rb), [status policy](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/policies/status_policy.rb).

### Extensions and signatures

The pinned federation statement lists followers synchronization (FEP-8fcf), search-indexing consent (FEP-5feb), consent-respecting quotes (FEP-044f) and a subset of Activity Intents (FEP-3b86), and accepts FEP-521a keys and FEP-8b32 integrity proofs on receipt; that is the project's declared scope, not an interoperability result. `[documented]` [federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md). Signature schemes, relayed-activity attribution and what each establishes are on [federation trust boundaries](../../security/mastodon-4-7.md); scheme differences across servers are on [HTTP signatures](../../fundamentals/http-signatures.md).

## Resource usage

Memory, throughput and storage are **unmeasured** here. Queue depth, follower distribution, media, database size and connection settings affect real deployments; no capacity figure can be inferred from this source review.

## Strengths, known bugs and tradeoffs

Named workers, services and serializers make boundaries discoverable, but a single interaction crosses several state stores and queues. A successful API response, persisted database row, local timeline update and remote delivery are separate events. This is an architectural inference from the paths above, not a measured reliability or performance comparison. `[source]`

Version 4.7.3 is affected by the later-disclosed [ActivityPub identifier verification advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j); the fix is in 4.7.4. Study this version as historical source, not as a deployment recommendation. `[documented]`

## Technical details

Mastodon 4.7.3 compacts JSON-LD when an embedded signature calls for it, but otherwise avoids treating every incoming payload as fully processed JSON-LD; malformed JSON or unsupported contexts do not become activities. The linked-data signature and integrity-proof paths have different forwarding constraints. These are implementation choices, not a general ActivityPub rule. `[source]` [processing service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb).

For the detailed request and delivery sequence, see the [federation pipeline](../federation-pipelines/mastodon-4-7.md). For operational state and recovery, see [storage and recovery](../storage/mastodon-4-7.md). The [federation trust boundaries](../../security/mastodon-4-7.md) page covers signature and authorization distinctions.


## Sources

- [Mastodon 4.7.3 release](https://github.com/mastodon/mastodon/releases/tag/v4.7.3) — release and version context.
- [Pinned ActivityPub source tree](https://github.com/mastodon/mastodon/tree/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app) — controller, worker, model and service paths cited above.
- [Pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) — project's declared federation behavior.
- [Identifier verification advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j) — historical security issue and affected versions.
