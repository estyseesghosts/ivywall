# Extensions and FEPs

ActivityPub deliberately leaves out features users expect: quote posts, reactions, group semantics, follower synchronisation. The Fediverse fills the gaps with community proposals ([FEPs](../glossary.md#fep)), conventions inherited from other software, and vocabularies private to one server. This page explains how to tell these apart.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

ActivityStreams allows extension through `@context`. `[spec]` ActivityStreams 2.0 Core.

## What implementations do

Mastodon's own federation notes describe the extensions needed to interoperate with it; other servers add `EmojiReact`, `_misskey_quote` and similar terms. See the [mirrored federation documents](../references/federation-docs/index.md).

## Technical details

> Unknown: a table of which software emits and accepts which extension. This belongs in per-feature [compatibility records](../federation/compatibility/emoji-reactions.md) and in [FEP records](../references/feps/fep-044f.md).

## Sources

- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — proposal texts and statuses
