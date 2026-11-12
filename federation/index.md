# Federation

How servers actually behave when they exchange content: the lifecycle of a post or a follow, delivery queues and retries, the object types in use, and, most importantly, what each implementation does with each feature. Two servers that both implement ActivityPub can still disagree about reactions, quotes, edits and visibility, so this section records behaviour by feature, software version and direction instead of with checkmarks.

## Pages

Pages:

- [Life of a remote follow](activities/life-of-a-follow.md) — pending requests, delivery and acceptance.
- [Life of a federated post](activities/life-of-a-post.md) — source-derived path from posting through remote processing.
- [Delivery queues and retries](delivery/queues-and-retries.md) — version-specific retry and ordering behavior.
- [Compatibility: emoji reactions](compatibility/emoji-reactions.md) — directional representations and loss.
- [Compatibility: quote posts](compatibility/quotes.md) — legacy fields, consent and translation.
- [Compatibility: post edits](compatibility/post-edits.md) — edit delivery and remote update handling.
- [Observed profiles of Mastodon, Misskey, Catodon, Akkoma and Sharkey](compatibility/observed-profiles.md) — index of laboratory behaviour, by family.
- [Compatibility: Undo, boosts and unboosts](compatibility/undo-and-reposts.md) — reversing actions across families.
- [Compatibility: mentions and notifications](compatibility/mentions.md) — text, tag and addressing.
- [Compatibility: remote media attachments](compatibility/media-attachments.md) — pending states and re-encoding.
- [Failure mode: wrong-domain activity ids](failure-modes/wrong-domain-activity-ids.md) — boosts silently not counted.
- [Failure mode: a deleted post reappears](failure-modes/delete-before-create.md) — Delete before Create.
- [Failure mode: an Undo has no effect](failure-modes/undo-ignored-or-deduplicated.md) — id reuse and unknown activities.
- [Failure mode: duplicate remote objects](failure-modes/duplicate-remote-objects.md) — several arrival paths.
- [Failure mode: first-contact races](failure-modes/first-contact-races.md) — slow or failing first requests.
- [Compatibility: polls](compatibility/polls.md) — poll shapes, vote handling and limited historical evidence.
- [Failure mode: media not verifying](failure-modes/media-not-verifying.md) — distinguish missing attachments, fetching and byte comparison.
- [Failure mode: missing replies](failure-modes/missing-replies.md) — delivery, fetching and response limits; reproduction remains open.

Not yet covered (the pages above exist; these do not), in priority order:

- Compatibility records still to write: rich text, MFM, Markdown, custom emoji, visibility, hashtags, replies, search, account migration, moderation actions, group federation. This is the highest-priority part of the wiki.
- Activity lifecycles still to write: delete, update, undo, move and group announce.
- Delivery: retry schedules and dead-destination handling per server; ordering guarantees.
- Object types: Note, Article, Question, Group, Video and software-specific types (no page yet).
- Failure modes still to write: stale profiles, duplicated boosts, lost reactions, invalid signatures, broken mentions, migration failures.

## Notes and open questions

Compatibility records capture what a server emits and what it accepts, using the values defined under [compatibility values](../glossary.md#compatibility-values). The current records describe Mastodon 4.7.3 and Misskey 2026.10.1 and identify their supporting source paths.

> Unknown: no matrix has been tested yet. Until the testing lab produces results, rows are filled from pinned source and documentation and labelled `[source]` or `[documented]`, never `[observed]`.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — delivery and forwarding rules
- [Akkoma documentation](https://docs.akkoma.dev/) — emoji reaction and ActivityPub extension behaviour
