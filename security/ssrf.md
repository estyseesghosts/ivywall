# SSRF and remote fetching

A federating server fetches URLs that strangers supply: actor documents, objects, media, WebFinger targets. If those fetches can reach the server's own network, an attacker can use the server to probe or attack it. This is [SSRF](../glossary.md#ssrf), and it is the first security topic every implementation must get right.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification says

ActivityPub warns about fetching `localhost` and other internal targets, recursive objects, and denial of service. `[spec]` ActivityPub, security considerations.

## Technical details

Mitigations to document per implementation: blocking private address ranges after DNS resolution (against DNS rebinding), re-checking on every redirect, size and time limits, and an egress proxy. > Unknown: what each studied server does.

## Pitfalls

- Validating the hostname but not the resolved address.
- Following redirects into internal ranges.

## Sources

- [ActivityPub security considerations](https://www.w3.org/TR/activitypub/#security-considerations) — the warnings
