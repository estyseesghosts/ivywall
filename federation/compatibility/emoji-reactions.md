# Compatibility: emoji reactions

An emoji reaction records a particular response to a post; a favourite records a simpler like. Both can travel as an ActivityPub `Like`, but the receiving server may not preserve the chosen emoji. The evidence below describes individual code paths in [Misskey 2026.10.1](../../references/software/misskey.md) and [Mastodon 4.7.3](../../references/software/mastodon.md), not a completed live interoperability matrix.

## Summary

| Software | Version | Emits | Accepts | Notes |
| -------- | ------- | ----- | ------- | ----- |
| Misskey | 2026.10.1 | native | native / translated | Emits a `Like` with emoji fields. Reads `_misskey_reaction`, `content`, then `name`; an absent value falls back to a heart. `[source]` [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [inbox](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [reaction service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/ReactionService.ts). |
| Mastodon | 4.7.3 | translated | lossy | Emits a plain `Like` for a favourite. Its incoming `Like` handler creates a favourite without using the emoji fields. `[source]` [serializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/like_serializer.rb), [handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/like.rb). |

Values are defined in the [glossary](../../glossary.md#compatibility-values). The rows are source-level conclusions, conditional on the handler being reached and its checks passing, not observed success between two servers.

## Information lost in translation

Misskey's outgoing `Like` contains the chosen emoji, but Mastodon's 4.7.3 handler stores an ordinary favourite for an eligible local status; it does not store that emoji from the activity. A Mastodon favourite has no arbitrary emoji in its outgoing serializer; Misskey's receiver supplies its heart fallback when the activity contains no reaction value. These are directional code-level implications, not captured traffic. `[source]` [Misskey inbox](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [Mastodon Like handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/like.rb).

Misskey stores a unique `(userId, noteId)` reaction row. It can normalize or replace a custom emoji with a heart, for example when an emoji is unavailable, disallowed, or a post's reaction policy restricts remote reactions. Thus a received `Like` does not necessarily preserve the advertised string even on Misskey. `[source]` [reaction model](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/NoteReaction.ts), [reaction service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/ReactionService.ts).

## Technical details

The following excerpts are hand-written from the cited serializers and have not been run; the hosts, IDs and emoji are illustrative. They show the distinguishing fields, not complete delivery requests or security headers.

Misskey 2026.10.1's `renderLike` emits both fields and may include an `Emoji` tag for a non-local-only custom emoji. `[source]` [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts):

```json
{"id":"https://a.example/likes/123","type":"Like","actor":"https://a.example/users/alice","object":"https://b.example/notes/456","content":"😀","_misskey_reaction":"😀"}
```

Mastodon 4.7.3's serializer emits the activity ID, type, actor and object but no selected emoji. `[source]` [Like serializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/like_serializer.rb):

```json
{"id":"https://a.example/users/alice#likes/123","type":"Like","actor":"https://a.example/users/alice","object":"https://b.example/notes/456"}
```

Misskey's inbox extracts emoji tags before calling its reaction service and chooses `_misskey_reaction` over `content`, then `name`. It checks for an existing reaction and skips a duplicate. Mastodon's `Like` handler checks for a local target, an earlier delete and an existing favourite before creating a favourite and scheduling a notification. `[source]` [Misskey inbox](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts); [Mastodon handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/like.rb).

`Undo` must also be tested: Mastodon 4.7.3 has an `Undo(Like)` path that finds the target local status and removes the sender's favourite. A bare referenced activity ID cannot be resolved by its `try_undo_like` fallback in that code. `[source]` [Undo handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/undo.rb).

## Reaction-storm result

The October 2026 [laboratory](../../testing/interoperability/bench-evidence.md) reported 635 resolved and 215 unresolved reaction targets, all classified `edge_present_not_visible`; whether timeline indexing or harness paging explains it is open. It does not show that 215 activities were rejected or lost. `[reported]` [run report](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L7-L16), [results](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L68-L74).

## Test procedure

No live two-server result is claimed. On isolated instances of the pinned releases, make two fixture users able to see and follow each other; send a Unicode reaction and an allowed custom emoji from Misskey to a Mastodon post, record the delivered activity and inspect the resulting favourite via the Mastodon API. Reverse the direction with a Mastodon favourite and inspect the Misskey reaction value. Repeat with a missing emoji, a restrictive reaction policy, duplicate delivery and Undo; record HTTP status, queues, final API state, activity IDs and timeouts. Redact credentials and use only test content. This separates transport acceptance from persisted result and verifies whether both directions follow the source-level prediction.

## Reaction conventions seen in the October 2026 laboratory

The October 2026 [laboratory](../../testing/interoperability/bench-evidence.md) distinguished three conventions (`[reported]`, not rerun here; Akkoma's model is also `[documented]`)

| Family | Representation | Semantic difference |
| ------ | -------------- | ------------------- |
| Misskey, Catodon | `Like` with `_misskey_reaction` and emoji content | one reaction per account per note |
| Akkoma | `EmojiReact` for emoji; `Like` for favourites | favourite and reactions are independent; several different reactions per user |
| Mastodon | plain `Like` | favourite only |

Consequences: a receiver that maps every `EmojiReact` to a `Like` can collapse several reactions into one, drop the emoji, or remove a favourite when undoing a reaction. A test harness read Akkoma's `favourited_by` instead of `emoji_reactions` and concluded reactions were lost; they were present elsewhere. One test server also lacked inbound `EmojiReact` handling until 20 October 2026, a real gap; the fix was unit-tested and not exercised against a live Akkoma. Inbound and outbound support are independent: that server still sent bare favourites to Akkoma. `[reported]` [Akkoma compatibility worklog](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-20-akkoma-compat.md). For reversing reactions see [Undo, boosts and unboosts](undo-and-reposts.md).

## Sources

- [Misskey 2026.10.1 renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [inbox](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApInboxService.ts), [reaction service](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/ReactionService.ts) and [model](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/models/NoteReaction.ts) — representation, parsing, restrictions and uniqueness.
- [Mastodon 4.7.3 Like serializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/like_serializer.rb), [Like handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/like.rb) and [Undo handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/undo.rb) — outbound favourites, incoming processing and reversal.

- [19 October 2026 laboratory run](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L68-L74) — reported reaction-storm results and unresolved measurement ambiguity.
- [Pinetree Akkoma compatibility worklog, 20 October 2026](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-20-akkoma-compat.md) — inbound `EmojiReact` handling and what was not verified live
