# Failure mode: boosts not counted because the activity id is on the wrong host

A user boosts a remote post. Their own server shows the boost, but the post's origin never counts it and shows no new boosts. Nothing visible fails. Receivers that check that an activity's id belongs to the acting server quietly refuse activities whose id sits on a different server.

## Expected and observed behaviour

Expected: the origin counts the boost. Observed in the laboratory: a test server minted the `Announce` id by editing the boosted post's URI, so the id lived on the origin's host while the actor lived on the booster's host. These were laboratory runs of 19 October 2026 in which two minimal test servers (Pinetree and Birchtree) acted as probes against Mastodon, Misskey, Catodon and Akkoma peers.

| Receiver | Observed |
| -------- | -------- |
| Mastodon | Accepted and counted the boost |
| Misskey, Catodon, Akkoma | Boost not counted (inferred: the problem log says "evidently" refuse, from the missing counts, not from a receiver trace) |
| The test server's own strict receiver | HTTP 403 `URL failed verification: Domains do not match` |

`[reported]` [problem log item 39](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md), [repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md).

## Root cause

The sender's id host differed from the actor's host. A strict receiver compares the two and refuses. The sender then logged the delivery as complete because the failure was a 4xx the sending library treated as final, so nothing was visible from the sender. `[reported]` [repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md).

## Affected versions

| Software | Versions | Status |
| -------- | -------- | ------ |
| Test sender | Birchtree builds before the fix | Fixed to mint the wrapper under the booster's actor URI; verified live (a boost counted at the origin in 6 seconds) `[reported]` |
| Mastodon | lab build | Tolerated the malformed id |
| Misskey, Catodon, Akkoma | lab builds | Appeared to refuse it (inference) |

> Unknown: exact peer versions and the receiver-side trace for the three that did not count the boost.

## Technical details

```json
{
  "type": "Announce",
  "actor": "https://server-b.example/users/bob",
  "id": "https://server-a.example/users/alice/statuses/12345"
}
```

Hand-written illustration of the shape; the id host differs from the actor host.

**Requirement versus implementation policy.** These are different things and should not be conflated.

| Level | Statement | Status |
| ----- | --------- | ------ |
| Specification | A receiver must not trust an identifier or object it cannot attribute to the right authority, and it should guard against spoofing: an activity must not let one origin speak for another. `[spec]` ActivityPub 2018 §7 and security considerations B.* | requirement, but it names the goal (origin authorization), not a method |
| Implementation policy | Compare the host of the activity `id` with the host of the `actor` and refuse if they differ | a common, defensible check; it is stricter than the specification and would also refuse an arrangement where one organisation legitimately serves identifiers from a delegated or split domain |
| Sender convention | Mint the activity id on the acting actor's own host | what interoperates with strict receivers; follow it unless you control every peer |

So the lab results show that a hostname check is common among receivers, not that ActivityPub requires literal hostname equality. A receiver that is lenient, as Mastodon was here, still has to establish authority some other way, for example by refetching the object from its claimed origin; leniency without that is a security weakness. A sender-only fix cannot be tested against lenient receivers alone: Mastodon and the permissive test server both accepted the broken ids.

The same defect affected the `Undo(Announce)` id, so unboosts "passed" vacuously while the boost they undid had never arrived. `[reported]` [repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md).

## Reproduction

Send a signed `Announce` whose `id` host differs from `actor` host to each family, and compare local count, stored activity and HTTP status. Not yet run by this wiki.

## Sources

- [Birchtree federation repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md) — cause, receipts and fix
- [Federation bench problem log, item 39](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — the receiver table and live verification
- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — boost rows all passing after the fix
