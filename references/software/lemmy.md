# Lemmy fact sheet

**Studied release:** Lemmy 0.19.21, released 26 October 2026, commit [`2ff971f205880f2638d5ce8dd979063dbd1dd6da`](https://github.com/LemmyNet/lemmy/tree/2ff971f205880f2638d5ce8dd979063dbd1dd6da). This is a source review, not a live interoperability benchmark.

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | Rust, Actix Web, Tokio, Diesel and PostgreSQL. `[source]` [manifest](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/Cargo.toml). |
| Client interface | Lemmy `/api/v3` routes; no universal Mastodon API compatibility is implied. `[source]` [routes](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/src/api_routes_http.rs). |
| Federation | Community `Group` actors, post `Page` and comment `Note`; ActivityPub library and signed inbox processing. `[source]` [activity types](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/apub/src/activity_lists.rs). |
| Outbound queue | PostgreSQL activity and per-destination worker state. `[source]` [worker](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/federate/src/worker.rs). |
| Media | pict-rs is integrated for image processing and storage. `[source]` [image routes](https://github.com/LemmyNet/lemmy/blob/2ff971f205880f2638d5ce8dd979063dbd1dd6da/crates/routes/src/images.rs). |

## Technical details

See the [case study](../../servers/case-studies/lemmy.md) for delivery, authorization and loss boundaries. Features and performance require version-pinned tests.

## Sources

- [0.19.21 release announcement](https://join-lemmy.org/news/2026-10-26_-_Lemmy_Release_v0.19.21_-_Security_Fixes) — release date and security fixes.
- [Lemmy 0.19.21 source](https://github.com/LemmyNet/lemmy/tree/2ff971f205880f2638d5ce8dd979063dbd1dd6da) — pinned code.
