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

## Sources

- [RFC 7033: WebFinger](https://www.rfc-editor.org/rfc/rfc7033) — the protocol
