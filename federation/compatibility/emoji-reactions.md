# Compatibility: emoji reactions

Users expect to react to a post with an emoji. Implementations model that differently, so a reaction sent from one server may be shown, converted to a like, or dropped on another. This is the template record for every feature in this section.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Summary

| Software | Version | Emits | Accepts | Notes |
| -------- | ------- | ----- | ------- | ----- |
| Akkoma | 2026.08 | native (`EmojiReact`) | native | Several different reactions per user `[documented]` |
| Misskey | 2026.10.1 | untested | untested | Reaction part of its own note model |
| Mastodon | 4.7.3 | untested | untested | Native interaction is `Like` |

Values are defined under [compatibility values](../../glossary.md#compatibility-values). Rows not yet checked say `untested`.

## Information lost in translation

> Unknown: what a receiving server shows for an unsupported reaction.

## Technical details

> Unknown: wire format per implementation and the code paths. Evidence label required on every row before this leaves stub status.

## Test procedure

Not yet reproducible; needs the [testing lab](../../testing/index.md).

## Sources

- [Akkoma documentation](https://docs.akkoma.dev/) — emoji reaction behaviour
