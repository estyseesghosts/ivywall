# Lemmy FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Lemmy maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Lemmy does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [github.com/lemmynet/lemmy](https://github.com/lemmynet/lemmy) |
| Studied at commit | `dae30ee5f41836a2e468cd61e9c184dfe0717aa9` (2026-11-10) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server)
- [WebFinger](https://webfinger.net/)
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures)
- [NodeInfo](https://nodeinfo.diaspora.software/)

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)
- [FEP-fe34](https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md): the moderation authorization code references a specific trust rule from this proposal; this is not a claim of full implementation.

#### ActivityPub in Lemmy

Lemmy uses ActivityPub to federate users, communities, posts, comments, votes and moderation actions. Communities are represented by `Group` actors; posts and comments are distinct objects. Community activities and private communities have additional handling beyond a general microblogging implementation.

- [ActivityPub objects](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/protocol/)
- [ActivityPub activities](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/)

##### WebFinger and HTTP Signatures

WebFinger resolves local users and communities, as well as the instance actor. Lemmy uses HTTP signatures to authenticate federation requests. Federation can be disabled by the instance administrator.

- [WebFinger endpoint](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/routes/src/webfinger.rs)
- [Federation implementation](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/)
- [NodeInfo endpoint](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/routes/src/nodeinfo.rs)

#### Size limits

Federated post titles are truncated to 200 characters when imported. Other validation and instance configuration can also affect accepted content.

- [Post import](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/objects/post.rs)

##### Endpoints and objects

The [ActivityPub routes](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/routes.rs) expose `/inbox` as the shared inbox, user actors at `/u/{name}`, community actors at `/c/{name}`, posts at `/post/{post_id}`, comments at `/comment/{comment_id}`, and actor outboxes and community collections. Fetch representations with ActivityPub content negotiation; HTML routes may share these URLs. Activity IDs are served under `/activities/{type}/{id}` when the activity is not sensitive.

`Person` actors represent users and `Group` actors represent communities. The community is central to a post or comment's audience: a community can announce activities to its followers. The [activity list](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/activity_lists.rs) handles follows, accepts, rejects and undo follows; creates and updates of posts and comments; votes and undo votes; deletes and undo deletes; and community moderation, including blocks, collection changes, locks and reports. This list is not a promise to accept arbitrary combinations of activity and object types. The [protocol types](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/protocol/) and [object types](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/protocol/) define the payloads.

Private community content fetches require a signed request and an authorized follower relationship; local-only communities are not federated. See [fetch authorization](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/mod.rs). Incoming activities are deduplicated by ID; the shared inbox applies a nine-second processing timeout. The ActivityPub library handles signature verification and request signing; a successful signature does not bypass the per-activity authorization and community membership checks.

##### Moderation extension

The [moderation authorization code](https://github.com/lemmynet/lemmy/blob/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/objects/src/utils/functions.rs) references [FEP-fe34](https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md): it trusts moderation actions from the community's or object's origin instance, and checks other actors against community moderator or administrator membership and bans. This is a specific authorization rule, not a claim of complete FEP implementation.

##### Additional documentation

- [ActivityPub HTTP endpoints](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/src/http/)
- [ActivityPub activity handling](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/activities/src/)
- [ActivityPub test fixtures](https://github.com/lemmynet/lemmy/tree/dae30ee5f41836a2e468cd61e9c184dfe0717aa9/crates/apub/apub/assets/)

## Sources

- [Lemmy repository](https://github.com/lemmynet/lemmy) — source the document was written from, at commit `dae30ee5f41836a2e468cd61e9c184dfe0717aa9`
