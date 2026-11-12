# Catodon federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the Catodon maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean Catodon conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [codefloe.com/catodon/catodon](https://codefloe.com/catodon/catodon) |
| Release basis | Development snapshot: 38 commits after tag `26.11.0-rc.1`, a release candidate. |
| Commit | `a7319c535ecc4ac0bcb3727637e1f42749019d18` (2026-11-11) |
| Other wiki revisions | No Catodon case study or fact sheet exists, so there is no other pinned revision. |
| Verification | Partial. `[source-verified]` items were read in the local checkout of this commit; `[inferred]` rows rest on references, not on reading the behaviour. The hosting site (CodeFloe) could not be retrieved independently, so the links point at it but were not re-fetched. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

Catodon is a Misskey-derived server. It is not wire-identical to Misskey; the clearest difference found here is that it applies `Update` of ordinary posts (see the matrix). Each claim below is separated so it can be checked on its own.

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; shared inbox and per-user inbox, each with a **64 KiB** body limit | `[source-verified]` [ActivityPubServerService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/ActivityPubServerService.ts) |
| ActivityPub client-to-server | optional, **on unless an administrator turns off "ActivityPub client API"**; it carries out posted activities through the same endpoints the Misskey and Mastodon APIs use, and answers HTTP 422 with `application/problem+json` where Misskey cannot express the request | `[source-verified]` [COMPATIBILITY.md](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/activitypub-c2s/COMPATIBILITY.md) |
| WebFinger, NodeInfo | served | `[source-verified]` [WellKnownServerService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/WellKnownServerService.ts) |
| HTTP signatures (draft) and RFC 9421 | verifies both on inboxes; signing and requiring signatures on GET are configurable | `[upstream-documented]` earlier draft; `[unverified]` here |
| `RsaSignature2017` linked-data signatures | handled, including for relayed activities | `[source-verified]` [JsonLdService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/JsonLdService.ts) exists |

### Supported FEPs

Each row is a separate claim with its own evidence. "References" means the FEP number or its distinctive fields appear in the named files; it is weaker than a read of the behaviour.

| FEP | Claim | Direction | Support level | Evidence |
| --- | ----- | --------- | ------------- | -------- |
| 044f | quote policies, requests, authorization stamps | accepts `QuoteRequest` and answers `Accept` with a stamp or `Reject`; verifies stamps by dereferencing; emits requests | **substantial**: a dedicated handler checks that the request id host equals the actor host, requires an `instrument`, applies a rate limit and returns `Reject` on refusal | `[source-verified]` [ApInboxService `quoteRequest`](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApInboxService.ts), [check-quote-authorization.ts](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/misc/check-quote-authorization.ts) |
| 1b12 | forum `Group` actors relay member activities | emits and accepts | present | `[inferred]` references in [ApInboxService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApInboxService.ts) and [ApRendererService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApRendererService.ts) |
| 7888 | keeps an external conversation `context` | accepts; does not advertise local context collection URIs | partial | `[inferred]` reference in [type.ts](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/type.ts) |
| 4f05 | emits `Announce(Undo(Delete))` when restoring a moderator-removed post | emits | partial; receivers without the behaviour may keep the tombstone | `[inferred]` reference in [ForumModerationService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/ForumModerationService.ts) |
| e232 | reads and emits the legacy Misskey quote link in `tag` | both | compatibility | `[inferred]` references in [ApRendererService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApRendererService.ts) and [ApNoteService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/models/ApNoteService.ts) |
| 2677 | application actor linked from NodeInfo | emits | present | `[source-verified]` file [fep-2677.ts](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/misc/fep-2677.ts) and [NodeinfoServerService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/NodeinfoServerService.ts) |
| 5feb | respects remote actors' search-indexing preference | accepts | partial | `[inferred]` references in [ApPersonService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/models/ApPersonService.ts) |
| 8a8e | events and attendance (`Join`, `Leave`, tentative accept/reject) | both | partial; attendance fields vary by peer | `[source-verified]` inbox dispatch handles `Invite`, `Join`, `Leave`, `TentativeAccept`, `TentativeReject`; mapping is in the events guide |
| b2b8 | long-form `Article` posts | both | present | `[inferred]` [BlogPublishService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/BlogPublishService.ts) |
| ee3a | EXIF metadata a user chooses to share | both | opt-in | `[inferred]` [ApImageService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/models/ApImageService.ts) |
| 5837 | content provenance: digital source types read and sent; content credentials read only | both, asymmetric | partial | `[inferred]` references in [ApImageService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/models/ApImageService.ts) |
| d8c2 | `Application` objects identify OAuth clients | emits | partial | `[inferred]` [ApRendererService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApRendererService.ts) |

