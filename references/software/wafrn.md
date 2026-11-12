# Wafrn fact sheet

**Studied release:** Wafrn server 2026.11.01, commit [`f2bdd67849f44227d932c9ed0aa91b6af06d512d`](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d). The commit is dated 5 November 2026; the precise release publication date was not independently verified. This is a source study rather than a live deployment test. `[source]` [release-tag manifest](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/package.json).

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | TypeScript/Node.js backend and Angular frontend. `[source]` [backend manifest](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/package.json), [frontend manifest](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/frontend/package.json). |
| Storage | PostgreSQL, Redis/BullMQ and local or object-backed media. `[source]` [Compose](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/docker-compose.default.yml), [media storage](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/utils/storage.ts). |
| Federation | ActivityPub and optional AT Protocol integration. `[source]` [ActivityPub route](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/routes/activitypub/activitypub.ts), [AT worker](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/atproto.ts). |
| Client API | Native application API plus a Mastodon-compatible subset, with separate OAuth handling. `[source]` [API router](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/mastoapi/mastoapi.ts), [OAuth](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/packages/backend/mastoapi/oauth.ts). |

## Technical details

See the [case study](../../servers/case-studies/wafrn.md) for queue acknowledgment, privacy boundaries, representation and evidence gaps.

## Sources

- [Wafrn 2026.11.01 source](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d) — version-pinned implementation and deployment configuration.
- [Wafrn package manifest](https://codeberg.org/wafrn/wafrn/src/commit/f2bdd67849f44227d932c9ed0aa91b6af06d512d/package.json) — version identifier.
