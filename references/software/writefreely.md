# WriteFreely fact sheet

**Studied release:** WriteFreely v0.17.3, published 9 November 2026, commit [`d2485910010b1671a6e4341ab36cd199b7868e8d`](https://github.com/writefreely/writefreely/tree/d2485910010b1671a6e4341ab36cd199b7868e8d). Evidence is a static source review, not a live federation or security test.

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | Go server with HTML templates and a writing-oriented HTTP API. `[source]` [module](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/go.mod), [routes](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/routes.go). |
| Storage | SQLite or MySQL-compatible SQL; numbered migrations. `[source]` [database](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/database.go), [migrations](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/migrations/migrations.go). |
| Actor model | A federated blog collection is a `Person` actor; incoming Follow and Like paths maintain remote relationships. `[source]` [ActivityPub](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go). |
| Client API | Purpose-built writing API, not general Mastodon REST compatibility. `[source]` [routes](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/routes.go). |
| Delivery | Groups followers by shared inbox or individual inbox and makes signed POSTs from asynchronous code; no durable retry queue is established in this path. `[source]` [ActivityPub](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go). |
| Incoming authentication | The inspected inbox handling path does not visibly verify an HTTP signature; this is not a tested exploit assertion. `[source]` [inbox handler](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go). |

## Technical details

See the [case study](../../servers/case-studies/writefreely.md) for the publication and follow paths, visibility boundaries, operational details and open tests.

## Sources

- [WriteFreely v0.17.3 release](https://github.com/writefreely/writefreely/releases/tag/v0.17.3) — release identity, fixes and upgrade guidance.
- [WriteFreely v0.17.3 source](https://github.com/writefreely/writefreely/tree/d2485910010b1671a6e4341ab36cd199b7868e8d) — pinned implementation.
