# WebFinger

[WebFinger](../glossary.md#webfinger) turns a handle such as `alice@example.com` into the URL of that account's actor document. It is the first request in almost every remote follow and mention, which is why a broken WebFinger endpoint makes an account invisible to other servers.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

A GET to `/.well-known/webfinger?resource=acct:alice@example.com` returns a JSON Resource Descriptor with `links`. `[spec]` RFC 7033.

## What implementations do

Fediverse servers look for a `self` link of type `application/activity+json` (or the LD+JSON profile form). The handle's domain and the actor's domain can differ; see [identity](identity.md).

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
