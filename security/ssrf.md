# SSRF and remote fetching

A federating server fetches URLs from actors, activities, media, and discovery responses supplied by other servers. A malicious URL can make it contact a service on its own network or expose credentials; this is **[server-side request forgery](../glossary.md#ssrf)**. A safe design must account for where the connection actually goes, not only whether the URL looks plausible.

## Before you start

ActivityPub 2018 discusses requests to localhost and internal services, recursive content and denial of service in its security considerations. It does not specify a complete destination-filtering implementation. `[spec]` [ActivityPub Appendix B](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations).

The recommendations below are engineering controls, not evidence that a particular server implements them. Deployments can intentionally federate with private networks; if so, isolate and explicitly scope those exceptions rather than assuming public-network rules apply unchanged.

## Validate the complete request path

1. Restrict the allowed URL schemes and reject malformed or ambiguous URLs. Do not pass untrusted URLs to a generic downloader capable of reading local files or contacting arbitrary protocols. `[spec]` [ActivityPub Appendix B](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations).
2. Resolve DNS and validate the actual destination addresses against the deployment's network policy, including IPv4, IPv6 and IPv4-mapped IPv6. Reject loopback, link-local, private and other special-use destinations when public-only fetching is required. A hostname check alone is insufficient. Bind the decision to the address used for the connection so a second resolution cannot change the target after validation. `[documented]` [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).
3. Disable redirects where unnecessary; otherwise apply the same scheme, destination, authorization and redirect-count checks at **each** hop, and do not forward credentials to an unrelated origin. Restrict network egress independently of application validation, accounting for proxies and metadata services. `[documented]` [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).
4. Bound connection and overall time, response bytes, decompression, nested object traversal, and concurrent fetches. Apply these limits to actor, key, media, preview and other fetch paths; protecting one HTTP client does not protect a different downloader. `[spec]` [ActivityPub Appendix B](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations).

## Technical details

Mastodon 4.7.3 provides an example of the distinction between address classification and the place a network connection is made. `PrivateAddressCheck.private_address?` normalizes IPv4-mapped and compatible IPv6 addresses before checking private, loopback, link-local and listed special ranges. Its request socket checks resolved addresses; the implementation also has development, configured-exception and proxy paths that change where checks apply. A proxy can make its own connections, so operators must assess that boundary separately. These are observations about the pinned source, not a claim that every Mastodon fetch is safe. `[source]` [address check](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/private_address_check.rb#L35-L40), [request socket](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/request.rb#L315-L405).

A useful isolated test suite should control DNS answers and HTTP redirects, including a public address that redirects to a private address, DNS answers that change between lookup and connection, IPv6 mapped addresses, and responses exceeding the size and time budgets. Assert which destination received a request and whether credentials were forwarded; an error response alone does not prove that no forbidden connection occurred. This is a proposed test plan, not a completed audit.

## Pitfalls and open questions

- **Validating only the URL text:** an apparently public hostname may resolve to an internal address or redirect there.
- **Trusting a single DNS check:** ensure the connection uses an address that passed policy, including when retries or proxies are involved.
- **Protecting only ActivityPub fetches:** media processors and preview workers may have separate HTTP stacks and redirect behavior.
- **Treating one deny-list as universal:** local deployments, proxy routing and new special-use ranges affect the policy. Test with the actual environment and keep network controls independent.

Exact redirect, DNS, proxy and media-fetch behavior for each studied implementation has not been tested exhaustively. See [Mastodon federation trust boundaries](mastodon-4-7.md) for that release's additional checks.

## Sources

- [ActivityPub 2018, Appendix B](https://www.w3.org/TR/2018/REC-activitypub-20180123/#security-considerations) — protocol security considerations.
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — application and network-layer defenses and DNS challenges.
- [Mastodon 4.7.3 address classification](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/private_address_check.rb#L35-L40) and [request implementation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/request.rb#L315-L405) — scoped source examples.
