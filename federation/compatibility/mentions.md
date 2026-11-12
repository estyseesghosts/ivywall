# Compatibility: mentions and notifications

Writing `@someone@example.com` in a post does not by itself tell the receiving server to notify that person. Servers differ on whether the text, a structured `Mention` tag, or the post's addressing triggers the notification. In the laboratory this showed up as Akkoma-authored mentions that never produced a notification elsewhere.

## Summary

| Author server | Receiver | Observed | Evidence |
| ------------- | -------- | -------- | -------- |
| Akkoma (build not recorded) | Misskey-family and Mastodon-API receivers | No mention notification in the lab; the operator's forensic note says the posts carried bare mention text without an ActivityPub `Mention` tag | `[reported]` [run 5](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) |
| Mastodon, Misskey, Catodon | Test receivers | Mentions notified in the first clean cross-family run (162/162 checks) | `[reported]` [run 5](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) |

Counts: run 5 lists two `mention-notif akkoma -> birchtree` rows as failures, and calls the Akkoma outbound mention family emit-side. The report also notes `akkoma -> mastodon` rows were outside its scope.

## Information lost in translation

Four different things can all look like "a mention":

1. Text in the content that looks like `@someone@server`.
2. A structured `Mention` tag naming an actor.
3. The sender addressing that actor as a recipient (`to` or `cc`).
4. The receiver creating a local notification.

A server that depends on one of these without the others will fail to notify. The lab's diagnosis was that the Akkoma output had (1) without (2). It does not establish that every Akkoma instance always omits tags.

## Technical details

**A notification failure can be a local bug, not a federation failure.** In Pinetree's own worklog, fresh foreign mentions were invisible in the notification API for 240 seconds because the notification index ordered by notification type instead of creation time. After the fix, mentions from Pinetree, Misskey and Catodon appeared in about 3.1 to 3.2 seconds, with no change to ActivityPub delivery. A test that checks only the notification list cannot tell missing delivery from a broken notification index. `[reported]` [fed-debug-logging worklog](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-fed-debug-logging.md).

> Unknown: a paired raw outgoing Akkoma `Note` and the receiver's trace. Without it the emit-side explanation is the operator's, not a captured fact.

## Test procedure

From each server, post a mention in three forms: with a `Mention` tag and addressing, with a tag but no addressing, and text only. Record the outgoing JSON, each receiver's stored object, and its notification list after a stated deadline. Use fixture accounts.

## Sources

- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — Akkoma mention-notification rows and emit-side classification
- [Federation bench problem log, item 46](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — the Akkoma outbound family
- [Pinetree fed-debug-logging worklog](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-fed-debug-logging.md) — the notification-index counterexample
