# Mastodon 4.7.3 federation trust boundaries

Federation accepts messages and URLs from other servers. A valid HTTP signature identifies the holder of a key for one request; it does not automatically prove that every embedded object belongs to that signer. [Mastodon 4.7.3](../references/software/mastodon.md) has separate checks for requests, actors, embedded or forwarded activities, and object ownership. This historical release has known security vulnerabilities fixed later; this page is an engineering study, not a deployment recommendation.

## Before you start

Use an isolated test instance and fixture accounts when reproducing security behavior. Never publish live tokens, keys or private user content. The trust boundaries below describe the pinned source, and the advisory scope applies only to the cited affected versions. The [federation pipeline](../servers/federation-pipelines/mastodon-4-7.md) explains when the checks and asynchronous work occur.

## Authenticate a request and establish authority

The inbox controller requires a signed actor request before ordinary activity processing. Signature verification finds key material and can refresh a known remote key; network fetching and redirects are therefore themselves security boundaries. The processing service separately checks the activity's actor and handles linked-data signatures or object integrity proofs for relayed content. A peer must not treat a relay's transport signature as universal authority for the activity's claimed author. `[source]` [signature verification](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/concerns/signature_verification.rb), [activity processing](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb).

Mastodon's pinned federation statement distinguishes legacy HTTP Signatures from RFC 9421 HTTP Message Signatures. It describes RSA and Ed25519 verification support and distinguishes accepting FEP-521a keys and FEP-8b32 proofs from emitting them. Its outbound request code tries the legacy signature first and retries using RFC 9421 on a 400 or 401 response when a signing key is present. Do not infer the algorithm used for outbound requests from the set accepted inbound. `[documented]` [federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md); `[source]` [request implementation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/request.rb).

## Handle hostile content and URLs

Remote actor, key, object, collection, media and redirect URLs are untrusted input. Mastodon has private-address checks and dedicated remote-fetch code; implementers should also test destination validation across DNS resolution and redirects, bound response sizes and recursion, and sanitize displayed HTML. Those tests are engineering recommendations, not proof that this historical release blocks every possible attack. `[source]` [private address check](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/private_address_check.rb), [remote status fetch](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_remote_status_service.rb); `[spec]` [ActivityPub security considerations](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations).

## Technical details

The inbox checks request `content_length` against `ActivityPub::Activity::MAX_JSON_SIZE` before dispatch; the pinned federation statement documents a 1 MB JSON-LD limit. Length checks are one boundary, not an assurance that parsing, graph processing or nested references have bounded computational cost. `[source]` [inbox controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/activitypub/inboxes_controller.rb#L12); `[documented]` [federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md).

Local private key material uses encrypted database fields. Backups and access control must protect the keys and their corresponding encryption configuration; encrypted fields do not eliminate the need to secure credentials, logs and backups. `[source]` [keypair model](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/models/keypair.rb), [encryption configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/initializers/active_record_encryption.rb).

## Historical advisories and testing

The project disclosed an ActivityPub identifier verification vulnerability affecting 4.7.3 and fixed it in 4.7.4. This is direct evidence that parsing or verifying a signature is not enough to establish correct object authorization. `[documented]` [GHSA-288h-6j8h-6x5j](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j).

For an isolated regression suite, test forged actor and object IDs, valid signatures from unauthorized actors, forwarding by a different signer, stale or rotated keys, hostile redirects, oversized inputs and out-of-order Delete/Create delivery. Compare persisted state and notifications, not only HTTP status. This is a proposed test plan; the wiki has not run these tests or measured the results for this release.

## Pitfalls and open questions

- A successful 202 response does not demonstrate that a queued activity passed later authorization or was displayed.
- A signed request is not a blanket authorization for embedded objects or a guarantee of confidentiality for content delivered to remote servers.
- Key rotation and a restore without the original encryption configuration can affect the ability to sign or decrypt local key material; test recovery before relying on it.
- The exact behavior for every malformed signature, URL, proof and race has not been exhaustively tested here.

## Sources

- [Mastodon 4.7.3 federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) — declared signature support and federation limits.
- [Signature verifier](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/concerns/signature_verification.rb), [activity processing](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/process_activity_service.rb) and [request implementation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/request.rb) — request, actor and outbound signing paths.
- [ActivityPub security considerations](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations) — general protocol threats.
- [Identifier verification advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-288h-6j8h-6x5j) — affected releases and fix.
