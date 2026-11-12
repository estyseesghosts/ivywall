# Failure mode: replies missing on remote threads

A user opens a post on their server and sees only some of the replies that exist on the origin server. Replies are not pushed to every server that shows the post, so a thread is always partly a cache.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Expected and observed behaviour

Expected: all public replies visible. Observed: a subset, depending on who follows whom and what the server fetched `[hypothesis]`.

## Root cause

Replies reach a server only by delivery to a followed actor or by an explicit fetch of the replies collection. Inbox forwarding is optional. See [ActivityPub server-to-server](../../fundamentals/activitypub-s2s.md).

## Reproduction

Not yet reproducible; needs the [testing lab](../../testing/index.md).

## Technical details

> Unknown: affected versions and per-implementation backfill behaviour.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
