# HTTP signatures and authentication

Federation needs a way to know which server sent a request. The Fediverse's answer is an [HTTP signature](../glossary.md#http-signature): the sender signs selected headers with the private key of the sending actor, and the receiver fetches the public key from the actor document to verify it. The mechanics have several incompatible generations, which is the main source of invalid-signature failures.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

ActivityPub itself requires no particular scheme. `[spec]` ActivityPub leaves authentication open.

## What implementations do

Servers broadly use the draft-cavage HTTP Signatures scheme, with newer servers moving to RFC 9421 HTTP Message Signatures; some also sign `GET` requests ("authorized fetch"). Which software does which, and from which version, is not yet recorded.

## Technical details

> Unknown: header lists signed per implementation, digest handling, clock skew limits and key rotation behaviour. See also [FEP-521a](../references/feps/fep-521a.md).

## Pitfalls

- Clock skew and missing `Digest` headers.
- Key not found after an actor moves or rotates keys.

## Sources

- [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421) — the standardised scheme
- [Signing HTTP Messages (draft-cavage)](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures) — the older scheme in wide use
