# WriteFreely FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the WriteFreely maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

WriteFreely does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [github.com/writefreely/writefreely](https://github.com/writefreely/writefreely) |
| Studied at commit | `2bbe3c70b9f36180a9d10d5a1c31480648761ce0` (2026-11-11) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server)
- [WebFinger](https://webfinger.net/)
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) (outgoing requests)
- [NodeInfo](https://nodeinfo.diaspora.software/)

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)

No other FEP is explicitly identified as implemented in this checkout. Similar vocabulary or behavior alone should not be taken as a claim of full conformance to a FEP.

#### ActivityPub in WriteFreely

WriteFreely federates blogs as actors and publishes their posts to followers. Federation can be configured by the instance administrator; see [configuration](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/config/config.go). ActivityPub is a publication and follow interface here, not a complete general-purpose ActivityPub client or server implementation. See [ActivityPub implementation](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) for the precise behavior.

##### Discovery, actors and collections

`/.well-known/webfinger` resolves blog handles to an `application/activity+json` actor link. `/.well-known/nodeinfo` advertises the NodeInfo endpoint, `/api/nodeinfo`. Actor discovery and the actor's actual URL should be used rather than constructing the latter from a handle. See [WebFinger](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/webfinger.go), [NodeInfo](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/nodeinfo.go) and [routes](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/routes.go).

Blog actors expose inbox, outbox, followers and following URLs. The routes include `POST /api/collections/{alias}/inbox` and GET endpoints for the outbox, followers and following. The following collection is exposed as empty. The actor and outbox handlers do not expose private or protected blogs, or actors belonging to silenced users. The outbox is paginated. Single-user and multi-user installations can resolve actors differently, so clients should follow the URLs advertised by the actor.

##### Activities and delivery

Public posts are distributed using `Create`, `Update` and `Delete` activities. Delivery groups followers by inbox, preferring the remote actor's shared inbox and falling back to its individual inbox. See [ActivityPub delivery](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go).

The inbox resolver handles `Follow` and issues `Accept`, records `Like`, handles `Undo` for likes and follows, and has a `Delete` callback. Handling is limited to the code paths implemented by the resolver; for example the `Delete` callback returns a response and should not be assumed to perform general remote-object deletion. The `Undo` handler has specific like and unfollow logic, rather than a general-purpose undo implementation. See [the inbox handler](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go).

##### HTTP Signatures and remote fetching

Outgoing ActivityPub POSTs and object-fetch GETs use the legacy `Signature` header with RSA-SHA256, signing `(request-target)`, `date`, `host` and `digest`. The inbox handler in this checkout does not itself verify incoming HTTP signatures; outgoing signing must not be interpreted as proof that incoming activities are authenticated. Check any deployment-specific middleware separately.

The ActivityPub HTTP client has a 15-second timeout, limits redirect chains to fewer than five prior requests, and checks destination addresses when connecting. Remote WebFinger lookup also uses a restricted client. These affect reachability of peers on private networks as well as redirects; see [ActivityPub client](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go) and [WebFinger network checks](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/webfinger.go).

##### Additional documentation

- [ActivityPub implementation](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/activitypub.go)
- [WebFinger implementation](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/webfinger.go)
- [NodeInfo implementation](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/nodeinfo.go)
- [HTTP routes](https://github.com/writefreely/writefreely/blob/2bbe3c70b9f36180a9d10d5a1c31480648761ce0/routes.go)

## Sources

- [WriteFreely repository](https://github.com/writefreely/writefreely) — source the document was written from, at commit `2bbe3c70b9f36180a9d10d5a1c31480648761ce0`
