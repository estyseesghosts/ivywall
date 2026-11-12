# Pixelfed federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the Pixelfed maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean Pixelfed conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [github.com/pixelfed/pixelfed](https://github.com/pixelfed/pixelfed) |
| Release basis | Development snapshot: 230 commits after tag `v0.15.2`. |
| Commit | `2731e6999d47e1dcf05c0d931cae2f1b88e349d1` (2026-11-10) |
| Other wiki revisions | The [Pixelfed case study](../../servers/case-studies/pixelfed.md) and [fact sheet](../software/pixelfed.md) pin release 0.15.2 (`b19607f`). This snapshot is far ahead of that release; do not combine the two without checking. |
| Verification | Partial. `[source-verified]` items were read at this commit. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives. Shared inbox `POST /f/inbox`, per-user `POST /users/{username}/inbox`, instance actor `i/actor/inbox` and `i/actor/outbox` | `[source-verified]` [routes/api.php](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/routes/api.php) |
| WebFinger, NodeInfo | served; each can be disabled (`WEBFINGER`, `NODEINFO`) | `[source-verified]` [config/federation.php](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php) |
| HTTP signatures (draft-cavage) | signs outgoing; verifies incoming. No RFC 9421 code was looked for | `[source-verified]` [InboxWorker](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Jobs/InboxPipeline/InboxWorker.php) |
| Signed fetch ("authorized fetch") | `AUTHORIZED_FETCH`, default `false` | `[source-verified]` config |

### Federation switches and defaults

Federation is off unless configured: `ACTIVITY_PUB` defaults to `false`. With it on, these defaults apply. `[source-verified]` [config/federation.php](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php)

| Setting | Default | Effect |
| ------- | ------- | ------ |
| `AP_OUTBOX`, `AP_INBOX`, `AP_SHAREDINBOX` | true | each endpoint can be disabled |
| `AP_REMOTE_FOLLOW` | true | remote follow flow |
| `AUTHORIZED_FETCH` | false | require signed fetches |
| `ACTIVITYPUB_DELIVERY_TIMEOUT` | 30 s | outbound request timeout |
| `AP_DELIVERY_FAILURE_THRESHOLD`, `AP_DELIVERY_MAX_BACKOFF` | 5, 604800 s | dead-destination handling |
| `AP_FOLLOWERS_SYNC` | true | FEP-8fcf behaviour |
| `AP_BLOCK_SYNC`, `AP_BLOCK_SYNC_DISCLOSE` | true, true | FEP-070c behaviour |
| `AP_INGEST_STORE_NOTES_WITHOUT_FOLLOWERS` | false | store notes nobody follows |
| `PF_ACCT_MIGRATION_ENABLED` | true | account moves |
| `CUSTOM_EMOJI` | false | custom emoji |

### Supported FEPs

Support is described by direction and by whether it is full, partial or configurable. Evidence is read at this commit.

| FEP | Subject | Support | Direction | Evidence |
| --- | ------- | ------- | --------- | -------- |
| 044f | Consent-respecting quote posts | **partial, configurable** | accepts `QuoteRequest` and replies with `Accept` carrying a `QuoteAuthorization` stamp or `Reject`; revokes by `Delete`; enforces a per-account and per-status policy on every request. Whether Pixelfed itself sends `QuoteRequest` to remote servers when a user quotes is `[unverified]`; the FEP's own implementation list says it cannot create or view quotes directly | `[source-verified]` [HandlesQuoteRequests](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/Inbox/HandlesQuoteRequests.php), [QuoteService](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/QuoteService.php); `[upstream-documented]` FEP text |
| 8fcf | Followers collection synchronization | **configurable**, on by default | sends a signed `Collection-Synchronization` header on followers-only delivery, serves a partial followers collection to authenticated remote instances, reconciles incoming headers; all three can be disabled by `AP_FOLLOWERS_SYNC` | `[source-verified]` config comment, [FollowersSyncService](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/FollowersSyncService.php) |
| 070c | Block synchronization | **configurable**, on by default | receives and reconciles block digests; discloses its endpoint unless `AP_BLOCK_SYNC_DISCLOSE` is false | `[source-verified]` config, [BlockSyncService](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/BlockSyncService.php) |
| 7aa9 | Featured collection authorization | **partial** | handles `FeatureRequest`; exposes `canFeature` policies and stamps; automatic approval only | `[source-verified]` inbox dispatch, [FeaturedCollectionService](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/FeaturedCollectionService.php) |
| 5837 | Content provenance | **configurable, driver-dependent** | credential metadata; inspection and signing need configuration and a C2PA driver | `[source-verified]` file exists: [ContentCredentialService](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/ContentCredentials/ContentCredentialService.php); behaviour `[unverified]` |
| 6757 | License information | **partial** | media licence vocabulary | `[source-verified]` file exists: [License](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/Media/License.php); behaviour `[unverified]` |

