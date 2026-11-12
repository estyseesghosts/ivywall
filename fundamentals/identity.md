# Identity and account handles

A Fediverse account can have a human handle such as `alice@example.com` and an actor identifier, typically an HTTPS URL. [WebFinger](webfinger.md) can associate the handle with an actor; the domains can differ, subject to implementation-specific verification. This page covers how identity is resolved and what happens when an account moves.

> **Coverage incomplete.** Actor ids and handles follow the specification and FEP-7628. Not yet covered: how each studied server verifies a `Move` and what it does with followers. Statements without an evidence label are general background.

## What the specification requires

ActivityPub actors have an `id` URI, while the specification does not prescribe the `user@domain` handle as their identifier. Identifiers should be treated as distinct from presentation names and handles. `[spec]` [ActivityPub §§3.1, 4](https://www.w3.org/TR/2018/REC-activitypub-20180123/#actors).

## What implementations do

Mastodon 4.7.3 uses WebFinger for handle discovery and describes actor moves with `Move` and `alsoKnownAs`. See its [pinned federation documentation](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) and the [Move handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/move.rb#L6). `[source]`

## Technical details

> Unknown: how each implementation verifies a `Move` and what it does with followers.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — proposal texts and statuses
