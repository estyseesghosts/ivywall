# Lemmy federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the Lemmy maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean Lemmy conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [github.com/lemmynet/lemmy](https://github.com/lemmynet/lemmy) |
| Release basis | Development snapshot: 11 commits after `1.0.0-beta.3`, which is a pre-release of the 1.0 line. |
| Commit | `dae30ee5f41836a2e468cd61e9c184dfe0717aa9` (2026-11-10) |
| Other wiki revisions | The [Lemmy case study](../../servers/case-studies/lemmy.md) and [fact sheet](../software/lemmy.md) pin release 0.19.21 (`2ff971f`), an earlier line with a different activity set. Do not combine this page's findings with that study without checking the differences. |
| Verification | Partial. `[source-verified]` items were read at this commit. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; shared inbox `/inbox`, actor inboxes; communities are `Group` actors | `[source-verified]` [routes](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/routes.rs) |
| WebFinger | serves and resolves users, communities and the instance actor | `[source-verified]` [webfinger.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/routes/src/webfinger.rs) |
| HTTP signatures | signs outgoing requests and verifies incoming ones through the `activitypub_federation` library | `[inferred]` library behaviour not read here |
| NodeInfo | served | `[source-verified]` [nodeinfo.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/routes/src/nodeinfo.rs) |

### Supported FEPs

| FEP | Support | Evidence |
| --- | ------- | -------- |
| FEP-fe34 (origin-based security) | **partial**: one rule only. A moderation action is trusted without a membership check when the moderator's domain equals the community's domain or the moderated object's domain; otherwise the moderator must be a community moderator or admin and not banned from the community. This is the only fe34-related logic found; it is not a claim of full implementation. | `[source-verified]` [`verify_mod_action`](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/utils/functions.rs) cites the FEP in a comment |

No other FEP support was established. An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer at the top of this page) and has been removed.

### Discovery

- Shared inbox `/inbox`; users `/u/{name}`; communities `/c/{name}`; posts `/post/{post_id}`; comments `/comment/{comment_id}`; outboxes and community collections; activity ids served under `/activities/{type}/{id}` when the activity is not sensitive. `[source-verified]` [routes.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/routes.rs)
- HTML routes can share these URLs; ActivityPub content negotiation selects the representation. `[source-verified]` same file.

### Authentication

Incoming and outgoing signature handling is done by the ActivityPub library. A valid signature does not bypass per-activity authorization or community membership checks. `[inferred]`; the request path is in [`http/mod.rs`](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/mod.rs). Fetching posts and comments of a **private** community requires a signed request: for a local community the signing actor's instance must have a follower of the community; for a remote community Lemmy asks the community's followers URL with `is_follower=<actor>` using a signed request. Communities with local-only visibility return not found to remote fetches. `[source-verified]` [`check_community_content_fetchable`](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/mod.rs)

### Community redistribution contract

A community actor receives activities from members and redistributes them to its followers wrapped in `Announce`.

1. A member's server sends an activity (for example `Create(Page)`) to the community inbox or the shared inbox. It is parsed as `RawAnnouncableActivities`, the community is found from the activity, the community must accept activity, the activity is verified and applied, and, when the community is local, the sender's membership of the community is checked. `[source-verified]` [announce.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/community/announce.rs)
2. If the community is local, Lemmy then sends an `Announce` whose `object` is the original activity to the community's followers. `[source-verified]` same file.
3. A remote community's `Announce` is accepted only if the `Announce` actor URL equals the community URL, its `to`/`cc` match the community's visibility, and the community accepts the activity. `[source-verified]` same file.
4. `Page` sent by Lemmy for Mastodon/Pleroma compatibility can be sent but is rejected when received. `[source-verified]` same file.

