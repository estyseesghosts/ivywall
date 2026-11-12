# Pixelfed FEDERATION.md (community-written)

> **Disclaimer.** This document was **not written by the Pixelfed maintainers**. It was written for this wiki, following the `FEDERATION.md` convention, from studying the project's source at the commit below. It may be incomplete or inaccurate. Do not treat it as the project's own statement, and do not cite it as one. Where it matters, verify against the source.

Pixelfed does not publish a `FEDERATION.md` of its own. This page holds the wiki's copy of the one written for it, so it can be read and searched alongside the documents the projects publish themselves (see the [index](index.md)).

## Document details

| Field | Value |
| ----- | ----- |
| Author | Written for this wiki, not by upstream |
| Repository studied | [github.com/pixelfed/pixelfed](https://github.com/pixelfed/pixelfed) |
| Studied at commit | `2731e6999d47e1dcf05c0d931cae2f1b88e349d1` (2026-11-10) |
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
- [FEP-8fcf: Followers collection synchronization across servers](https://codeberg.org/fediverse/fep/src/branch/main/fep/8fcf/fep-8fcf.md): sends and processes collection synchronization information.
- [FEP-044f: Consent-respecting quote posts](https://codeberg.org/fediverse/fep/src/branch/main/fep/044f/fep-044f.md): implements quote requests and authorization.
- [FEP-6757](https://codeberg.org/fediverse/fep/src/branch/main/fep/6757/fep-6757.md): handles license information on actors and content.
- [FEP-070c](https://codeberg.org/fediverse/fep/src/branch/main/fep/070c/fep-070c.md): block synchronization, subject to configuration.
- [FEP-7aa9](https://codeberg.org/fediverse/fep/src/branch/main/fep/7aa9/fep-7aa9.md): featured collection authorization, with automatic approval.
- [FEP-5837](https://codeberg.org/fediverse/fep/src/branch/main/fep/5837/fep-5837.md): content provenance metadata, subject to configuration and driver availability.

#### ActivityPub in Pixelfed

Pixelfed uses ActivityPub to exchange actors, posts, media and interactions. Federation behavior depends on server configuration.

- [ActivityPub implementation](https://github.com/pixelfed/pixelfed/tree/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/)
- [Federation routes](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/routes/api.php)
- [Federation configuration](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php)

##### WebFinger and HTTP Signatures

Pixelfed exposes WebFinger and NodeInfo discovery endpoints. It signs outgoing ActivityPub deliveries and validates signatures on inbound federation requests. Signed fetching is supported for protected resources.

- [Federation controller](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Http/Controllers/FederationController.php)
- [Delivery service](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/ActivityPubDeliveryService.php)
- [Signed fetch verification](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/ActivityPubSignedFetchService.php)

##### Optional extensions

Followers synchronization and quote authorization use the mechanisms described in FEP-8fcf and FEP-044f. Support for media licenses uses the vocabulary described in FEP-6757.

- [Followers synchronization](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/FollowersSyncService.php)
- [Quote service](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/QuoteService.php)
- [Media licenses](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/Media/License.php)

#### Size limits

| Limited property | Size limit | Consequence of exceeding the limit |
| --- | --- | --- |
| Fetched ActivityPub response | 2 MiB | Fetch is rejected |

Media and local post limits are separately configurable.

##### Endpoints and processing

Federation is controlled by `ACTIVITY_PUB` (default `false` in the checked-in configuration); inbox, shared inbox, outbox, WebFinger and NodeInfo can be configured separately. The [federation configuration](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php) is authoritative for defaults and related settings. The [routes](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/routes/api.php) and [federation controller](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Http/Controllers/FederationController.php) expose actor and object representations, inboxes, collections and discovery. ActivityPub representations depend on content negotiation and visibility; applications should discover actor inboxes from actor documents rather than construct delivery URLs.

The inbox is queued. The [inbox worker](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Jobs/InboxPipeline/InboxWorker.php) requires a signature and date, checks that the activity ID and actor are valid and on the signing key's host, resolves the signing actor, and verifies the signature before dispatching. It rejects dates outside a one-day window and deduplicates processed activity IDs. Other inbox paths and activity-specific checks are in the [inbox pipeline](https://github.com/pixelfed/pixelfed/tree/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Jobs/InboxPipeline/) and [handlers](https://github.com/pixelfed/pixelfed/tree/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/Inbox/). The [delivery service](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/ActivityPubDeliveryService.php) signs deliveries and uses per-host retry/backoff configuration. Actor, object, and audience validation still apply after authentication.

##### Additional extensions

- [FEP-070c: Block synchronization](https://codeberg.org/fediverse/fep/src/branch/main/fep/070c/fep-070c.md): [block synchronization](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/BlockSyncService.php) receives and reconciles block digests and can disclose its synchronization endpoint. `AP_BLOCK_SYNC` and `AP_BLOCK_SYNC_DISCLOSE` control these behaviors.
- [FEP-7aa9](https://codeberg.org/fediverse/fep/src/branch/main/fep/7aa9/fep-7aa9.md): [featured collection authorization](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/FeaturedCollectionService.php) exposes `canFeature` policies and authorization stamps; the implementation documents automatic approval only.
- [FEP-5837: Content provenance](https://codeberg.org/fediverse/fep/src/branch/main/fep/5837/fep-5837.md): [content credentials](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Services/ContentCredentials/ContentCredentialService.php) support digital source type and credential metadata, with inspection and signing dependent on configuration and an available C2PA driver.

The followers synchronization implementation is configurable: signed `Collection-Synchronization` headers on followers-only delivery, partial collection access, and inbound reconciliation can be disabled. Block synchronization has independent settings. Quote and feature policies can restrict interactions, so callers must handle authorization failures.

##### Additional documentation

- [Federation routes](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/routes/api.php)
- [ActivityPub implementation](https://github.com/pixelfed/pixelfed/tree/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/app/Util/ActivityPub/)
- [Federation tests](https://github.com/pixelfed/pixelfed/tree/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/tests/Feature/Federation/)
- [Federation configuration](https://github.com/pixelfed/pixelfed/blob/2731e6999d47e1dcf05c0d931cae2f1b88e349d1/config/federation.php)

## Sources

- [Pixelfed repository](https://github.com/pixelfed/pixelfed) — source the document was written from, at commit `2731e6999d47e1dcf05c0d931cae2f1b88e349d1`
