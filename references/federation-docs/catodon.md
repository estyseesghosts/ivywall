# Catodon FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Catodon maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Catodon does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [codefloe.com/catodon/catodon](https://codefloe.com/catodon/catodon) |
| Studied at commit | `a7319c535ecc4ac0bcb3727637e1f42749019d18` (2026-11-11) |
| Status | Not fact-checked against source (`[hypothesis]` until verified). Headings demoted two levels so they nest under this page. |

When the project changes, the document needs re-checking against the new source; update the commit above when it is.

## Document

### Federation

#### Supported federation protocols and standards

- [ActivityPub](https://www.w3.org/TR/activitypub/) (server-to-server; optional client-to-server API)
- [WebFinger](https://webfinger.net/)
- [HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) and [HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
- [NodeInfo](https://nodeinfo.diaspora.software/)

#### Supported FEPs

- [FEP-67ff: FEDERATION.md](https://codeberg.org/fediverse/fep/src/branch/main/fep/67ff/fep-67ff.md)
- [FEP-044f: Consent-respecting quote posts](https://codeberg.org/fediverse/fep/src/branch/main/fep/044f/fep-044f.md): quote policies, requests and authorization stamps.
- [FEP-1b12: Group federation](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md): forum Group actors and relayed activities.
- [FEP-7888](https://codeberg.org/fediverse/fep/src/branch/main/fep/7888/fep-7888.md): preserves an external conversation `context` identifier when rendering a post; it does not advertise local collection URIs for this purpose.
- [FEP-4f05](https://codeberg.org/fediverse/fep/src/branch/main/fep/4f05/fep-4f05.md): emits a forum `Announce(Undo(Delete))` when restoring a moderator-removed post; receivers without this behavior may retain the tombstone.
- [FEP-e232](https://codeberg.org/fediverse/fep/src/branch/main/fep/e232/fep-e232.md): reads and emits the legacy Misskey quote link in `tag`, alongside newer quote handling.
- [FEP-2677: Identifying the Application Actor](https://codeberg.org/fediverse/fep/src/branch/main/fep/2677/fep-2677.md): the application actor is linked from NodeInfo discovery.
- [FEP-5feb: Search indexing consent for actors](https://codeberg.org/fediverse/fep/src/branch/main/fep/5feb/fep-5feb.md): respects remote actors' indexing preference.
- [FEP-8a8e: ActivityPub Events](https://codeberg.org/fediverse/fep/src/branch/main/fep/8a8e/fep-8a8e.md): events and attendance, including Join and Leave.
- [FEP-b2b8: Long-form Text](https://codeberg.org/fediverse/fep/src/branch/main/fep/b2b8/fep-b2b8.md): Article posts.
- [FEP-ee3a: EXIF metadata](https://codeberg.org/fediverse/fep/src/branch/main/fep/ee3a/fep-ee3a.md): image metadata a user chooses to share.
- [FEP-5837: Content provenance](https://codeberg.org/fediverse/fep/src/branch/main/fep/5837/fep-5837.md): reads and sends digital source types; content credentials are read only.
- [FEP-d8c2: Client identification](https://codeberg.org/fediverse/fep/src/branch/main/fep/d8c2/fep-d8c2.md): ActivityPub Application objects can identify OAuth clients.

#### ActivityPub in Catodon

Catodon federates posts, profiles, forums, events and other activities using ActivityPub. The optional client-to-server API is documented separately, including its supported operations and differences: [ActivityPub client-to-server compatibility](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/activitypub-c2s/COMPATIBILITY.md).

##### WebFinger

Catodon exposes WebFinger for local account discovery. See the [well-known server](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/WellKnownServerService.ts).

##### HTTP Signatures

Catodon verifies both draft HTTP Signatures and RFC 9421 signatures on inbox requests. Signing outgoing GET requests and requiring signatures on GET requests are configurable. See the [ActivityPub server](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/ActivityPubServerService.ts), [inbox processor](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/queue/processors/InboxProcessorService.ts) and [configuration](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/config.ts).

##### Optional extensions

Catodon handles `RsaSignature2017` linked-data signatures, including for relayed activities. See [JSON-LD signature handling](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/JsonLdService.ts).

##### Additional documentation

- [Catodon documentation](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/docs/)
- [ActivityPub implementation](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/)


##### Actors, content and interoperability

Catodon represents accounts as ActivityPub actors and exchanges posts, replies, reposts, reactions, polls, follows, blocks and reports. Forums use `Group` actors and relay member activities; forum moderation and restoration have their own semantics. The [ActivityPub implementation](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/) and [inbox handling](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/queue/processors/InboxProcessorService.ts) specify which combinations are accepted.

For quote posts Catodon can advertise a policy, request authorization, verify dereferenced authorization stamps, and process acceptance or rejection. It also understands older quote forms for interoperability. A received authorization is not trusted merely because it is embedded in a post. See [quote handling](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/QuotePolicyService.ts) and [post parsing](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/activitypub/models/ApNoteService.ts).

Events contain dates, places, status and attendance information. Public upcoming events are exposed through a collection; the attendance protocol and fields vary by peer. The [events federation guide](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/docs/events-federation.md) documents the mappings, privacy, compatibility exceptions and limitations. Long-form `Article` posts use the [blog publishing implementation](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/core/BlogPublishService.ts). Place search, location privacy, opt-in EXIF and content provenance are detailed in the [Nearby federation guide](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/docs/nearby-federation.md).

##### Client-to-server API

The optional ActivityPub client API exposes OAuth discovery and selected outbox operations and collections. It is controlled by server policy; accepted operations, scopes, authorization and unsupported addressing are documented in the [client API guide](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/docs/activitypub-client-api.md) and [compatibility matrix](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/activitypub-c2s/COMPATIBILITY.md). URL-identified OAuth clients may also use an ActivityPub `Application` or `Service` as described there.

#### Size limits

| Limited property | Size limit | Consequence |
| --- | --- | --- |
| Shared and per-user inbox request body | 64 KiB | Request rejected by the HTTP server |

Other validation, media, event, place and configuration limits apply independently. See the [server routes](https://codefloe.com/catodon/catodon/src/commit/a7319c535ecc4ac0bcb3727637e1f42749019d18/packages/backend/src/server/ActivityPubServerService.ts) and the linked guides.

## Sources

- [Catodon repository](https://codefloe.com/catodon/catodon) — source the document was written from, at commit `a7319c535ecc4ac0bcb3727637e1f42749019d18`
