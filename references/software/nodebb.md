# NodeBB fact sheet

**Studied release:** NodeBB 4.16.7, released 31 October 2026, commit [`e10be67aceaec0581fd130c6ef7b5e2f1e7f64f2`](https://github.com/NodeBB/NodeBB/tree/e10be67aceaec0581fd130c6ef7b5e2f1e7f64f2). This is a source study, not a live interoperation or capacity test. `[source]` [release](https://github.com/NodeBB/NodeBB/releases/tag/v4.16.7), [manifest](https://github.com/NodeBB/NodeBB/blob/v4.16.7/install/package.json).

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | Node.js and JavaScript; Express and Socket.IO. `[source]` [manifest](https://github.com/NodeBB/NodeBB/blob/v4.16.7/install/package.json). |
| Storage | Redis, MongoDB or PostgreSQL adapters expose object and sorted-set operations. `[source]` [database selector](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/database/index.js). |
| Federation | ActivityPub server-to-server, WebFinger and NodeInfo; categories can be Group actors. `[source]` [routes](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/activitypub.js), [discovery](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/well-known.js), [actor mapper](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/mocks.js). |
| Signatures | RFC 9421 and draft signature handling. `[source]` [implementation](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/activitypub/signatures.js). |
| Client API | NodeBB read/write API and Socket.IO; no blanket claim of Mastodon API parity. `[source]` [write routes](https://github.com/NodeBB/NodeBB/blob/v4.16.7/src/routes/write/index.js). |

## Technical details

The [case study](../../servers/case-studies/nodebb.md) follows incoming and outgoing paths, backing stores, and untested risks. Build and deployment settings can change actual limits and behavior.

## Sources

- [NodeBB v4.16.7 release](https://github.com/NodeBB/NodeBB/releases/tag/v4.16.7) — release identifier and date.
- [NodeBB v4.16.7 source](https://github.com/NodeBB/NodeBB/tree/v4.16.7) — source for runtime, persistence and federation facts.
