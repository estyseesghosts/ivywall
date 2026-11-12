# ivywall

an engineering reference for building fediverse software: servers, clients, and the glue between them.

activitypub compatibility does not mean feature compatibility. two servers can both "speak activitypub" and still disagree about reactions, quotes, edits, visibility, threading, notifications, or how to find an account. supporting the mastodon api does not mean a client can treat mastodon, akkoma, gotosocial and pixelfed the same way. this wiki records where the standards end and the real behaviour begins, version by version, with source references.

none of this research is my own and i do not assume credit for any of the work presented here. this is a collection to assist development.

## What it answers

1. How does the fediverse actually work? Protocols, extensions, authentication, delivery, discovery.
2. What does each implementation actually support, including undocumented behaviour and interoperability failures?
3. How do you engineer a reliable client or server?
4. Which existing implementations are worth learning from, and what mistakes should be avoided?

## Sections

- [Fundamentals](fundamentals/index.md) — ActivityStreams, ActivityPub, discovery, authentication, extensions.
- [Federation](federation/index.md) — delivery, activity lifecycles, object types, per-feature compatibility, failure modes.
- [Clients](clients/index.md) — client APIs and client engineering across software families.
- [Servers](servers/index.md) — architecture, storage, pipelines, performance, source-level case studies.
- [Security and privacy](security/index.md) — signature checks, SSRF, sanitization, what visibility can and cannot promise.
- [Moderation](moderation/index.md) — blocks, federation controls, message rewriting, audit trails.
- [Testing](testing/index.md) — a lab for measuring interoperability instead of guessing it.
- [References](references/index.md) — version-pinned software fact sheets, specifications, FEPs.
- [Guides](guides/index.md) — start-to-finish implementation walkthroughs.

## Reading guide

- Jargon is explained on first use and defined in the [glossary](glossary.md).
- Every claim about behaviour carries an evidence label and a software version. See the labels in [AGENTS.md](AGENTS.md).
- Every page ends with Sources. Contributors: read [AGENTS.md](AGENTS.md) first.
