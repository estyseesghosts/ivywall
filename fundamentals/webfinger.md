# WebFinger

[WebFinger](../glossary.md#webfinger) turns a handle such as `alice@example.com` into the URL of that account's actor document. It is commonly used for handle-based discovery; it is not required to resolve every actor URI, and WebFinger itself is a general resource-discovery protocol.

> **Coverage incomplete.** The query and response follow RFC 7033, and the laboratory observations are cited and separated by layer. Not yet covered: redirect and port handling per server, read from pinned source.

## What the specification requires

An HTTPS GET to the queried host’s `/.well-known/webfinger` endpoint with a `resource` parameter requests a JSON Resource Descriptor (JRD). A successful response describes the resource; the available links and relation types depend on that resource. `[spec]` [RFC 7033 §§4–4.4](https://www.rfc-editor.org/rfc/rfc7033#section-4).

## What implementations do

For Mastodon 4.7.3, the [WebFinger documentation](https://docs.joinmastodon.org/spec/webfinger/) describes an ActivityPub `self` link. The handle’s domain and actor’s domain can differ, subject to the implementation’s verification rules; see [identity](identity.md). `[documented]`

## Technical details

```http
GET /.well-known/webfinger?resource=acct:alice@example.com HTTP/1.1
Host: example.com
Accept: application/jrd+json
```

Hand-written request, not captured.

## Pitfalls

- Redirects between domains and the checks a server should apply; see [SSRF](../security/ssrf.md).

## Observed behaviour in interoperability tests

Three layers should be kept apart.

| Layer | Statement | Evidence |
| ----- | --------- | -------- |
| Protocol | WebFinger queries are made over HTTPS, so a plain-HTTP server cannot be discovered by a conforming client. | `[spec]` RFC 7033 §4.2 |
| Mastodon behaviour | In the laboratory Mastodon discovered a test server only on standard ports: identities of the form `host:8080` failed because the port was dropped during resolution and nothing answered on the HTTPS default port. This port handling is the implementation-specific finding; it was not checked against Mastodon's source by this wiki and the lab build is not otherwise pinned. | `[reported]` [problem log item 11](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Laboratory configuration | The fix was standard-port identities behind a proxy with a trusted test certificate authority. | `[reported]` same item |

Separately, the Node-based Misskey and Catodon processes ignored `/etc/hosts` because their resolver bypassed the system lookup, so name mappings had to be injected into the resolver, and a process that cached a stale entry needed a restart. These are properties of the lab builds and setup, not claims about public deployments. `[reported]` [problem log items 11 and 12](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md). The conclusion for implementers: use a stable, externally resolvable canonical origin and make the WebFinger subject, actor id, signature `keyId` and object ids agree.

## Sources

- [RFC 7033: WebFinger](https://www.rfc-editor.org/rfc/rfc7033) — the protocol
- [Federation bench problem log, items 11 and 12](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — Mastodon non-standard-port discovery and Node resolver behaviour
