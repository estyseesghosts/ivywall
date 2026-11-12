# Compatibility: Undo, boosts and unboosts

Reversing an action is where federation most often goes quietly wrong. A boost or a like arrives, is applied, and later the sender takes it back; whether the origin server reverses it depends on exactly which activity the sender names, which API route the user used, and whether the origin applies an `Undo` it receives. The October 2026 [laboratory](../../testing/interoperability/bench-evidence.md) results below are `[reported]`, not rerun here, and peer builds are unrecorded unless stated

## Summary

The table records what the laboratory observed for reversing a boost, by the server named in the first column, which is the origin (the server holding the boosted post) except in the Mastodon row. `Undo(Announce)` is the activity that withdraws a boost.

| Origin server | Observed when an `Undo(Announce)` was sent to it | Evidence |
| ------------- | ------------------------------------------------ | -------- |
| Mastodon 4.7.3 (as the booster, not the origin) | Deleting its own reblog decremented a test origin within 6 seconds, so it emits the `Undo`; Mastodon as an origin was not recorded separately | `[reported]` [problem log item 52](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Akkoma (build not recorded) | Rows where Akkoma was the origin stayed red for every booster, including Mastodon, which provably sent the `Undo`; attributed by the operator to Akkoma not applying it | `[reported]` [problem log item 53](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Misskey (build not recorded) | Five unrelated booster implementations all failed to reverse; separately a local-only test showed `renoteCount` not decreasing | `[reported]` [problem log item 47](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md), [re-run notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md) |

Run 5 ended with 17 unresolved unboost rows: nine with Akkoma as origin and eight with Misskey as origin. The report attributes both groups to the origin server, but gives no receiver-side trace. Treat the attribution as `[hypothesis]` until an inbound handler trace exists.

## Information lost in translation

- **A `Delete` of the repost wrapper is not an `Undo`.** On Mastodon-style APIs, deleting the status that wraps a boost is a different request from the explicit unreblog route. A sender that only emits `Delete` leaves the origin's own boost index and counter unchanged. In the lab the origin kept counting the boost until the sender also emitted `Undo(Announce)`. `[reported]` [problem log item 52](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md).
- **Counters are not records.** A Misskey checkout removed the renote row but left the origin note's `renoteCount` at 1, with no federation involved. A stale counter does not prove the interaction survived. `[reported]` [re-run notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md).
- **Akkoma's two routes differ.** On the tested Akkoma, `DELETE /api/v1/statuses/{wrapper}` returned 404 `Record not found`, while `POST /api/v1/statuses/{id}/unreblog` returned 200 and the remote count fell from 2 to 1. Concluding that Akkoma cannot send `Undo(Announce)` from the first result would be wrong. `[reported]` [re-run notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md).

## Technical details

**Reactions are reversed by naming the earlier activity.** Akkoma's `UndoValidator` requires an `Undo`'s object to be an existing activity; otherwise the `Undo` is dropped with no log line. A sender that federated a `Like` under one id and then sent `Undo(Like)` naming a different (internal) id saw the favourite remain on Akkoma. After the sender stored and reused the exact federated id, the live probe showed the favourite and the emoji reaction both removed. `[reported]` [bench re-run, live A/B](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md); the validator path is from the same log, not read from Akkoma source by this wiki.

| Probe on Akkoma | Before the sender fix | After |
| --------------- | --------------------- | ----- |
| Add heart favourite | listed | listed |
| Undo heart | favourite remained | removed |
| Add emoji reaction | count rose | count rose |
| Undo emoji reaction | remained | count back to 0 |

**Separate outcome classes.** For a reversal, record the interaction and its counter independently:

| Condition | Meaning |
| --------- | ------- |
| Interaction removed, counter reduced | complete |
| Interaction removed, counter unchanged | counter maintenance or stale read |
| Interaction present after an `Undo` was received | receiver `Undo` processing problem |
| Interaction present and no `Undo` received | sender, delivery or routing problem |

This is the wiki's own synthesis, labelled `[hypothesis]` as a method; it is not a finding from the lab.

## Test procedure

For each ordered pair (booster server, origin server): boost, confirm the origin's list and counter, reverse by each available route (explicit unreblog, `DELETE` of the wrapper, native client action), capture the outgoing activity, confirm what the origin did, then replay the original `Announce` and confirm it is not resurrected. See the [test matrix](../../testing/interoperability/test-matrix.md).

## Sources

- [Federation bench problem log, items 47, 52, 53 and 54](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — unboost attribution and the reblog-delete fix, at Pinetree f1665e6
- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — unboost rows after the fix, and the 17 unresolved
- [Bench re-run notes, 17 October](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md) — Akkoma `Undo(Like)` live A/B, Akkoma unreblog route, Misskey `renoteCount`
