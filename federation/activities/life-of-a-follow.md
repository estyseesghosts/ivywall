# Life of a remote follow

A walkthrough of one user on server A following a user on server B: every HTTP request, database change, queued job and notification, from typing the handle to seeing the first post. This stub fixes the outline; the traced details come from the case studies.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## Actors and starting state

Alice on A, Bob on B. A has never seen Bob.

## Step by step

1. A resolves `bob@b.example` with [WebFinger](../../fundamentals/webfinger.md).
2. A fetches Bob's actor document and stores a remote account.
3. A creates a pending follow and queues a `Follow` activity.
4. A signs and POSTs the `Follow` to Bob's [inbox](../../glossary.md#inbox) ([authentication](../../fundamentals/http-signatures.md)).
5. B verifies the signature, stores the follow, notifies Bob, and (for open accounts) queues `Accept`.
6. A receives the `Accept` and marks the follow active.

Steps are the generic outline `[hypothesis]`; each needs request and database detail per implementation.

## Technical details

> Unknown: payload shapes, retry behaviour and what happens when B is down. See [delivery](../delivery/queues-and-retries.md).

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
