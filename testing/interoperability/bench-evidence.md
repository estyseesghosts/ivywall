# Reading federation benchmark results

A federation benchmark is a set of experiments, not a compatibility certificate. It can show that a particular operation was observed under a particular setup, but an HTTP response, a successful test assertion and a remote user's final view are different evidence. This page records the scope and measurement limits of a historical Pinetree/Birchtree laboratory run; those two programs were minimal test implementations, not authoritative reference servers for the protocols or other software.

## Before you start

The report for the 19 October 2026 run identifies a ten-node laboratory and a fresh run at `20261019T181810Z`. It reports Pinetree executable hash prefix `f58be005c558f650` and Birchtree executable hash prefix `e24d75aea1085a06`; those are build identifiers, not verified source commit IDs. The report includes Mastodon, Misskey, Catodon and Akkoma peers, but does not establish exact versions for every peer in the quoted results. Treat those peers' versions as unknown rather than applying the findings to current releases. `[reported]` [run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md), [run log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-run5-log.md).

## Interpret the result, not just the label

The run report lists 1,108 passing and 62 failing feature checks, and 162/162 cross-family checks passing. Those are counts from different suites and criteria: neither is an overall compatibility percentage. The report's own scope excludes some third-party pairs from its product-work tally, even though they appear in the total. It also lists unresolved cases and inherited classifications; these are not confirmed root causes merely because a summary assigns blame. `[reported]` [run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md).

A benchmark should record the activity and object identifiers, the source and destination software versions, HTTP responses, elapsed time, the exact query used by the checker, and final state at the destination. For asynchronous federation, distinguish a timeout from a permanent failure and a missing timeline entry from a missing object. `[spec]` ActivityPub recommends asynchronous delivery and retry for network failures; it does not promise a global completion time. See [server-to-server delivery](../../fundamentals/activitypub-s2s.md).

## Technical details

The historical run's feature suite counted eight delete checks as failures during its window. Its report says a later read-only recheck found the markers absent from destination home timelines. This is evidence of the report's described later state, not a measured universal deletion latency or proof that all copies were erased. The exact recheck timing and the individual raw captures are not provided by the cited report. `[reported]` [run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md).

The feature harness source at the cited repository snapshot says its media check looks for an attachment and compares the SHA-256 hash of the retrieved bytes with the uploaded original, after a configurable settle period and deadline. A mismatch alone cannot establish failed federation: a server may legitimately transform media. Conversely, an attachment record alone does not prove playable bytes are retrievable. Check the operation's intended contract separately from byte-for-byte preservation. The source snapshot is evidence of that code, not proof that it exactly matched the executed harness without a run-specific commit record. `[source]` [feature harness](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/scripts/fediverse-bench/phase-features.py); `[reported]` [run 5 media classifications](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md).

## Pitfalls

- **Counting a test oracle as the protocol:** read what the check actually observes, its deadline and any assumptions about pagination, indexing, encoding or privacy.
- **Treating a 2xx as end-to-end success:** inspect the receiving server's state and client-visible result after its queue has processed.
- **Assigning a cause from a failure count:** separate direct observations from an operator's diagnosis and reproduce suspected causes in isolation.
- **Generalizing across releases:** record each peer's exact image or commit, configuration and build; otherwise mark the version unknown.
- **Publishing sensitive captures:** use test actors and redact tokens, keys and non-public content.

## Open questions

The cited report does not include sufficient version and raw-event detail to reproduce every matrix cell. A new run with immutable images, captured per-cell requests and remote-side assertions is needed before using the results as a version-specific compatibility matrix. No live test was rerun for this page.

## Sources

- [Pinetree laboratory run 5 report, repository snapshot f1665e6](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — historical counts, scope, follow-up and unresolved classifications.
- [Run 5 log at the same snapshot](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-run5-log.md) — setup and run-level notes.
- [Feature harness at the same snapshot](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/scripts/fediverse-bench/phase-features.py) — later source snapshot's check implementation; exact executed revision unverified.
- [ActivityPub Recommendation §7.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery) — asynchronous delivery and retries.
