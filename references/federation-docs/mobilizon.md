# Mobilizon FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Mobilizon maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Mobilizon does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [framagit.org/kaihuri/mobilizon](https://framagit.org/kaihuri/mobilizon) |
| Studied at commit | `f2590486f6ee056f01fa05412a16f9a08c65357e` (2026-09-30) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server)
- [WebFinger](https://webfinger.net/) and host-meta for actor discovery
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures)
- [NodeInfo](https://nodeinfo.diaspora.software/)

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)

No other FEP is explicitly identified as implemented in this checkout. Similar vocabulary or behavior alone should not be taken as a claim of full conformance to a FEP.

#### ActivityPub in Mobilizon

Mobilizon federates events, people, groups, comments, posts and group membership. Federation is configurable by the instance administrator. The [ActivityPub routes](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/router.ex), [incoming activity handlers](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/transmogrifier.ex), and [publisher](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/publisher.ex) define the behavior described below. Activity and object type support is conditional on their combination and on validation; an activity name in this list does not imply support for every possible object.

##### Discovery and endpoints

- `/.well-known/webfinger` resolves local actors; `/.well-known/host-meta` advertises discovery information. Remote WebFinger discovery first looks for host-meta and falls back to the well-known WebFinger path. See [WebFinger](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/web_finger/web_finger.ex).
- `/.well-known/nodeinfo` advertises NodeInfo; `/.well-known/nodeinfo/:version` serves the versioned document.
- `/@{name}` serves actor data through ActivityPub content negotiation. Actor outbox, following, followers and members collections are under `/@{name}/outbox`, `/following`, `/followers` and `/members`.
- `POST /@{name}/inbox` and `POST /inbox` are the actor and shared inboxes. `/relay` exposes the relay actor and `/relay/inbox` its inbox. Event and comment URLs can also be requested as ActivityPub objects.

##### Activities and delivery

The inbox handlers include `Create` for `Note`, `Event`, `Article`, actors and `Member` objects, `Update` for events, notes, articles, members and actors, as well as `Delete`, `Follow`, `Accept`, `Reject`, `Announce`, `Undo`, `Join`, `Leave`, `Invite`, `Remove` and `Flag` in the cases implemented by the [transmogrifier](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/transmogrifier.ex). For example, `Undo` has specific handlers for follows and announces; it is not a general undo implementation. Group membership and events have application-specific semantics.

Inbound activities with a valid signature are queued for processing. For an actor inbox, the recipient must also be present in the message or otherwise satisfy the recipient check. For a `Create` without a valid author signature, the controller attempts to fetch the object from its source instead of trusting the submitted object; other activities without a valid signature are not queued by that path. A successful inbox response therefore does not by itself establish that the activity was ultimately applied. See [inbox handling](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/controllers/activity_pub_controller.ex).

Outgoing delivery expands follower and member collections to remote recipients, prefers each actor's shared inbox when available, deduplicates inbox URLs and queues one delivery per inbox. If relay support is enabled, public activities are addressed to relay followers and public `Create` activities are also published through the relay. See [publisher](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/publisher.ex).

##### HTTP Signatures

Outgoing inbox POSTs contain `application/activity+json`, a digest, date and HTTP signature. The signed fields include `(request-target)`, `host`, `content-length`, `digest` and `date`. Incoming inbox handling uses the result of signature verification as described above. A reverse proxy must preserve the host used for signature verification. See [publisher](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/publisher.ex), [signature code](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/http_signatures/signature.ex), and the [inbox controller](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/controllers/activity_pub_controller.ex).

##### Additional documentation

- [Federation implementation](https://framagit.org/kaihuri/mobilizon/-/tree/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/)
- [ActivityPub object and activity converters](https://framagit.org/kaihuri/mobilizon/-/tree/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/)
- [Web routes](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/router.ex)

## Sources

- [Mobilizon repository](https://framagit.org/kaihuri/mobilizon) — source the document was written from, at commit `f2590486f6ee056f01fa05412a16f9a08c65357e`
