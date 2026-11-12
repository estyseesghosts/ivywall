# Test oracles that give false federation failures

An oracle is the check that decides pass or fail. In the laboratory, many apparent federation failures were wrong oracles, and several apparent successes were vacuous. This page lists them so a future harness avoids repeating them. The source is the October 2026 [laboratory](bench-evidence.md), `[reported]` and not rerun here

## Before you start

The failures below were found by a team building probes against Mastodon, Misskey, Catodon and Akkoma. They show how a harness can mislead, not what those servers do.

## False diagnoses

| Apparent result | Established cause | Evidence |
| --------------- | ----------------- | -------- |
| Every boost fails | The polling helper returned a truthy error string before delivery finished | `[reported]` [problem log item 24](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Replies lose their parent | Check read only Misskey's `replyId`; Mastodon-style APIs use `in_reply_to_id` | `[reported]` [items 25 and 41](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Media missing at a Mastodon-style API | Check read `files` and `attachments`, not `media_attachments`; or inspected a pending record | `[reported]` [items 26 and 51](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Akkoma reactions disappear | Check read favourites, not emoji reactions | `[reported]` [interop notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md) |
| Akkoma cannot find remote notes | The deployment had no search backend (404); the harness relied on search | `[reported]` [re-run notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md) |
| Mastodon media corrupted | Byte hash compared against the upload, but Mastodon re-encodes | `[reported]` [item 44](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Hundreds of follows missing | Follower list read without pagination, with relative and mixed-scheme `Link` headers | `[reported]` [item 22](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Follow not visible in the home timeline | A follow creates no status to find | `[reported]` [run 5](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) |
| Deletions failed | The check ran before remote timeline cleanup; all 8 converged later | `[reported]` [item 58](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Over-limit posts rejected | A 2,900-character post exceeds Mastodon's 500-character default | `[reported]` [item 43](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Unboost passes | The boost never arrived, so there was nothing to undo | `[reported]` [repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md) |
| Smoke suite passed | The federation stage was skipped, or the script exited 0 after 14 failures | `[reported]` [problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |

## Evidence model

Prefer five outcomes to a pass or fail bit:

| Classification | Meaning |
| -------------- | ------- |
| Verified compatible | Activity and resulting state checked at both ends |
| Verified incompatible | Reproducible protocol or semantic mismatch |
| Eventually convergent | Initial failure followed by confirmed correct state |
| Harness invalid | The measurement did not test the intended behaviour |
| Unresolved | Evidence is insufficient to attribute the behaviour |

Also record how each result was established: a running instance, a captured payload, source reading, or inference. This is the wiki's design recommendation; `[hypothesis]` until used.

## Technical details

Each such check should state: the exact API field read, the deadline and polling interval, how pagination is handled, whether the check could pass vacuously, and what state it saw at the destination. Two harness controls from the laboratory are worth copying: read the build id from the running process rather than the file on disk (a rebuild during a run changes the file but not the process), and kill the runner before its children.

## Pitfalls

- Treating a Mastodon-compatible API as Misskey-shaped, or the reverse.
- Counting an unresolved note as a federation failure when only the lookup route differs.
- Reporting the first-page result of any paginated list.

## Open questions

Which of the 62 failing run 5 feature checks would survive a corrected harness is unknown; the report lists unclassified pairs.

## Sources

- [Federation bench problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — items 22 to 28, 41, 43, 44, 51, 58
- [Pinetree bench re-run notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md) — Akkoma and Misskey oracle errors
- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — remaining unclassified rows
