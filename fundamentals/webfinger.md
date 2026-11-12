# WebFinger

[WebFinger](../glossary.md#webfinger) turns a handle such as `alice@example.com` into the URL of that account's actor document. It is commonly used for handle-based discovery; it is not required to resolve every actor URI, and WebFinger itself is a general resource-discovery protocol.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

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

In a 2026 laboratory, test servers identified as `host:8080` could not be discovered by Mastodon, which performed WebFinger over HTTPS only and dropped the remote port; the fix was standard-port identities behind a proxy with a trusted test certificate. Separately, the Node-based Misskey and Catodon processes ignored `/etc/hosts` because their resolver bypassed the system lookup, so name mappings had to be injected into the resolver, and a process that cached a stale entry needed a restart. These are properties of the lab builds and setup, not claims about public deployments. `[reported]` [problem log items 11 and 12](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md). The conclusion for implementers: use a stable, externally resolvable canonical origin and make the WebFinger subject, actor id, signature `keyId` and object ids agree.

## Sources

- [RFC 7033: WebFinger](https://www.rfc-editor.org/rfc/rfc7033) — the protocol
- [Federation bench problem log, items 11 and 12](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — Mastodon HTTPS-only discovery and Node resolver behaviour
