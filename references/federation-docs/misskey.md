# Misskey FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Misskey maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Misskey does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [github.com/misskey-dev/misskey](https://github.com/misskey-dev/misskey) |
| Studied at commit | `5163caea120c901017eb52da17332939d527b8f2` (2026-11-11) |
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

#### ActivityPub in Misskey

Misskey federates accounts, notes and interactions using ActivityPub. Its ActivityPub vocabulary includes Misskey-specific extensions; peers should not assume every Misskey feature has a direct equivalent in other software.

- [ActivityPub extensions](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/docs/contributing/activitypub.md)
- [ActivityPub types](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/type.ts)

##### WebFinger and HTTP Signatures

Misskey exposes WebFinger for actor discovery and NodeInfo 2.0 and 2.1 for server metadata. Inbox requests require an HTTP signature covering `(request-target)`, `host`, `date` and `digest`; outbound signatures use `rsa-sha256`.

- [Discovery endpoints](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/server/WellKnownServerService.ts)
- [Inbox implementation](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/server/ActivityPubServerService.ts)
- [Signed requests](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRequestService.ts)

##### Optional extensions

Misskey implements `RsaSignature2017` Linked Data Signatures for activities.

- [Linked Data signature implementation](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/JsonLdService.ts)

#### Size limits

| Limited property | Size limit | Consequence of exceeding the limit |
| --- | --- | --- |
| Inbox request body | 64 KiB | Request is rejected |

The limit applies to both the shared inbox and per-user inbox. Other limits apply to imported objects and attachments.

##### Endpoints and supported activity types

The shared inbox is `POST /inbox`; `POST /users/{user}/inbox` uses the same handler. Actor and note URLs include `/users/{user}` and `/notes/{note}`; ActivityPub representations are selected by content negotiation. Actor endpoints also expose public keys and featured collections. The authoritative routes are in [ActivityPubServerService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/server/ActivityPubServerService.ts).

The [inbox dispatcher](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts) handles `Create`, `Delete`, `Update`, `Follow`, `Accept`, `Reject`, `Add`, `Remove`, `Announce`, `Like`, `Undo`, `Block`, `Flag`, and `Move`, subject to object type and authorization checks. `Undo` handling includes follows, blocks, likes and announces. Support for an activity type does not imply support for every possible object. Notes, attachments, mentions, polls and emoji reactions use the structures and extensions in the [ActivityPub types](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/type.ts) and [renderers](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRendererService.ts).

##### Authentication and delivery

The inbox checks a SHA-256 body digest and the signed host; its host must match the configured host. Signature parsing and digest checks occur at the HTTP endpoint, and key resolution and cryptographic verification occur in the queued [inbox processor](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/queue/processors/InboxProcessorService.ts). The processor also handles embedded `RsaSignature2017` signatures when processing relayed activities; it checks the author and signer relationship. POST signatures use `(request-target)`, `date`, `host`, and `digest`; signed GETs omit the body digest. See [request signing](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRequestService.ts).

Misskey-specific properties such as `_misskey_quote`, `_misskey_reaction`, and `_misskey_votes` are defined in the [JSON-LD context](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/misc/contexts.ts). Consumers should treat extensions as optional: older releases and other software may omit them. Discovery, delivery, visibility, moderation, and supported content are affected by server settings.

##### Additional documentation

- [Inbox activity processing](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts)
- [Remote object resolution](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApResolverService.ts)
- [ActivityPub payload contribution guide](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/docs/contributing/activitypub.md)

## Sources

- [Misskey repository](https://github.com/misskey-dev/misskey) — source the document was written from, at commit `5163caea120c901017eb52da17332939d527b8f2`
