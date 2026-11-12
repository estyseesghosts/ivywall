# NodeBB federation behaviour (community-written)

> **Not by the NodeBB maintainers.** Written for this wiki from the project's source; it may be incomplete or inaccurate and must not be cited as the project's own statement. It follows the structure of [FEP-67ff](../feps/fep-67ff.md); the project publishes no such file.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [github.com/NodeBB/NodeBB](https://github.com/NodeBB/NodeBB) |
| Release basis | Development snapshot: 19 commits after tag `v4.16.7`. |
| Commit | `b04f482eb068e9421bed35c335232164a27fc5b5` (2026-11-11) |
| Other wiki revisions | The [NodeBB case study](../../servers/case-studies/nodebb.md) and [fact sheet](../software/nodebb.md) pin the 4.16.7 release commit `e10be67`; do not combine findings across the two without checking the diff. |
| Verification | Partial. Items labelled `[source-verified]` were read at this commit; the FEP positions are copied from NodeBB's documentation site, not from this commit. |

Claim labels (`[source-verified]`, `[upstream-documented]`, `[observed]`, `[inferred]`, `[unverified]`) are defined in [AGENTS.md](../../AGENTS.md#community-written-federation-documents).

## Document

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; per-user inbox `/uid/:uid/inbox`, category inbox `/category/:cid/inbox`, instance `/inbox`; an outbox exists at `/uid/:uid/outbox` | `[source-verified]` [routes](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/routes/activitypub.js) |
| WebFinger | serves and resolves | `[source-verified]` [well-known](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/well-known.js) |
| HTTP signatures (draft-cavage) and HTTP Message Signatures (RFC 9421) | verifies both; signs both (see Authentication) | `[source-verified]` [signatures](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/signatures.js) |
| NodeInfo 2.0 | serves schema 2.0 only at `/nodeinfo/2.0` | `[source-verified]` [well-known routes](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/routes/well-known.js) |

### Supported FEPs

NodeBB publishes its own FEP position table in its documentation, listing each proposal's position and whether it is implemented. The table below starts from that list (`[upstream-documented]`) and adds what this wiki found in the source at the commit above. The upstream table describes the current documentation site and may not match this commit exactly. "No evidence found" means a search for the FEP's identifier or distinguishing field turned up nothing, not that the feature is absent.

| FEP | Subject | NodeBB docs: implemented | Source evidence at this commit | Direction and notes |
| --- | ------- | ------------------------ | ------------------------------ | ------------------- |
| 1b12 | Group federation | yes | `[source-verified]` category actors announce to followers and relays ([feps.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/feps.js)); category handling in [inbox.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/inbox.js) | emits and accepts; plain-object `Announce` for main posts |
| 3b86 | Activity Intents | yes | `[source-verified]` WebFinger templates and an intents endpoint ([well-known.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/well-known.js), [intents](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/write/intents.js)) | emits templates; reads remote ones `[inferred]` |
| baf5 | Administrator Collection | yes | `[source-verified]` `/actor/admins` ([routes](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/routes/activitypub.js)) | emits |
| fb2a | Actor metadata | yes | `[source-verified]` attachment parsing in [mocks.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/mocks.js) | accepts `PropertyValue`, `Link`, `Note` |
| 7888 | Demystifying the `context` property | yes | `[inferred]` context resolution in [contexts.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/contexts.js) | emits and resolves contexts |
| 4f05 | Soft Deletion | yes | `[inferred]` Tombstones with `formerType` rendered in [mocks.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/mocks.js) | emits; inbound Tombstone handling in [inbox.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/inbox.js) |
| 9098 | Custom emojis | yes | `[inferred]` `Emoji` tags parsed in [notes.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/notes.js) and [helpers.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/helpers.js); an emoji route | accepts, serves |
| f228 | Backfilling Conversations | yes | `[inferred]` backfill job in [jobs.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/jobs.js) | fetches |
| fe34 | Origin-based security model | yes | `[source-verified]` same-origin checks on `attributedTo` and category ids in [inbox.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/inbox.js); full scope `[unverified]` | accepts with checks |
| 7458 | Using the replies collection | partial | `[source-verified]` a `/post/:pid/replies` route exists ([routes](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/routes/activitypub.js)); a `replies` property is commented "todo" in one renderer ([mocks.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/mocks.js)) | partial |
| 0151 | NodeInfo (2025 edition) | yes | `[unverified]` the source serves schema 2.0 only | |
| 11dd, f15d | Context ownership; relocation and removal | yes | `[unverified]` | |
| ae0c | Relay protocols | yes | `[source-verified]` [relays.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/relays.js) and relay broadcasting in [feps.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/feps.js) | emits to relays |
| b2b8 | Long-form text | yes | `[unverified]` `Article` is an accepted post type | accepts |
| d556 | Server-level actor discovery via WebFinger | yes | `[unverified]` | |
| 044f | Quote posts | no (positive position) | no evidence found | neither emits nor accepts |
| c0e0, 9967, 1a11, 8b32 | Emoji reactions, polls, bulk Announce, integrity proofs | no (positive position) | no evidence found | not implemented per upstream |

### Discovery

- Application actor `/actor`; users `/uid/:uid` (also `/user/:userslug`); categories `/category/:cid`; topics `/topic/:tid`; posts `/post/:pid`. `[source-verified]` [routes](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/routes/activitypub.js)
- WebFinger accepts `acct:` resources whose host matches the local host and resolves users, categories and the application actor, subject to local view privileges. `[source-verified]` [well-known](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/well-known.js)
- Accepted request content types are `application/activity+json` and ActivityStreams-profiled JSON-LD. Remote fetches use HTTPS except when the `CI` environment variable is `true`. `[source-verified]` [index.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/index.js)

### Authentication

| Item | Behaviour | Evidence |
| ---- | --------- | -------- |
| Incoming | Requires `Signature` or `Signature-Input`; for requests with a body requires a `Digest` or `Content-Digest` header and checks it against the body; then tries RFC 9421, then the draft scheme | `[source-verified]` [`Signatures.verify`](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/signatures.js) |
| Outgoing, draft | Signs `(request-target)`, `host`, `date` and `digest` when present | `[source-verified]` same file |
| Outgoing, RFC 9421 | Signs `@method`, `@authority`, `@target-uri`, `date`, plus `content-digest` and `content-type` when there is a body; carries `created` and a nonce | `[source-verified]` same file |
| Clock skew | RFC 9421 `created` and `expires` are checked with a skew tolerance | `[source-verified]` constant at the top of the same file |
| Public key fetch | Rate-limited per IP | `[source-verified]` [index.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/index.js) |

### Activity and object matrix

Inbound handlers exist for `Create`, `Update`, `Delete`, `Add`, `Remove`, `Move`, `Like`, `Dislike`, `Announce`, `Follow`, `Accept`, `Undo` and `Reject`. `[source-verified]` [inbox.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/inbox.js). Conditions:

| Activity | Object | Accepts | Conditions |
| -------- | ------ | ------- | ---------- |
| `Create` | `Note`, `Page`, `Article`, `Question`, `Video` | yes | `attributedTo` must be a single value on the sender's origin; an array is rejected. `[source-verified]` |
| `Update` | post types, actors, `Tombstone` | yes | same `attributedTo` origin check; the object may be refetched. `[source-verified]` |
| `Delete` | notes, contexts, messages | yes | deleting a context's main post removes the topic. `[source-verified]` |
| `Like` / `Dislike` | posts | yes | mapped to votes; refused where voting is not allowed. `[source-verified]` |
| `Announce` | objects, `Create`, `Like`, `Update`, `Delete` | yes | rejected when there are no local followers of the announcer. `[source-verified]` |
| `Follow` / `Accept` / `Undo(Follow)` | application, user, category actors | yes | the target actor type selects the branch. `[source-verified]` |
| `Add` / `Remove` / `Move` | posts and topics with categories | yes | the category must be same-origin as the actor. `[source-verified]` |

Accepted actor types: `Application`, `Organization`, `Person`, `Service`; `Group` is listed separately for community actors. Remote actors must have an `inbox`. `[source-verified]` [index.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/index.js)

### Distinctive behaviour

- A forum category is a federated actor; main posts can be announced to followers and relays as plain objects as well as wrapped activities (FEP-1b12). `[source-verified]`
- Federation and view privileges are configurable, so not every forum, category or user is publicly discoverable. `[upstream-documented]`

### Operational behaviour

- Delivery POST timeout is 10 seconds, redirects are not followed and destinations pass an SSRF check. `[source-verified]` [sendWorker.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/sendWorker.js)
- Responses over 10 MiB are refused by `Content-Length`. `[source-verified]` same file.
- **Signature fallback can cause duplicate delivery.** For outbound POSTs NodeBB signs with RFC 9421 first. If that attempt fails for any reason, including a timeout after the remote already processed the activity, it sends the same activity again with a draft signature. A receiver can therefore get the same activity twice and must deduplicate by activity id. `[source-verified]` [sendWorker.js](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/sendWorker.js)

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| Missing signature, or a body without a digest header, or a digest mismatch | request fails verification | `[source-verified]` |
| `attributedTo` on another origin, or an array | `Create` / `Update` rejected | `[source-verified]` |
| Category id on another origin than the actor | rejected with an origin-mismatch error | `[source-verified]` |
| Announce with no local followers | rejected | `[source-verified]` |
| Delivery returns non-2xx | recorded as a failed send with status and body | `[source-verified]` |
| Retry schedule and dead-destination handling | not read | `[unverified]` |

### Examples

> Unknown: no captured or constructed signed delivery has been added yet. A useful one is an RFC 9421-signed `Create` followed by the draft-signed retry of the same activity.

## Sources

- [NodeBB repository](https://github.com/NodeBB/NodeBB) — source read at commit `b04f482eb068e9421bed35c335232164a27fc5b5`
- [NodeBB FEP positions](https://docs.nodebb.org/activitypub/fep/) — upstream list of proposals, positions and implementation state
