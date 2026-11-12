# Pixelfed fact sheet

**Studied release:** Pixelfed 0.15.2, published 21 October 2026, commit [`b19607f1315b45aead25bc827c5e691a62317894`](https://github.com/pixelfed/pixelfed/tree/b19607f1315b45aead25bc827c5e691a62317894). Source inspection is not a live compatibility test. `[source]` [release](https://github.com/pixelfed/pixelfed/releases/tag/v0.15.2).

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | PHP and Laravel; web, Horizon workers and scheduler can run separately. `[source]` [dependencies](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/composer.json), [Compose](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/docker-compose.yml). |
| Storage | SQL, Redis and local or object-backed media. PostgreSQL is documented as best effort. `[source]` [README](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/README.md), [filesystem config](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/config/filesystems.php). |
| Federation | ActivityPub server-to-server, WebFinger, NodeInfo and HTTP signatures. `[source]` [routes](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/routes/api.php), [inbox validator](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/app/Jobs/InboxPipeline/InboxValidator.php). |
| Client API | Pixelfed and Mastodon-shaped endpoints with version-specific coverage and restrictions. `[source]` [API controller](https://github.com/pixelfed/pixelfed/blob/b19607f1315b45aead25bc827c5e691a62317894/app/Http/Controllers/Api/ApiV1Controller.php). |

## Technical details

The [case study](../../servers/case-studies/pixelfed.md) covers inbox and delivery jobs, feed storage, failure boundaries and unanswered interoperability questions.

## Sources

- [Pixelfed 0.15.2 source](https://github.com/pixelfed/pixelfed/tree/v0.15.2) — pinned implementation and deployment configuration.
- [Pixelfed 0.15.2 release](https://github.com/pixelfed/pixelfed/releases/tag/v0.15.2) — release information.
