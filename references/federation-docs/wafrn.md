# Wafrn federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the Wafrn maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean Wafrn conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [codeberg.org/wafrn/wafrn](https://codeberg.org/wafrn/wafrn) |
| Release basis | Release tag `2026.11.01` (the commit is that tag). |
| Commit | `f2bdd67849f44227d932c9ed0aa91b6af06d512d` (2026-11-05) |
| Other wiki revisions | The [Wafrn case study](../../servers/case-studies/wafrn.md) and [fact sheet](../software/wafrn.md) pin the same commit `f2bdd67`. |
| Verification | Partial. `[source-verified]` items were read in the local checkout of this commit. The hosting site (Codeberg) was not re-fetched. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

Partial-support limits come first, because the FEP list alone gives a stronger impression than the code supports.

### What is only partly implemented

| Area | What the code does | Evidence |
| ---- | ------------------ | -------- |
| FEP-044f quote **requests** | A `QuoteRequest` for a local post is **always accepted** if the post and the quoting post resolve: a quote record is created and an `Accept` carrying a `QuoteAuthorization` URL is sent. There is no policy check, and a code comment says rejecting quotes on the fediverse is a TODO | `[source-verified]` [inbox.ts, `QuoteRequest` case](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts) |
| FEP-044f quote **rejection / revocation** | not implemented in the incoming handler | `[source-verified]` same TODO; no revocation path found |
| FEP-6fce `ReplyRequest` | answered automatically with `Accept` or `Reject` from the same audience rule that governs local replies (`canInteract` on the post's reply control); a comment says there is no manual review yet | `[source-verified]` same file |
| FEP-6fce `AnnounceRequest` | answered automatically from `canInteract` on the post's boost control; the instrument must be on the requester's host; the announce is dereferenced and its actor and object are checked | `[source-verified]` same file |
| "Manual approval" policies | advertised policies with `manualApproval` are treated as automatic by the handlers above | `[source-verified]` same file |
| FEP-fffd | reads `at://` links and Bridgy URLs to associate a post with its AT Protocol counterpart, only when Bluesky lookup is enabled | `[source-verified]` [getPostThreadRecursive.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/activitypub/getPostThreadRecursive.ts) |

Quote requests, acceptances, rejections, authorization and revocation are therefore **not** equally supported: request and acceptance exist, rejection and revocation do not, and the policy is not consulted for quotes. An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer) and has been removed.

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; inbox is queued | `[source-verified]` [inbox.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts), [routes](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/routes/activitypub/activitypub.ts) |
| WebFinger, NodeInfo 2.0 | served | `[upstream-documented]` earlier draft; `[unverified]` here |
| HTTP signatures (RSA-SHA256, draft) | signs outgoing; verifies incoming POSTs | `[source-verified]` [checkFediverseSignature.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/activitypub/checkFediverseSignature.ts) |
| `RsaSignature2017` | verification path for signed activities | `[source-verified]` same file (the code comments "Mastodon allows two kinds of signatures on POST bodies") |
| AT Protocol | optional integration for threads and posts; see below | `[source-verified]` [`atproto/`](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/atproto/) directory |

### Discovery

Local actors at `/fediverse/blog/:url`; posts at `/fediverse/post/`; quote and reply authorization objects dereferenceable at `/fediverse/quote_authorization/…` and `/fediverse/reply_authorization/…`; following and followers are paginated and subject to visibility settings. `[source-verified]` URLs in [inbox.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts); `[upstream-documented]` earlier draft for collections.

### Authentication

| Item | Behaviour | Evidence |
| ---- | --------- | -------- |
| Digest | verified against the raw body for POSTs | `[source-verified]` |
| Clock skew | one hour ("this one is for threads") | `[source-verified]` |
| Actor binding | the signing actor must match the activity actor | `[source-verified]` |
| Key refresh | the stored key is refetched if the remote actor was last updated more than 24 hours ago | `[source-verified]` |
| Cross-account delete | a `#delete` shortcut is rejected when the actor does not match the target account | `[source-verified]` (log text in the inbox) |
| Enforcement | depends on the route | `[upstream-documented]` earlier draft |

### Activity and object matrix

The inbox dispatch handles `Accept`, `Reject`, `Announce`, `Create` (also `Page`), `Follow`, `Update`, `Undo`, `Like`, `Delete`, `EmojiReact`, `Remove`, `Add`, `Block`, `Move`, `Flag`, `Bite`, `AskQuestion`, `QuoteRequest`, `ReplyRequest`, `AnnounceRequest`, and ignores `CacheFile`, `Playlist`, `Listen`, `View`. `[source-verified]` [inbox.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts)

| Activity | Object | Accepts | Notes |
| -------- | ------ | ------- | ----- |
| `EmojiReact` | post | yes | handled separately from `Like` |
| `Update` | posts and others | yes, after a fixed 5-second wait | |
| `Bite`, `AskQuestion` | | yes | Wafrn-specific activity types |
| `QuoteRequest` / `ReplyRequest` / `AnnounceRequest` | local post | yes | see the partial-support table |
| `Accept` / `Reject` | follows and interaction requests | yes | |

### Distinctive behaviour: ActivityPub and AT Protocol boundary

Wafrn can resolve a post that is only on AT Protocol (an `at://` URI) when Bluesky lookup is enabled, and it recognises Bridgy Fed's `bsky.brid.gy` URLs, treating those as the original Bluesky posts and avoiding duplicates. It does not itself speak ActivityPub to Bluesky: bridged content arrives as ActivityPub from Bridgy. Where a conversation crosses the boundary, the AP and AT copies are mapped to one post by the lookup code. `[source-verified]` [getPostThreadRecursive.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/activitypub/getPostThreadRecursive.ts) lines around the `at://` and `brid.gy` branches; deeper mapping rules `[unverified]`.

### Operational behaviour

- Inbound activities are queued and processed asynchronously. `[source-verified]`
- An `Update` is deliberately delayed 5 seconds before being applied. `[source-verified]`
- Outbound delivery is built in `prepareSendRemotePost`; retry details were not read. `[unverified]`

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| Missing post or unresolved instrument for a quote or reply request | nothing is sent | `[source-verified]` |
| Disallowed reply request | `Reject` | `[source-verified]` |
| Announce request with an instrument on another host, or mismatched actor/object | ignored | `[source-verified]` |
| Cross-account delete shortcut | rejected | `[source-verified]` |
| Invalid POST signature | request not processed | `[source-verified]` |

### Examples

An `Accept` for a quote request, as constructed by the handler (not captured):

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://wafrn.example/contexts/litepub-0.1.jsonld"],
  "type": "Accept",
  "id": "https://wafrn.example/fediverse/quote_request/123",
  "actor": "https://wafrn.example/fediverse/blog/alice",
  "object": { "type": "QuoteRequest", "object": "https://wafrn.example/fediverse/post/…", "instrument": { "id": "https://other.example/notes/9" } },
  "result": "https://wafrn.example/fediverse/quote_authorization/123"
}
```

## Sources

- [Wafrn repository](https://codeberg.org/wafrn/wafrn) — source read at commit `f2bdd67849f44227d932c9ed0aa91b6af06d512d`
- [inbox.ts](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts) — dispatch and the interaction request handlers
- [FEP-044f](../feps/fep-044f.md) — quote model
