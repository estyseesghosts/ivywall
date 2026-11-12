# Federation

How servers actually behave when they exchange content: the lifecycle of a post or a follow, delivery queues and retries, the object types in use, and, most importantly, what each implementation does with each feature. Two servers that both implement ActivityPub can still disagree about reactions, quotes, edits and visibility, so this section records behaviour by feature, software version and direction instead of with checkmarks.

## Pages

No topic pages yet. Planned, in priority order:

- Compatibility records, one per feature — rich text, MFM, Markdown, custom emoji, polls, quotes, reactions, edit histories, visibility, mentions, hashtags, media, replies, search, account migration, moderation actions, group federation. This is the highest-priority part of the wiki.
- Activity lifecycles — the full life of a federated post and of a remote follow, step by step.
- Delivery — queues, retries and backoff, duplicate handling, ordering, dead destinations.
- Object types — Note, Article, Question, Group, Video and software-specific types.
- Failure modes — missing replies, stale profiles, duplicated boosts, lost reactions, invalid signatures, broken mentions, rejected media, migration failures.

## Notes and open questions

Compatibility records capture what a server emits and what it accepts, using the values defined under [compatibility values](../glossary.md#compatibility-values). Illustration of the intended depth: Akkoma sends separate `EmojiReact` activities and allows several different reactions per user, while Mastodon's native interaction is a `Like`. The real record will carry versions and evidence for every row.

> Unknown: no matrix has been tested yet. Until the testing lab produces results, rows are filled from pinned source and documentation and labelled `[source]` or `[documented]`, never `[observed]`.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — delivery and forwarding rules
- [Akkoma documentation](https://docs.akkoma.dev/) — emoji reaction and ActivityPub extension behaviour
