# Security and privacy

Security and privacy are first-class engineering topics here, not an appendix. A federating server fetches arbitrary remote URLs, parses untrusted documents, renders other people's HTML and stores copies of content it does not control, so almost every feature is an attack surface. This section covers the threats and, as importantly, what visibility settings can and cannot promise.

## Pages

Pages:

- [SSRF and remote fetching](ssrf.md) — destination validation, redirects, proxies and testing.
- [Mastodon security boundaries](mastodon-4-7.md) — signatures, identity, remote fetching and access controls.

Still planned:

- Security — signature verification, key rotation, actor ownership validation, [SSRF](../glossary.md#ssrf), DNS rebinding, malicious redirects, JSON-LD processing, replay attacks, HTML sanitization, oversized objects, resource exhaustion.
- Privacy — followers-only visibility, direct messages, recipient leakage, signed fetches, remote caching, deletion limits, and the difference between access controls and enforceable confidentiality.

## Notes and open questions

> Unknown: remote fetch validation has not been exhaustively tested across implementations; the SSRF page includes one pinned source example.

## Sources

- [ActivityPub security considerations](https://www.w3.org/TR/activitypub/#security-considerations) — localhost fetching, recursive objects, denial of service and unsafe HTML
