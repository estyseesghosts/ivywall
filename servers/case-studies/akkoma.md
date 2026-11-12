# Akkoma 2026.08 (3.20.0)

Akkoma is an Elixir social server descended from Pleroma. It combines a configurable federation pipeline with a Mastodon-compatible client API and additional post, emoji and moderation features. This study is pinned to [v3.20.0](../../references/software/akkoma.md); the version and configured policies matter when evaluating interoperability. Its module names retain the `Pleroma` namespace.

## Architecture

The server runs on the Erlang virtual machine as an OTP application. Phoenix handles HTTP, Ecto and PostgreSQL persist social data, and Oban stores background jobs in PostgreSQL. An application supervisor starts the repository, background jobs, caches and web components; media storage and search options are configurable. This makes database capacity and backup relevant to both application records and queued work. `[source]` [application startup](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/application.ex), [dependencies](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/mix.exs), [configuration](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/config/config.exs).

Activities and objects retain ActivityStreams-shaped JSON in relational records; query paths and indexing are important because relationships are not simply equivalent to a conventional object foreign key. Accounts, follow relationships, notifications and other social state have separate models. Back up PostgreSQL and media together; determine the right consistency point, retention policy and restore procedure for the deployment rather than assuming an object-storage snapshot alone is sufficient. `[source]` [activity model](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/activity.ex), [object model](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/object.ex), [uploaders](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/uploaders).

## Key code paths

### Inbound activity and transaction

The shared and user inbox routes require a valid signature; the controller queues a federator job and returns `"ok"`, before the queued activity has completed downstream processing. Missing or invalid signatures are rejected on these paths. A successful HTTP response therefore says neither that an activity was persisted nor that a recipient saw it. `[source]` [inbox controller](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/activity_pub_controller.ex), [receiver worker](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/workers/receiver_worker.ex).

`Pipeline.common_pipeline` wraps validation, message rewrite facility (**[MRF](../../glossary.md#mrf)**) filtering, persistence, side effects and potential federation in `Repo.transaction`, then invokes after-transaction side effects on success. A policy can transform or reject a message before persistence. Errors and rejection are distinct outcomes; asynchronous notifications and network delivery cannot be treated as one transaction across servers. `[source]` [pipeline](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/pipeline.ex#L27), [MRF](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/mrf.ex).

### Outbound delivery and fetch

The federator and publisher determine remote recipients and schedule signed deliveries. They group compatible recipients by inbox, including shared inboxes; blind recipients require separate treatment. A remote HTTP failure or offline destination does not roll back the original local post. See the [general delivery guide](../../federation/delivery/queues-and-retries.md) for the failure model; exact retry budgets and the selected Oban configuration need to be checked per deployment. `[source]` [federator](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/federator.ex), [publisher](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/publisher.ex), [publisher worker](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/workers/publisher_worker.ex).

Object and user fetchers resolve remote references; origin validation, authorization and safe destination checking remain distinct concerns from decoding JSON. A remotely supplied URL or an apparent actor ID should not be treated as proof of authority. `[source]` [object fetcher](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/object/fetcher.ex), [user fetcher](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/user/fetcher.ex).

## API coverage

The router exposes Mastodon-compatible endpoints as well as Pleroma/Akkoma-specific endpoints; this is a surface to test, not a claim of complete Mastodon parity. ActivityPub support described by the release is server-to-server, not a claim of full standard client-to-server support. Version-specific routes and response fields should be verified rather than inferred from a version string. `[source]` [router](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/router.ex), [federation document](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/FEDERATION.md).

## Federation behaviour

Akkoma 3.20.0 documents ActivityPub server-to-server, WebFinger, HTTP signatures and NodeInfo. Signed POSTs are required; signed GETs may be required by instance configuration. It explicitly says it does not perform JSON-LD processing. Its federation document lists FEP-67ff, 2c59, dc88, f1d5, fffd and c16b; consult each proposal and test actual behavior before treating a listing as proof of every optional feature. `[documented]` [release federation document](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/FEDERATION.md).

The same document explains the split-domain discovery requirement: WebFinger must accept a user account URI or actor ID as `resource`; a backlink can avoid ambiguity when the account and actor domains differ. MRF settings, account/domain blocks and visibility determine what survives local processing. The [visibility implementation](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/visibility.ex) uses more than a public/private flag. `[source]` [MRF](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/mrf.ex).

## Resource usage and tradeoffs

CPU, memory, network throughput and database size are **unmeasured** for this release. JSON-based representation supports a flexible vocabulary but makes JSONB indexes and query plans operationally important. PostgreSQL-backed work reduces the number of distinct persistence services but means job pressure competes for database resources. These are architectural observations, not measured claims. `[source]` [activity schema](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/activity.ex), [configuration](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/config/config.exs).

## Technical details and open questions

The source reviewed here is the independently verified v3.20.0 tag at the commit identified in the fact sheet. A separately supplied archive declares version 3.20.1 but lacks Git metadata, so it cannot establish a byte-identical v3.20.0 tree; the claims above were checked against the tag. Exact cross-server reaction translation, malformed-input behavior, queue recovery, performance and restore outcomes require version-pinned tests.

## Sources

- [Akkoma v3.20.0 source](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442) — pinned server implementation.
- [Federation document](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/FEDERATION.md) — release's supported protocols, FEP listing and discovery requirements.
- [Pipeline](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/pipeline.ex#L27) and [inbox controller](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/activity_pub_controller.ex) — transaction and request handling.
