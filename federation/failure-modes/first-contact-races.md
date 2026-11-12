# Failure mode: the first request to a new remote server fails

Everything works between two servers that already know each other, but the very first follow, lookup or delivery fails or takes many seconds. First contact does extra work (resolve the handle, fetch the actor, store a key, sometimes generate one) and each step can race or time out.

## Expected and observed behaviour

| Where | Observed | Evidence |
| ----- | -------- | -------- |
| Mastodon as receiver | A new server's first inbound `Follow` was handled about 17 seconds after arrival: Mastodon's proxy logged 499 and Sidekiq `elapsed=10.028`, then it succeeded on retry. Cause on the sender: RSA key generation on first use, longer than Mastodon's 10-second timeout | `[reported]` [Birchtree phase 6 verification](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md), [phase 6 log](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-17-phase-6-federation.md) |
| Mastodon as receiver | About one in 9,180 first-contact follows from a Misskey user got HTTP 422; Misskey did not retry a permanent 4xx. In run 5 three edges stayed missing, all `mastodon/u0` following Misskey or Catodon users. Cause unclassified | `[reported]` [problem log items 35 and 57](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Misskey as the resolver | Two concurrent first lookups of a remote server sometimes failed with a duplicate-key insert; not fixed upstream in the lab, the harness retried after 2 seconds | `[reported]` [problem log item 21](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| A test sender | Two concurrent requests created two different keys for one actor, so peers cached a key that was then replaced | `[reported]` [problem log item 18](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |
| Test receiver | After a signature failure it kept using a cached remote key for 24 hours, returning 401. Fix: refetch the key once, with a 60-second cooldown, then recheck | `[reported]` [problem log item 20](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) |

## Root cause

Lazy initialisation on the first request, non-atomic creation of remote-account or key records, and receivers with short timeouts. For the 422 there is no confirmed cause: Mastodon's log showed only the status line and no exception.

## Affected versions

| Software | Versions | Status |
| -------- | -------- | ------ |
| Mastodon | 4.7.3 and the lab build | Observed; 422 cause unknown |
| Misskey | lab build | Race observed, not fixed |

## Technical details

Invariants for a new implementation: generate actor keys at account creation, never on the first request; create remote actors atomically (insert-or-fetch); keep a bounded forced key refresh after a verification failure; make first-contact failures observable. Mastodon's 10-second inbound handling window is the budget to stay within. `[reported]` [Birchtree phase 6 log](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-17-phase-6-federation.md).

## Reproduction

Start a fresh server and follow a Mastodon account from it with no warmed state. Record timings at each hop. For the Misskey race, issue concurrent first lookups of the same remote handle. Not yet run by this wiki.

## Sources

- [Birchtree phase 6 verification](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md) — the 17-second first Follow and the fix timings
- [Birchtree phase 6 log](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-17-phase-6-federation.md) — the keygen stall explanation
- [Federation bench problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — items 18 to 21, 35 and 57
