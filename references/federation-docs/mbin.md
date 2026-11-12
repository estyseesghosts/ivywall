# Mbin FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Mbin maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Mbin does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [github.com/MbinOrg/mbin](https://github.com/MbinOrg/mbin) |
| Studied at commit | `6d04519c09ce4b42acf791359e770c7fff5d4840` (2026-11-10) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server)
- [WebFinger](https://webfinger.net/)
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures)
- [NodeInfo](https://nodeinfo.diaspora.software/) 2.0 and 2.1

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)
- [FEP-1b12: Group federation](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md): Mbin federates magazine groups. See the [federation developer documentation](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/05-fediverse_developers/README.md).

#### ActivityPub in Mbin

Mbin federates user and magazine actors, posts, comments and interactions. It provides individual user and magazine inboxes as well as a shared inbox. See the [ActivityPub controllers](https://github.com/MbinOrg/mbin/tree/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Controller/ActivityPub/) and [federation developer documentation](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/05-fediverse_developers/README.md).

##### WebFinger

WebFinger resolves both user and magazine actors. See the [user](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/EventSubscriber/ActivityPub/UserWebFingerSubscriber.php) and [group](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/EventSubscriber/ActivityPub/GroupWebFingerSubscriber.php) subscribers.

##### HTTP Signatures

Mbin signs outgoing ActivityPub requests with RSA-SHA256 HTTP Signatures. Inbox validation requires `Signature` and `Date` headers, verifies the signature with the actor public key and checks a supplied digest. The validator currently leaves Date freshness verification as a TODO. It checks the domains of the signing key, activity ID and actor; apparent forwarded activities take a separate path. See the [HTTP client](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/ApHttpClient.php) and [signature validator](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/SignatureValidator.php).

##### Additional documentation

- [Mbin documentation](https://github.com/MbinOrg/mbin/tree/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/)

##### Actors and collections

The application actor is available at `/i/actor`, local users at `/u/{username}`, and magazines as `Group` actors at `/m/{name}`. The user outbox, followers and following and magazine collections are described with representative payloads in the [federation developer documentation](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/05-fediverse_developers/README.md). That document notes that the magazine outbox currently returns an empty object, magazine followers disclose a count rather than items, and moderator and featured collections are not paginated.

##### Activities and group federation

Users can follow users or magazines; a local user automatically accepts follows. Content creation, updates, deletes, likes and undo, reposts and reports are federated. The developer documentation describes moderator actions including adding or removing moderators, pinning, locking and removing content, and magazine bans. Magazines announce activities addressed to them, including relevant moderation activities, to their audience. `Announce(Flag)` is directed only to servers with moderators of the magazine. See the [federation developer documentation](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/05-fediverse_developers/README.md) for activity and object shapes; it also states that down-votes are not federated.

##### Validation and delivery

Mbin validates URLs in the key ID and activity ID, checks host relationships, resolves the actor's public key and verifies the signed headers. An apparent forwarded activity is handled separately rather than treated as an ordinary activity from the forwarder. The exact decision is in [SignatureValidator](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/SignatureValidator.php). The HTTP client signs outgoing requests; see [ApHttpClient](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/ApHttpClient.php). Local configuration and visibility affect whether a given actor or collection is available.

## Sources

- [Mbin repository](https://github.com/MbinOrg/mbin) — source the document was written from, at commit `6d04519c09ce4b42acf791359e770c7fff5d4840`
