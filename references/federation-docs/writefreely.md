# WriteFreely federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the WriteFreely maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean WriteFreely conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [github.com/writefreely/writefreely](https://github.com/writefreely/writefreely) |
| Release basis | Development snapshot: 12 commits after tag `v0.17.3`. |
| Commit | `2bbe3c70b9f36180a9d10d5a1c31480648761ce0` (2026-11-11) |
| Other wiki revisions | The [WriteFreely case study](../../servers/case-studies/writefreely.md) and [fact sheet](../software/writefreely.md) pin release 0.17.3 (`d248591`). This snapshot is 12 commits later. |
| Verification | Partial. `[source-verified]` items were read at this commit; the delivery-reliability findings are read from code and not tested. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

### Protocols and standards

WriteFreely is a publishing platform, not a general social server. Each blog is a federated `Person` actor that others can follow; posts are delivered to followers; followers can like posts.

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | outgoing delivery to followers' inboxes; a per-collection inbox for `Follow`, `Undo` and `Like` | `[source-verified]` [activitypub.go](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) |
| HTTP signatures | **signs** outgoing requests with RSA-SHA256 over `(request-target)`, `date`, `host`, `digest`. **Does not verify** incoming signatures | `[source-verified]` `makeActivityPost`; no signature verifier was found in the repository |
| WebFinger, NodeInfo | served | `[source-verified]` files `webfinger.go`, `nodeinfo.go` |
| Federation toggle | `federation` in the application config; federation can be turned off | `[source-verified]` [config.go](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/config/config.go) |

### Supported FEPs

No FEP support was established. An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer) and has been removed.

### Discovery

WebFinger and the actor document expose the blog actor with its inbox, outbox, followers and following collections. Collection routes: outbox, followers, following and inbox. `[source-verified]` [activitypub.go](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) (`handleFetchCollectionOutbox`, `…Followers`, `…Following`, `…Inbox`).

### Authentication

| Direction | Behaviour | Evidence |
| --------- | --------- | -------- |
| Outgoing | `Signature`-header RSA-SHA256 over `(request-target)`, `date`, `host`, `digest`; a `Digest` header with the SHA-256 of the body; a sign failure is logged and the request is **still sent** unsigned | `[source-verified]` `makeActivityPost` |
| Outgoing fetch | signed GET requests to resolve actors | `[source-verified]` |
| Incoming | **no signature verification in the inbox handler.** The body is decoded as JSON and dispatched. Anyone who can reach the inbox URL can post a `Follow`, `Like` or `Undo` in another actor's name | `[source-verified]` `handleFetchCollectionInbox` |

### Activity and object matrix

| Activity | Object | Accepts | Behaviour | Evidence |
| -------- | ------ | ------- | --------- | -------- |
| `Follow` | the blog | yes | answers with `Accept` after a 2-second delay and stores the follower (see Operational behaviour) | `[source-verified]` |
| `Like` | a post | yes | stores a remote like for the post | `[source-verified]` |
| `Undo` | `Like` | yes | removes the remote like | `[source-verified]` |
| `Undo` | `Follow` | partly | a `Follow` branch is a TODO inside `Undo`; an unfollow path exists in the delayed goroutine | `[source-verified]` TODO comment; `[inferred]` rest |
| `Delete` | any | acknowledged | returns 200 with the body and takes no other action | `[source-verified]` |
| `Create`, `Update`, `Announce`, others | | no handler | unrecognised types return 200 "OK" | `[source-verified]` |

Outgoing: `Create` and `Update` of posts to followers' shared inboxes, `Create` to mentioned remote users' inboxes, `Delete` of posts, and `Accept`. `[source-verified]` call sites in [activitypub.go](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go)

### Distinctive behaviour

- A blog actor is a `Person`; there are no replies handled inbound, so conversation does not flow back. `[source-verified]` handler set above.
- Outbound requests go through a client that validates the resolved IP of every connection, including redirects, so private, loopback and link-local destinations are refused. `[source-verified]` `activityPubClient`, `safeDialContext`, `isPublicIRI`

### Operational behaviour and delivery reliability

| Topic | Behaviour | Evidence |
| ----- | --------- | -------- |
| HTTP client | 15-second timeout, at most 5 redirects, IP checked at dial time | `[source-verified]` [`activityPubClient`](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) |
| **HTTP status interpretation** | **`makeActivityPost` does not look at the response status.** It reads the body and returns `nil` unless the request itself errored. A 4xx or 5xx from the follower's inbox is treated as success | `[source-verified]` [`makeActivityPost`](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) |
| **Persistence order for `Follow`** | The `Accept` is sent from a goroutine after a 2-second sleep, **before** the follower is written to the database. If sending fails (a network error), the goroutine returns and the follower is never stored; the remote server may have been refused or may have received the `Accept` with the relationship unrecorded on the WriteFreely side | `[source-verified]` `handleFetchCollectionInbox` |
| Retry | no retry or queue was found for outgoing activities; a failed send is logged | `[inferred]` from the code read |
| Recovery | no reconciliation of followers; a re-sent `Follow` would re-run the same path | `[inferred]` |
| Exceptions in the goroutine | not recovered; errors only logged | `[source-verified]` |

Together these mean a tester cannot infer that a follow exists from the remote server's `Accept` log, and cannot infer delivery success from the absence of an error. Test by reading the follower list.

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| Inbox JSON cannot be decoded | error returned | `[source-verified]` |
| Silenced owner | collection treated as not found | `[source-verified]` |
| Unknown activity type | 200 OK, no action | `[source-verified]` |
| Outgoing: destination refused by IP check | error, logged | `[source-verified]` |
| Outgoing: non-2xx response | **ignored** | `[source-verified]` |
| Outgoing: sign failure | logged; request sent without a valid signature | `[source-verified]` |
| Duplicate like | logged as an error and rolled back | `[source-verified]` |

### Examples

> Unknown: no captured exchange. A useful one is a `Follow` followed by the delayed `Accept`, with the remote inbox returning a 4xx to show the unrecorded follower.

## Sources

- [WriteFreely repository](https://github.com/writefreely/writefreely) — source read at commit `2bbe3c70b9f36180a9d10d5a1c31480648761ce0`
- [activitypub.go](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) — all behaviour above
