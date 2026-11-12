# Testing

Manual research does not scale, and compatibility claims go stale. This section is for a companion lab: a controller creates actors, posts, follows and failure scenarios against many servers, and captures HTTP traces, database state, delivery results and API responses as machine-readable fixtures that can generate the compatibility pages. The proposed wiki test lab does not exist yet; historical external lab reports can still provide bounded evidence.

## Pages

- [A local federation lab](harness/local-lab.md) — the two existing harnesses, what to fix before reuse, and the gates that separate lab faults from software faults.
- [Fixture corpus](fixtures/index.md) — signing vectors and quote payloads, with provenance and verification status.
- [FediTest](interoperability/feditest.md) — what the existing test suite covers, and its age.
- [An interoperability test matrix](interoperability/test-matrix.md) — what a new server should test, per area and direction.
- [Test oracles that give false federation failures](interoperability/test-oracles.md) — harness mistakes and a five-way outcome model.
- [Interoperability result fixture format](fixtures/result-schema.md) — the directional, versioned record each result is stored as.
- [Reading federation benchmark results](interoperability/bench-evidence.md) — scope, test oracles and limits of a historical run.

Not yet covered (the interoperability pages above and the fixture format exist):

- Harness — controller design and server set (Mastodon, Misskey, Akkoma, GoToSocial, snac and others). Nothing is running.
- Interoperability runs — successful and malformed activities, arrival orders, duplicate delivery, remote downtime, key rotation, privacy-boundary checks, run against pinned peers.
- Benchmarks — delivery throughput, p95 latency, queue growth, memory, database size, network traffic, CPU, recovery.

## Notes and open questions

> Unknown: which existing tools to build on. FediTest and the Fediverse Schema Observatory are the first candidates to evaluate.

## Sources

- [FediTest](https://feditest.org/) — existing protocol test framework
- [Fediverse Schema Observatory](https://observatory.cyber.harvard.edu/) — real-world ActivityPub schema data