Example (copied from the repository's test fixtures at this commit, not captured from a live server):

```json
{
  "actor": "http://enterprise.lemmy.ml/c/main",
  "to": ["https://www.w3.org/ns/activitystreams#Public"],
  "object": {
    "actor": "http://enterprise.lemmy.ml/u/lemmy_beta",
    "type": "Create",
    "to": ["https://www.w3.org/ns/activitystreams#Public"],
    "cc": ["http://enterprise.lemmy.ml/c/main"],
    "object": { "type": "Page", "id": "http://enterprise.lemmy.ml/post/7", "name": "post 4" },
    "id": "http://enterprise.lemmy.ml/activities/create/2807c9ec-3ad8-4859-a9e0-28b59b6e499f"
  },
  "cc": ["http://enterprise.lemmy.ml/c/main/followers"],
  "type": "Announce",
  "id": "http://enterprise.lemmy.ml/activities/announce/8030b171-803a-4108-94b1-342688f375cf"
}
```

The fixture's inner object is abbreviated here; the full file is [`announce_create_page.json`](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/assets/lemmy/activities/community/announce_create_page.json).

### Activity and object matrix

The shared inbox accepts directly: `Follow`, `Accept(Follow)`, `Reject(Follow)`, `Undo(Follow)`, `Report`, `ResolveReport`, `Announce`, and a catch-all for announcable activities. `[source-verified]` [activity_lists.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/activity_lists.rs). Announcable activities (received inside an `Announce`, or directly at a community for redistribution):

| Activity | Object | Meaning | Who may send | Evidence |
| -------- | ------ | ------- | ------------ | -------- |
| `Create` / `Update` | `Page` | post | a member of the community | `[source-verified]` |
| `Create` / `Update` | `Note` (also private-message form) | comment, or private message | a member; private messages are routed outside communities | `[source-verified]` |
| `Like` / `Dislike` and `Undo` | post or comment | vote (`Vote` has `Like` and `Dislike` types) | a member | `[source-verified]` |
| `Delete` / `Undo(Delete)` | `Tombstone` | with `summary` present it is a moderator removal; without it, a user deleting their own content; `removeData` and `withReplies` are nonstandard flags | author, or a moderator for removal | `[source-verified]` [delete.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/protocol/deletion/delete.rs) |
| `Update` | `Group` or feed | community settings | moderator | `[source-verified]` |
| `Block` / `Undo(Block)` | person, `target` = site or community | ban; `endTime`, `summary`, `removeData` | moderator or admin | `[source-verified]` |
| `Add` / `Remove` | `object` URL, `target` URL | collection changes: featured posts and moderators | moderator | `[source-verified]` |
| `Lock` / `Undo(Lock)` | post or comment | lock for replies, with `summary` | moderator | `[source-verified]` |
| `Flag` (`Report`) / `Resolve` | post, comment, or other | report and its resolution | member; sent to site or community | `[source-verified]` |
| `Warn` | post or comment | warning addressed to one person with `summary` | moderator | `[source-verified]` |
| `Page` (bare) | | compatibility form for Mastodon/Pleroma | send only; rejected when received | `[source-verified]` |

Who may send a moderation action: the moderator's domain must match the community or the moderated object (trusted as origin, the FEP-fe34 rule above), otherwise the actor must be a community moderator or admin and not community-banned. A site ban does not stop a moderator (the code cites an upstream issue). `[source-verified]` [`verify_mod_action`](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/utils/functions.rs)

A list of activity names does not promise any combination of activity and object is accepted; the payload types decide: [activities](https://github.com/LemmyNet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/protocol/), [objects](https://github.com/LemmyNet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/protocol/).

### Distinctive behaviour

- Lemmy-specific fields on standard activities: `Delete.summary`, `Delete.removeData`, `Delete.withReplies`, `Block.removeData`, `Block.endTime`, and an `audience` property naming the community. `[source-verified]` protocol structs above.
- Imported post titles are truncated to 200 characters (`MAX_TITLE_LENGTH`). `[source-verified]` [post.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/objects/post.rs)

### Operational behaviour

- Incoming activities are deduplicated by activity id. `[unverified]` the dedup check was not located in this pass.
- The shared inbox processes an incoming activity within a 9-second timeout; the code comment says a longer wait would make the sender mark this instance dead, so it times out first. `[source-verified]` [`INCOMING_ACTIVITY_TIMEOUT`](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/mod.rs)

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| `Announce` actor is not the community | rejected (URL mismatch) | `[source-verified]` |
| Community does not accept activity (for example deleted, or visibility mismatch) | rejected | `[source-verified]` |
| Sender not a member of a local community | rejected (membership is checked for local communities, after the activity has been verified and applied) | `[source-verified]` |
| Moderator without rights | rejected | `[source-verified]` |
| Private community fetch without follower relationship | error | `[source-verified]` |
| Local-only community fetched remotely | not found | `[source-verified]` |
| Processing exceeds 9 seconds | request times out | `[source-verified]` |
| Signature failures and unknown-actor handling | not read | `[unverified]` |

## Sources

- [Lemmy repository](https://github.com/lemmynet/lemmy) — source read at commit `dae30ee5f41836a2e468cd61e9c184dfe0717aa9`
- [activity_lists.rs](https://github.com/LemmyNet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/activity_lists.rs) — shared inbox and announcable activity lists
- [Test fixtures](https://github.com/LemmyNet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/assets/lemmy/) — representative activity JSON
