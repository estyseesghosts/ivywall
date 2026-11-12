# A local federation lab

A lab runs two or more servers with working DNS, HTTPS, queues and request capture, so a federation result can be trusted. Two existing harnesses cover most of it and neither is portable as checked in. This page says what they provide, what to fix before reusing them, and the gates that separate a software incompatibility from a broken lab. Nothing here has been rerun by this wiki.

## Existing harnesses

| | Quick lab | Full lab |
| - | --------- | -------- |
| Source | Birchtree `scripts/lab/` | Pinetree `scripts/fediverse-bench/` |
| Servers | Birchtree and a real Mastodon 4.7.3 built from tag `8ff11c2b` | 10 nodes: three Pinetree, three Birchtree, Misskey, Catodon, Akkoma, Mastodon |
| Checks | the follow family in both directions (14 steps, `phase6-interop.sh`) | follows, features, stress, concurrent, cross-family and interop suites (`run-suites.sh`) |
| Network | Docker bridge `birchtree-lab` 172.28.0.0/24; TLS proxies for `mastodon.lab` and `birchtree.lab`; Postgres 16 and Redis 7 | the same lab network plus per-run Misskey and Catodon configs and an Akkoma container |
| Reset | `down.sh` | `bench-up.sh` starts from empty databases; `bench-down.sh`, `reset-lab.sh` |

`[source]` [Birchtree lab README](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/scripts/lab/README.md), [Pinetree `bench-up.sh`](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/scripts/fediverse-bench/bench-up.sh). The Birchtree result is limited to the follow family and is not full ActivityPub compliance.

## Before reusing either

- Both default to `/root` paths, expect prebuilt binaries and named containers, and assume Docker. `bench-up.sh` destroys all bench data and refuses to run under `/tmp`.
- `lib.py` already adapts Misskey-family and Mastodon-family APIs; it is the natural base for server adapters, with paths and ports moved to configuration.
- Separate three parts: provisioning (containers, networks, certificates, accounts, versions), test execution (adapters, no hard-coded paths) and evidence collection (requests, status codes, queue outcomes, API state, builds).

## Validity gates

Run these before any federation test, and fail the run, not the software, when one is false. Each comes from a mistake the laboratory made `[reported]` ([problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md)).

| Gate | Why |
| ---- | --- |
| Running binary hashes recorded from the process, not the file | a rebuild during a run changes the file but not the process (item 27) |
| Nothing else holds the ports; listener pid equals pid file | a stale node served old data (item 2) |
| Every hostname resolves from every container and from node processes that bypass `/etc/hosts` | Misskey and Catodon ignored the hosts file; Akkoma needed the CA at boot (items 12, 13) |
| One trusted lab CA everywhere, including the test harness's own HTTP client | untrusted HTTPS looked like missing media (item 44) |
| Identities use standard ports behind a proxy | Mastodon dropped non-standard ports (item 11) |
| Workers, queues and search backends are running | no search backend made polls "unresolvable" |
| Follower and timeline reads follow every page | a first-page read produced about 830 false missing follows (item 22) |
| Waits are bounded, observable, and end on a final-state assertion | a truthy error string ended a poll early (item 24) |

Every test needs a deadline and a final-state assertion; a non-empty diagnostic string is never proof of success.

## What a run records

Which servers exchanged the activity and their exact builds, what was sent (raw bytes where safe), where processing stopped, the stored state read at the destination, whether the test itself was valid, and whether the state converged. Use the [result format](../fixtures/result-schema.md) and the five outcomes in [test oracles](../interoperability/test-oracles.md). A provisioning failure must read differently from a federation failure.

## Sources

- [Birchtree lab README](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/scripts/lab/README.md) — topology and bring-up
- [Pinetree benchmark harness](https://github.com/estyseesghosts/pinetree/tree/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/scripts/fediverse-bench) — suites and setup scripts
- [Federation bench problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — the environment mistakes behind the gates
