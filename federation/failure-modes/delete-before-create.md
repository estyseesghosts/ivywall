# Failure mode: a deleted post reappears

A post is created and quickly deleted. Some servers keep showing it. The cause is ordering: the `Delete` can be processed before the `Create` it refers to. The receiver has nothing to remove, forgets the delete, and then stores the late `Create`.

## Expected and observed behaviour

Expected: the note never appears, or disappears. Observed in the laboratory's churn test: residue on several families. Before a fix, a five-note probe left two deleted notes reachable on one test server and one on another. In run 5, the churn residue was 4, 4 and 4 on three Birchtree nodes, 2 on Misskey, 1 on Catodon and 2 on Akkoma. The Birchtree residue matched the Delete-beats-Create mechanism; the Misskey, Catodon and Akkoma residue was receiver-side and not classified per pair. `[reported]` [run 5](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md), [tombstone log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-tombstone-delete-before-create.md).

## Root cause

Handling `Delete` for an unknown object returned success and recorded nothing. In the lab's account, Misskey and Catodon sent `Delete` before the `Create` they raced with. A durable tombstone fixes it: record the deleted URI, then refuse a later `Create` for that URI. `[reported]` [tombstone log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-tombstone-delete-before-create.md).

```text
Without tombstone: Delete(unknown) -> discard; late Create -> note appears
With tombstone:    Delete(unknown) -> record URI; late Create -> rejected
```

## Affected versions

| Software | Versions | Status |
| -------- | -------- | ------ |
| Test servers | pre-fix builds | Fixed with a tombstone in Pinetree; Birchtree's contract describes one `[reported]` |
| Misskey, Catodon, Akkoma | lab builds | Residue seen; mechanism not isolated |

## Technical details

- **Authority.** A tombstone must be written only when the deleting actor owns the object URI, otherwise anyone could pre-delete someone else's future posts. Pinetree's rule: same host for actor and object, and not the local host. `[reported]` [tombstone log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-tombstone-delete-before-create.md).
- **Do not tombstone every delete.** Writing a tombstone when deleting a note you hold breaks a later legitimate refetch; Pinetree's first version did, and its conformance test caught it.
- **Caveat.** The post-fix live probe did not actually produce a Delete-before-Create ordering; the fix is established by deterministic handler tests. `[reported]` [tombstone log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-tombstone-delete-before-create.md).
- **Deletion is not timeline cleanup.** Eight run 5 delete checks failed at first, and a later read-only scan found the markers absent from every destination home timeline. That supports delayed disappearance only. See [life of a federated post](../activities/life-of-a-post.md).

## Reproduction

Needs controlled delivery delay: deliver `Delete` first, then `Create`, then inspect storage and timelines. Not yet run by this wiki.

## Sources

- [Pinetree tombstone investigation](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-tombstone-delete-before-create.md) — mechanism, fix and caveats
- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — churn residue per family
