# NodeBB FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the NodeBB maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

NodeBB does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [github.com/NodeBB/NodeBB](https://github.com/NodeBB/NodeBB) |
| Studied at commit | `b04f482eb068e9421bed35c335232164a27fc5b5` (2026-11-11) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server)
- [WebFinger](https://webfinger.net/)
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) and [HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
- [NodeInfo](https://nodeinfo.diaspora.software/) 2.0

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)
- [FEP-1b12: Group federation](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md): category actors announce activities to their followers and relays; main posts also produce an announcement of the plain object. See [group forwarding](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/feps.js).
- [FEP-3b86: Activity Intents](https://codeberg.org/fediverse/fep/src/branch/main/fep/3b86/fep-3b86.md): advertises Object, Create, Like, Dislike and Follow templates in user WebFinger responses, and reads remote intent templates.
- [FEP-fb2a](https://codeberg.org/fediverse/fep/src/branch/main/fep/fb2a/fep-fb2a.md): imports account metadata in `Note` and `Link` attachments as well as legacy `PropertyValue` fields.
- [FEP-baf5: Administrator Collection](https://codeberg.org/fediverse/fep/src/branch/main/fep/baf5/fep-baf5.md): the application actor links to its administrators.

#### ActivityPub in NodeBB

NodeBB can federate forum content and actors using ActivityPub. Federation is controlled by the server's configuration. The [ActivityPub implementation](https://github.com/NodeBB/NodeBB/tree/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/) and [controllers](https://github.com/NodeBB/NodeBB/tree/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/activitypub/) describe the supported objects and activities.

##### WebFinger

NodeBB exposes WebFinger for actor discovery and uses it to resolve remote handles. Remote actor verification includes a WebFinger backreference check, with handling for split domains. See [actor discovery](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/actors.js) and [WebFinger verification](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/helpers.js).

##### HTTP Signatures

NodeBB verifies both draft signatures and RFC 9421 signatures. For outbound POST delivery it first tries RFC 9421 and falls back to the draft signature if that attempt fails; other signed requests use the draft signing path. Requests with a body must carry a `Digest` or `Content-Digest`, and the digest must be covered by the signature. See [signature handling](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/signatures.js).

##### Additional documentation

- [NodeBB documentation](https://docs.nodebb.org/)

##### Actors and discovery

The application actor is at `/actor`; users are actors at `/uid/{uid}`, and federated categories are actors at `/category/{cid}`. WebFinger resolves users, categories and the application actor when enabled; user and category discovery also depends on local view privileges. The WebFinger response for a user advertises the supported intent templates. See [discovery](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/well-known.js), [actor rendering](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/activitypub/actors.js), and [remote actor lookup](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/actors.js).

##### Delivery and verification

For draft signatures NodeBB signs `(request-target)`, `host`, `date` and, when present, `digest`. The RFC 9421 delivery signature covers method, authority, target URI and date, plus content digest and content type for a body. The sender uses a 10-second POST timeout, does not follow redirects, and applies an SSRF destination check. See the [delivery worker](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/sendWorker.js) and [signature implementation](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/signatures.js).

ActivityPub controllers and handlers in [the source](https://github.com/NodeBB/NodeBB/tree/b04f482eb068e9421bed35c335232164a27fc5b5/src/controllers/activitypub/) and [activity processing](https://github.com/NodeBB/NodeBB/tree/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/) are authoritative for supported combinations of actor, activity, object and local permissions. Federation and category visibility are configurable; a peer should not assume every forum or local user is publicly discoverable.

The ActivityPub parser recognizes `Note`, `Page`, `Article`, `Question` and `Video` post types and `Person`, `Application`, `Organization`, `Service` and `Group` actors. Remote actors need an inbox. Accepted content types include `application/activity+json` and ActivityStreams-profiled JSON-LD; remote requests use HTTPS outside the CI test environment. See [ActivityPub constants](https://github.com/NodeBB/NodeBB/blob/b04f482eb068e9421bed35c335232164a27fc5b5/src/activitypub/index.js).

## Sources

- [NodeBB repository](https://github.com/NodeBB/NodeBB) — source the document was written from, at commit `b04f482eb068e9421bed35c335232164a27fc5b5`
