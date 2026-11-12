# Extensions and FEPs

ActivityPub and ActivityStreams do not specify every feature or interoperability convention that applications need. Software uses community proposals ([FEPs](../glossary.md#fep)), other shared conventions and implementation-specific vocabulary. A proposal’s existence does not establish that a particular version supports it. This page explains how to tell these apart.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

ActivityStreams permits additional properties and contexts, but producers MUST NOT redefine the normative context. Unknown extensions may be ignored by consumers. `[spec]` [ActivityStreams Core §§2.1, 5](https://www.w3.org/TR/activitystreams-core/#extensibility).

## What implementations do

Mastodon 4.7.3 lists supported and required extensions in its [version-pinned federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md). Misskey 2026.10.1 emits `_misskey_quote` in its [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts#L484). See the [quote compatibility record](../federation/compatibility/quotes.md) for direction and limitations. `[documented]` `[source]`

## Technical details

> Unknown: a table of which software emits and accepts which extension. This belongs in per-feature [compatibility records](../federation/compatibility/emoji-reactions.md) and in [FEP records](../references/feps/fep-044f.md).

## Sources

- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — proposal texts and statuses
- [ActivityStreams Core §5](https://www.w3.org/TR/activitystreams-core/#extensibility) — extension handling
- [Mastodon 4.7.3 federation statement](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/FEDERATION.md) — declared implementation extensions
