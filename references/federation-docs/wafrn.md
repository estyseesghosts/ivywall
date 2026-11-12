# Wafrn FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Wafrn maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Wafrn does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [codeberg.org/wafrn/wafrn](https://codeberg.org/wafrn/wafrn) |
| Studied at commit | `f2bdd67849f44227d932c9ed0aa91b6af06d512d` (2026-11-05) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server)
- [WebFinger](https://webfinger.net/)
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures)
- [NodeInfo](https://nodeinfo.diaspora.software/) 2.0

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)
- [FEP-044f: Consent-respecting quote posts](https://codeberg.org/fediverse/fep/src/branch/main/fep/044f/fep-044f.md): sends and handles `QuoteRequest`, issues an `Accept` and exposes a `QuoteAuthorization`; rejection is not implemented in the incoming handler.
- [FEP-fffd](https://codeberg.org/fediverse/fep/src/branch/main/fep/fffd/fep-fffd.md): reads a linked `at://` URL to associate a Bridgy/AT Protocol post with its counterpart when Bluesky lookup is enabled.
- [FEP-6fce: Interaction Policies](https://codeberg.org/fediverse/fep/src/branch/main/fep/6fce/fep-6fce.md): supports reply and announce requests and authorization for manual approval.

#### ActivityPub in Wafrn

Wafrn exchanges ActivityPub activities with remote servers. Its inbox handles posts and replies, follows, reblogs, likes, updates and deletions, among other activities. See the [inbox processor](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts) and [ActivityPub routes](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/routes/activitypub/activitypub.ts) for the supported activity handling.

##### WebFinger

Wafrn exposes WebFinger for discovery of local accounts and a NodeInfo 2.0 endpoint. See the [well-known routes](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/routes/activitypub/well-known.ts).

##### HTTP Signatures

Outgoing ActivityPub POST requests use RSA-SHA256 HTTP Signatures and a SHA-256 digest, signing `(request-target)`, `host`, `date` and `digest`. The inbound middleware checks those fields for POSTs, allows one hour of clock skew, checks the digest and binds the signing actor to the activity actor; signature enforcement depends on the route. It also has a `RsaSignature2017` verification path for signed activities. See [outbound signing](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/activitypub/postPetitionSigned.ts) and [signature verification](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/activitypub/checkFediverseSignature.ts).

##### Additional documentation

- [Wafrn documentation](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/docs/)

##### Actors, collections and delivery

Local actor documents are served at `/fediverse/blog/:url`. Following and followers are exposed as paginated collections, subject to the account's visibility settings. ActivityPub content negotiation, deleted accounts, and access checks affect the response; see the [routes](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/routes/activitypub/activitypub.ts). Post objects and replies are served under `/fediverse/post/`.

The [inbox processor](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/inbox.ts) dispatches `Accept`, `Reject`, `Announce`, `Create`, `Follow`, `Update`, `Undo`, `Like`, `Delete`, `EmojiReact`, `Remove`, `Add`, `Block`, `Move`, `Flag`, quote requests and interaction requests. Handling a type does not imply every object or policy is supported. `ReplyRequest` and `AnnounceRequest` for manual-approval policies are answered automatically according to the existing interaction rules; there is no manual review in those handlers. Request and authorization objects can be dereferenced on the routes above.

The [post import](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/activitypub/getPostThreadRecursive.ts) and [outbound preparation](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/queueProcessors/prepareSendRemotePost.ts) contain the detailed mappings and recipient rules. Administrators should consult the [configuration](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/environment.example.ts) and deployment documentation for instance-specific behavior.

## Sources

- [Wafrn repository](https://codeberg.org/wafrn/wafrn) — source the document was written from, at commit `f2bdd67849f44227d932c9ed0aa91b6af06d512d`
