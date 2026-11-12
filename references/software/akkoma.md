# Akkoma fact sheet

**Studied release:** Akkoma 2026.08 / v3.20.0, commit [`98fcccccb1534280960d7123620c03a54b4b2442`](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442). The tag commit is dated 8 August 2026; release publication date has not been independently checked. The original research labels 2026.08 as the 3.20 release series and focuses on v3.20.0, but its supplied archive declares 3.20.1 and has no Git metadata. It is not assumed identical to this tag; the facts below were checked separately against v3.20.0.

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | Elixir/OTP and Phoenix, retaining the `Pleroma` namespace. `[source]` [dependencies](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/mix.exs). |
| Persistence and jobs | Ecto/PostgreSQL with Oban background jobs. `[source]` [configuration](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/config/config.exs). |
| Client API | Mastodon-compatible and Pleroma/Akkoma-specific routes; complete parity is unverified. `[source]` [router](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/router.ex). |
| Federation | ActivityPub server-to-server, WebFinger, HTTP signatures and NodeInfo; no JSON-LD processing is claimed. `[documented]` [FEDERATION.md](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/FEDERATION.md). |

## Technical details

See the [Akkoma case study](../../servers/case-studies/akkoma.md) for the pipeline, storage and operational limits. No runtime interoperability or performance test is claimed.

## Sources

- [Akkoma v3.20.0 source](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442) — pinned implementation.
- [Release federation document](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/FEDERATION.md) — supported protocols and extensions.
