# GoToSocial v0.22.3

GoToSocial is a Go ActivityPub server designed around a relatively small deployment footprint and explicit user controls. It provides public pages and administrative settings alongside a Mastodon-compatible client API; a full social client is separate. The [version-pinned fact sheet](../../references/software/gotosocial.md) identifies the release used here. This is a source and documentation study, not a live interoperability or performance test.

## Architecture

The single Go application composes HTTP handlers, processing modules, database access, media storage, caches and background workers. Its Bun-backed persistence layer supports SQLite or PostgreSQL; media can use the filesystem or S3-compatible storage. Shared state contains caches, worker pools and per-URI locks. Dedicated pools handle client, federation, delivery, dereference and other work, so asynchronous work exists even though a separate Redis service or task broker is not required. `[source]` [state](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/state/state.go), [workers](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/workers/workers.go), [database adapter](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/db/bundb/bundb.go); `[documented]` [storage configuration](https://docs.gotosocial.org/en/v0.22.3/configuration/storage/).

A `Status` stores an internal ULID, unique ActivityPub URI, account, reply and boost references, visibility, language, poll, edits, rendered content and interaction policy. These normalized records are not a promise to preserve every incoming activity as an immutable raw event log. Timeline and relationship state is filtered by viewer and hydrated from stored data; absence of a local reply is not evidence that no remote reply exists. `[source]` [status model](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/gtsmodel/status.go); `[documented]` [post federation](https://docs.gotosocial.org/en/v0.22.3/federation/posts/).

## Key code paths

### Receiving and authenticating

The address where an actor receives activities (an **[inbox](../../glossary.md#inbox)**) accepts federated requests subject to HTTP signature verification, access controls and activity-specific handling. `AuthenticateFederatedRequest` resolves or refreshes a public key and checks key/owner consistency. `federatingdb.Create` handles distinct post, vote and forwarding cases, including activity-ID deduplication. Subsequent processing can dereference other objects and update state asynchronously. The exact transaction and queue boundary for every activity is not established here; a valid signature is not itself authorization for every object. `[source]` [authentication](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/federation/authenticate.go), [Create handler](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/federation/federatingdb/create.go); `[documented]` [access control](https://docs.gotosocial.org/en/v0.22.3/federation/access_control/).

### Delivery

The outgoing transport prepares ActivityPub POSTs for remote inboxes and enqueues indexed delivery work. A delivery worker signs requests, handles failures and retries with backoff. Local creation or queueing does not guarantee remote receipt, and this source study does not establish every retry limit, HTTP response classification or crash-recovery guarantee. The documented actor representation does not advertise a shared inbox, so peers should address the relevant individual inboxes. `[source]` [delivery setup](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/transport/deliver.go), [delivery worker](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/transport/delivery/worker.go); `[documented]` [actors](https://docs.gotosocial.org/en/v0.22.3/federation/actors/).

## API coverage

The server exposes Mastodon-compatible REST and OAuth endpoints, plus streaming and project-specific endpoints. Its static profiles and settings pages do not constitute a full interactive timeline client. Compatibility is endpoint- and version-specific: do not infer full Mastodon API coverage from support for the family. Consult the [v0.22.3 API inventory](https://docs.gotosocial.org/en/v0.22.3/api/swagger/) and [authentication documentation](https://docs.gotosocial.org/en/v0.22.3/api/authentication/). `[documented]`

## Federation behaviour

WebFinger resolves account handles to actor URLs. Regular users are `Person`, bot accounts `Service`, and the instance actor `Application`. Posts commonly use `Note`; polls use `Question` and vote notes. The implementation handles common follow, post, update, delete, like and announce flows subject to authorization and local policy, rather than every ActivityStreams combination. The outbox is a paginated ordered collection; followers/following collections may be hidden by their owner. `[documented]` [actors](https://docs.gotosocial.org/en/v0.22.3/federation/actors/), [posts](https://docs.gotosocial.org/en/v0.22.3/federation/posts/).

The v0.22.3 federation manual requires signed ActivityPub GET and POST requests, including reads of public actors and objects; unsigned clients can therefore fail where other servers allow anonymous reads. Outgoing requests use RSA-SHA256 signatures; GET signs `(request-target) host date`, and POST additionally signs `digest`. Signature verification attempts both inclusion and omission of query parameters; an outgoing request can be retried without the query after a 401. Public-key URLs end in `/main-key` and return a partial actor representation; the key's `owner` identifies the full actor. `[documented]` [HTTP signatures](https://docs.gotosocial.org/en/v0.22.3/federation/http_signatures/); `[source]` [signing](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/transport/signing.go).

Interaction controls express `canLike`, `canReply` and `canAnnounce` policies with automatic and manual approval, plus request and authorization objects. Their effect across servers depends on peer implementation: an external server can ignore a policy or retain content already delivered. Do not infer support for a particular FEP merely from a similar vocabulary. `[documented]` [interaction controls](https://docs.gotosocial.org/en/v0.22.3/federation/interaction_controls/).

## Resource usage

No memory, CPU, throughput or storage measurement is available for this case study. SQLite and PostgreSQL have different concurrency and backup characteristics; fan-out cost also depends on recipient topology, media and deployment settings. Measure with the target database, number of active accounts and destination inboxes before extrapolating capacity.

## Strengths, known bugs and tradeoffs

Signed fetching and interaction controls offer explicit access checks but increase the assumptions a peer must satisfy. Local-only content and limited-audience posts require different treatment from public posts; neither federation nor remote deletion can enforce confidentiality on a server that already received content. `[documented]` [access control](https://docs.gotosocial.org/en/v0.22.3/federation/access_control/), [interaction controls](https://docs.gotosocial.org/en/v0.22.3/federation/interaction_controls/).

v0.22.3 addressed a dereferencing issue involving inconsistent URI hosts; this historical fix does not prove that every later issue is resolved. Examine the [release notes](https://codeberg.org/superseriousbusiness/gotosocial/releases/tag/v0.22.3) and security advisories for the version being deployed. `[documented]`

## Technical details

A full restore needs a consistent database backup, media, configuration and signing keys; a data export is not equivalent to a complete instance backup. Test the restore in isolation and preserve the hostname and key material before rejoining federation. SQLite snapshots must account for write-ahead logging. `[documented]` [backup and restore](https://docs.gotosocial.org/en/v0.22.3/admin/backup_and_restore/), [database configuration](https://docs.gotosocial.org/en/v0.22.3/configuration/database/).

Unverified here: durable retry behavior across power loss, full key-rotation overlap, all out-of-order activity combinations and actual client/peer compatibility. Test duplicate Create, Update-before-Create, Delete-before-Create and key rotation with isolated actors and inspect final state, not just HTTP responses.

## Sources

- [GoToSocial v0.22.3 source tree](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4) — pinned implementation.
- [v0.22.3 federation documentation](https://docs.gotosocial.org/en/v0.22.3/federation/) — actor, post, signature and interaction semantics.
- [v0.22.3 backup and restore](https://docs.gotosocial.org/en/v0.22.3/admin/backup_and_restore/) — recovery scope.