An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer) and has been removed.

### Discovery

Controllers in [FederationController](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Http/Controllers/FederationController.php); WebFinger and NodeInfo toggles above. Local and domain URL validation can skip local checks and permit unresolved hosts by configuration, and refuses IP literals, single-label hosts and loopback names before resolution. `[source-verified]` config comments in [config/federation.php](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php)

### Authentication

| Step | Behaviour | Evidence |
| ---- | --------- | -------- |
| Required headers | `Signature` and `Date` | `[source-verified]` [InboxWorker](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Jobs/InboxPipeline/InboxWorker.php) |
| Date window | accepted only within one day either side of the server clock; otherwise rejected | `[source-verified]` same file |
| Body | `id` and `actor` required | `[source-verified]` same file |
| Key host | the activity id and actor must be on the signing key's host; the key's actor is resolved and the signature verified before dispatch | `[source-verified]` same file; the exact host rule is in the file |
| Replay | processed activity ids are deduplicated | `[upstream-documented]` earlier draft; the dedup code was not re-read |

### Activity and object matrix

Inbox dispatch cases: `Add`, `Block`, `Create`, `Follow`, `Announce`, `Accept`, `Delete`, `Like`, `Reject`, `Undo`, `View`, `Story:Reaction`, `Story:Reply`, `Flag`, `FeatureRequest`, `QuoteRequest`, `Update`, `Move`. `[source-verified]` [Inbox.php](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/Inbox.php)

| Activity | Object | Accepts | Conditions | Evidence |
| -------- | ------ | ------- | ---------- | -------- |
| `Create` | `Note` with attachment | yes | attachments are verified; `Note` replies handled separately; non-public notes filed by their audience | `[source-verified]` [HandlesCreates](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/Inbox/HandlesCreates.php) |
| `Create` | `Question`, poll-vote `Note` | yes | branches exist | `[source-verified]` same file |
| `Update` | `Note` | **yes**, only if the sender owns the stored status | a missing status from a remote sender goes to the direct-message handler | `[source-verified]` [HandlesUpdates](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/Inbox/HandlesUpdates.php) |
| `Update` | `Person` | yes | validator must pass | `[source-verified]` same file |
| `Update` | `Question` | **no branch found** | | `[source-verified]` same file |
| `Quote request` | `QuoteRequest` | yes | policy and instrument checks, always answered with `Accept` or `Reject` once actor and post are known; otherwise dropped silently | `[source-verified]` |
| `Move` | actor | yes | `PF_ACCT_MIGRATION_ENABLED` and validator | `[source-verified]` |

### Distinctive behaviour

- Image-first model: a post is a `Note` with attachments; stories use nonstandard `Story:Reaction` and `Story:Reply` activities. `[source-verified]` dispatch cases.
- Quote and feature policies are advisory and enforced on every request, so callers must handle authorization failures. `[source-verified]` comment in [StatusEditController](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Http/Controllers/StatusEditController.php)

### Operational behaviour

- Inbox is queued ([InboxWorker](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Jobs/InboxPipeline/InboxWorker.php)); delivery uses a configurable concurrency (default 10), chunk size (default 50) and queue. `[source-verified]` config.
- Fetched ActivityPub responses are capped at **2 MiB** by `MAX_RESPONSE_SIZE`, checked on `Content-Length` and on the body length. `[source-verified]` [ActivityPubFetchService](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/ActivityPubFetchService.php). The earlier draft's figure was right.
- A quote `Accept` is retried because the quoting server sends its `QuoteRequest` once. `[source-verified]` comment in [DeliverQuoteActivityPipeline](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Jobs/QuotePipeline/DeliverQuoteActivityPipeline.php)

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| No `Signature` or `Date`, or date outside one day | rejected | `[source-verified]` |
| Missing `id` or `actor` | rejected | `[source-verified]` |
| Unparseable signature header | rejected | `[source-verified]` |
| `QuoteRequest` from an unknown actor or for a non-quotable post | dropped silently | `[source-verified]` |
| `QuoteRequest` that fails the policy | `Reject` sent | `[source-verified]` |
| Revoked quote | `Reject` on re-request | `[source-verified]` |
| Response over 2 MiB | fetch rejected | `[source-verified]` |
| Actor unavailable | inbox job retries | `[source-verified]` (`RetriesWhenActorUnavailable` concern exists) |

### Examples

> Unknown: no signed delivery or `QuoteRequest` exchange has been captured or constructed yet.

## Sources

- [Pixelfed repository](https://github.com/pixelfed/pixelfed) — source read at commit `2731e6999d47e1dcf05c0d931cae2f1b88e349d1`
- [config/federation.php](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php) — switches and defaults
- [FEP-044f](../feps/fep-044f.md) — the quote model and its stated implementers
