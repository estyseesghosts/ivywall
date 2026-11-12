# Identity and account handles

A Fediverse account has two names: a human handle like `alice@example.com` and an actor id that is a URL. They are linked by [WebFinger](webfinger.md), and they need not share a domain. This page covers how identity is resolved and what happens when an account moves.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

Actor `id` is the stable identifier; handles are not part of ActivityPub. `[spec]` ActivityPub, section 3.

## What implementations do

Handles are derived through WebFinger; account migration uses `Move` activities and `alsoKnownAs`. See [FEP-7628](../references/feps/fep-7628.md).

## Technical details

> Unknown: how each implementation verifies a `Move` and what it does with followers.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — proposal texts and statuses
