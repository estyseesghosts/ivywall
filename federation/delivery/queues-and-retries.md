# Delivery queues and retries

Delivery is where federation turns into engineering. Every post becomes many outbound HTTP requests to servers that may be slow, down, or hostile. This page covers queueing, retry and backoff, deduplication, ordering, and how to treat destinations that stay dead.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## How it works

Common designs queue one job per destination inbox with exponential backoff and give up after a window. Specifics differ by implementation and are not yet recorded `[hypothesis]`.

## Technical details

> Unknown: retry schedules, give-up thresholds, unavailable-instance tracking and ordering guarantees per studied server.

## Pitfalls

- Retrying forever against a server that is gone.
- Delivering `Update` before `Create` has landed; see [consistency](../../servers/index.md).
- Large fan-outs starving other queues.

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
