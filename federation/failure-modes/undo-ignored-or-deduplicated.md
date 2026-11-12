# Failure mode: an Undo has no effect

A user unfollows, un-likes or un-boosts and the other server still shows the relationship. Two different mechanisms produced this in the laboratory, and a third (the origin not applying the `Undo`) is covered on [Undo, boosts and unboosts](../compatibility/undo-and-reposts.md).

## Expected and observed behaviour

### Mastodon reused an `Undo(Follow)` id

Mastodon resent an `Undo(Follow)` with an id (`…#follows/N/undo`) it had already used for an earlier `Undo` that had no effect. The receiving test server had recorded that first, ineffective `Undo` as processed, so the later, meaningful one was dropped as a duplicate and the follower relationship stayed. The fix was to roll back the dedup record when the outcome was ignored. `[reported]` [Birchtree phase 6 verification](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md).

### Akkoma dropped an `Undo(Like)` naming a missing activity

See the table on [Undo, boosts and unboosts](../compatibility/undo-and-reposts.md). The `Undo` was dropped silently because its object did not match a stored activity. `[reported]` [bench re-run](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md).

## Root cause

- **Deduplication is not application.** Recording an activity id as seen before knowing the activity changed any state turns a no-op into a permanent block.
- **Undo must name the earlier activity.** Internal row ids and federated ids are different things.

## Affected versions

| Software | Versions | Status |
| -------- | -------- | ------ |
| Mastodon | 4.7.3 direct suite | Observed reusing the `Undo(Follow)` id |
| Akkoma | lab build, version not recorded | Drops an `Undo` whose object it cannot find |

## Technical details

The rule for receivers: only record a dedup key for an outcome that applied or is permanently invalid; a retryable or no-op outcome must leave no record. A server also has to separate `Undo` of a follow, a like, a reaction and an announce, since each targets a different stored thing.

## Reproduction

Send `Undo(Follow)` twice with the same id, first when no follow exists and then after one does. Send `Undo(Like)` naming an id the receiver never stored. Compare state after each.

## Sources

- [Birchtree phase 6 verification](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md) — Mastodon id reuse and the dedup rollback
- [Pinetree bench re-run notes](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-rerun.md) — Akkoma `Undo` validator behaviour