An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer) and has been removed. Rows marked `[inferred]` need a read of the behaviour before being used in a compatibility claim.

### Discovery

WebFinger for local accounts; the application actor is linked from NodeInfo (FEP-2677 row). Public upcoming events are exposed through a collection. `[upstream-documented]` [events federation guide](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/docs/events-federation.md)

### Authentication

See the protocols table. A received quote authorization is not trusted merely because it is embedded in a post; it is dereferenced and checked. `[source-verified]` [check-quote-authorization.ts](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/misc/check-quote-authorization.ts) exists and the handler calls into the quote service.

### Activity and object matrix

Inbox dispatch handles `Create`, `Delete`, `Update`, `Follow`, `Accept`, `Reject`, `Add`, `Remove`, `Announce`, `Like`, `Dislike`, `Undo`, `Block`, `Flag`, `Move`, `QuoteRequest`, `Invite`, `Join`, `Leave`, `TentativeAccept`, `TentativeReject`. `[source-verified]` [ApInboxService `performOneActivity`](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApInboxService.ts)

| Activity | Object | Accepts | Behaviour |
| -------- | ------ | ------- | --------- |
| `Update` | actor | yes | refreshes the actor; the activity actor must equal the stored actor |
| `Update` | `Question` | yes | creates the poll if unknown; a later edit date is applied as an edit; otherwise only the vote counts are applied |
| `Update` | post types (`Note`, `Article`, others) and BookWyrm native posts | **yes** | applied as an edit; if the post is unknown it is created instead (this covers Mastodon sending a quote's approval as an `Update` straight after its `Create`) |
| `QuoteRequest` | quoted post | yes | see FEP-044f row |
| `Like` / `Dislike` | note | yes | both have handlers |

This differs from Misskey 2026.11.0-beta.1 development builds, whose handler skips `Update` of ordinary posts (see the [Misskey document](misskey.md)). `[source-verified]` [`update`](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/ApInboxService.ts)

### Distinctive behaviour

- Quote posts: can advertise a policy, request authorization, verify dereferenced stamps and process `Accept`/`Reject`; also understands older quote forms. `[source-verified]` handler above and [QuotePolicyService](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/QuotePolicyService.ts)
- Events, places and nearby search are documented in [Nearby federation](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/docs/nearby-federation.md) and the events guide. `[upstream-documented]`
- The client API advertises OAuth discovery and selected outbox operations; accepted operations and unsupported addressing are listed in the compatibility notes. A post with no addressees becomes visible only to its author, never public by omission. `[source-verified]` [COMPATIBILITY.md](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/activitypub-c2s/COMPATIBILITY.md)

### Operational behaviour

- 64 KiB inbox body limit. `[source-verified]`
- Inbound `QuoteRequest`s are rate-limited per remote actor and quoted post. `[source-verified]`
- Per-object locking and retry behaviour for the inbox queue were not read. `[unverified]`

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| `QuoteRequest` without an id, with a mismatched id host, or without an `instrument` | skipped with a reason | `[source-verified]` |
| `QuoteRequest` rate-limited, unauthorised, or for a missing post | `Reject` delivered | `[source-verified]` |
| `Update` with a mismatched actor | `skip: invalid actor` | `[source-verified]` |
| `Update` of an unsupported type | `skip: Unsupported type for Update` | `[source-verified]` |
| Client API request Misskey cannot express | HTTP 422 `problem+json` | `[source-verified]` |
| Body over 64 KiB | rejected | `[source-verified]` |

### Examples

> Unknown: no captured or constructed exchange has been added yet.

## Sources

- [Catodon repository](https://codefloe.com/catodon/catodon) — source read at commit `a7319c535ecc4ac0bcb3727637e1f42749019d18`
- [ActivityPub C2S compatibility notes](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/activitypub-c2s/COMPATIBILITY.md) — upstream list of gaps
- [FEP-044f](../feps/fep-044f.md) — quote model
