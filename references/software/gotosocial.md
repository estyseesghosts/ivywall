# GoToSocial fact sheet

**Studied release:** GoToSocial v0.22.3, released 21 October 2026, commit [`5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4`](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4). This source study is not an interoperability or load test.

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | Go application with embedded worker pools. `[source]` [workers](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/workers/workers.go). |
| Storage | SQLite or PostgreSQL through Bun; filesystem or S3-compatible media. `[source]` [database adapter](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4/internal/db/bundb/bundb.go); `[documented]` [storage](https://docs.gotosocial.org/en/v0.22.3/configuration/storage/). |
| Client interface | Mastodon-compatible REST, OAuth and streaming with implementation-specific coverage. `[documented]` [API inventory](https://docs.gotosocial.org/en/v0.22.3/api/swagger/). |
| Federation | ActivityPub server-to-server, WebFinger, NodeInfo and signed requests. `[documented]` [federation](https://docs.gotosocial.org/en/v0.22.3/federation/). |
| Access | Signed ActivityPub GET and POST requests required; blocks and object access policy are separate checks. `[documented]` [signatures](https://docs.gotosocial.org/en/v0.22.3/federation/http_signatures/), [access control](https://docs.gotosocial.org/en/v0.22.3/federation/access_control/). |
| Shared inbox | The actor documentation says local actors do not advertise a shared inbox. `[documented]` [actors](https://docs.gotosocial.org/en/v0.22.3/federation/actors/). |

## Technical details

See the [case study](../../servers/case-studies/gotosocial.md) for code paths, delivery tradeoffs and evidence gaps. No runtime measurements or cross-server test results are asserted.

## Sources

- [GoToSocial v0.22.3 release](https://codeberg.org/superseriousbusiness/gotosocial/releases/tag/v0.22.3) — release identity and security changes.
- [GoToSocial v0.22.3 source](https://codeberg.org/superseriousbusiness/gotosocial/src/commit/5a6c8e26c1d028a04b9b50c1a84f55e63429a1a4) — pinned implementation.
- [v0.22.3 documentation](https://docs.gotosocial.org/en/v0.22.3/) — documented configuration and federation behavior.
