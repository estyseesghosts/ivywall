# Mastodon 4.7.3

Mastodon is the large multi-user Ruby on Rails server whose behaviour and API most other software is measured against. As a case study it shows a queue-heavy design built for big public instances.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Architecture

Rails web and streaming processes with [Sidekiq](../../glossary.md#sidekiq) workers and PostgreSQL `[hypothesis]` until checked against source.

## Key code paths

> Unknown: inbox receipt, delivery and timeline fan-out files at a pinned commit.

## Federation behaviour

See Mastodon's own [FEDERATION.md mirror](../../references/federation-docs/mastodon.md).

## Resource usage

Unmeasured.

## Technical details

Version facts belong in the [Mastodon fact sheet](../../references/software/mastodon.md).

## Sources

- [Mastodon source](https://github.com/mastodon/mastodon) — code to be studied
- [Mastodon FEDERATION.md mirror](../../references/federation-docs/mastodon.md) — project's own statement
