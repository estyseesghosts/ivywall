# FediTest

FediTest is an existing framework for testing Fediverse software, and its test repository is the closest thing to a ready-made starting point for this wiki's [test matrix](test-matrix.md). It is smaller and older than its website suggests: the repository's last commit is 29 December 2024, so treat it as a source of test designs, not a current conformance suite. `[observed]` repository history at commit `cdbb467`, checked 2026-11-12.

## What exists

| Directory | Contents |
| --------- | -------- |
| `tests/` | the executable tests: 21 Python test files: 11 WebFinger server tests numbered by RFC 7033 section, plus `system2` (two nodes) and `system3` (three nodes), plus empty `activitypub` and `swicg_activitypub_http_signature` placeholders with only a `TEST-SOURCES` note |
| `tests.to-be-done/` | 32 further files across `activitypub`, `webfinger` and `swicg_activitypub_http_signature` that are planned, not run |

Executable two-node tests: delete, direct addressing, follow receive, like, preserve links, reply, update. Three-node tests: announce, delete and update through an intermediate server. Each test records a specification level and an interoperability level, which separates "the specification says this" from "peers need this to work together". `[observed]` source files at the commit above.

Do not count `tests.to-be-done/` as coverage. Update-with-dropped-optional-field tests, for example, are there but not executable.

## Use in this wiki

- The single-hop and double-hop update tests create a note, wait for delivery, edit it and check the recipient's copy. They are the model for verifying the [post-edit record](../../federation/compatibility/post-edits.md), where Misskey skips `Update(Note)` and Catodon applies it.
- A wiki result should still record exact builds and keep the five-way classification from [test oracles](test-oracles.md); FediTest's pass or fail does not.
- Compare its result format with the [fixture format](../fixtures/result-schema.md) before the first run.

## Sources

- [feditest-tests-fediverse at commit cdbb467](https://github.com/fediverse-devnet/feditest-tests-fediverse/tree/cdbb4672437b2e09e7c1305a91a12d1081ca811b) — tests, planned tests and their sources
- [FediTest](https://feditest.org/) — the framework and quickstart
