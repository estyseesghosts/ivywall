# Testing

Manual research does not scale, and compatibility claims go stale. This section is for a companion lab: a controller creates actors, posts, follows and failure scenarios against many servers, and captures HTTP traces, database state, delivery results and API responses as machine-readable fixtures that can generate the compatibility pages. The proposed wiki test lab does not exist yet; historical external lab reports can still provide bounded evidence.

## Pages

- [Reading federation benchmark results](interoperability/bench-evidence.md) — scope, test oracles and limits of a historical run.

Planned:

- Harness — controller design and server set (Mastodon, Misskey, Akkoma, GoToSocial, snac and others).
- Fixtures — machine-readable results, naming and schema.
- Interoperability — successful and malformed activities, arrival orders, duplicate delivery, remote downtime, key rotation, privacy-boundary checks.
- Benchmarks — delivery throughput, p95 latency, queue growth, memory, database size, network traffic, CPU, recovery.

## Notes and open questions

> Unknown: which existing tools to build on. FediTest and the Fediverse Schema Observatory are the first candidates to evaluate.

## Sources

- [FediTest](https://feditest.org/) — existing protocol test framework
- [Fediverse Schema Observatory](https://observatory.cyber.harvard.edu/) — real-world ActivityPub schema data
