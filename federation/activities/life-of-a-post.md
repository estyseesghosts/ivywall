# Life of a federated post

A walkthrough of one public post from composing to appearing on followers' timelines on other servers: validation, storage, fan-out, delivery, remote processing and notifications.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Actors and starting state

Alice on A with followers on B and C.

## Step by step

1. A stores the post and renders HTML.
2. A resolves recipients and groups them by [shared inbox](../../glossary.md#inbox).
3. A queues one delivery job per destination.
4. Each job signs and POSTs a `Create` activity.
5. B and C validate, store and fan the post out to local timelines.

Outline only `[hypothesis]`.

## Technical details

> Unknown: everything implementation-specific. To be traced for [Mastodon](../../servers/case-studies/mastodon.md) first.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
