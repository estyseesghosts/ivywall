# Fixture corpus

Machine-readable inputs and expected results that a developer can run against their own parser or state machine without deploying other servers. Every fixture states where it came from and what has actually been verified; the format for results is in [result format](result-schema.md). A fixture proves what is written in its row and nothing more.

## What is here

| Fixture | Kind | Producer and receiver | Expected | Verified |
| ------- | ---- | --------------------- | -------- | -------- |
| [`signing/vectors.json`](signing/vectors.json): 8 HTTP signature requests, 4 legacy and 4 RFC 9421, each valid or invalid for one stated reason | constructed with a throw-away key whose private half was deleted; hosts are `.example` | none; usable against any verifier | the `expected` field of each vector: verifies, or the rejection reason | `python3 tools/signing_vectors.py verify` passes 8 of 8 (CI). One implementation checks them; no second verifier has |
| [`quotes/misskey-quote-create.json`](quotes/misskey-quote-create.json): a `Create` of a quote note | captured from a native Misskey 2026.10.1-alpha.1 rig by the Birchtree project; carries only `_misskey_quote` and `quoteUrl` | Misskey, parsed by Birchtree (commit `f09ec35`) | parses as a quote; the target is the `_misskey_quote` value; no FEP-044f `quote` | Birchtree test `misskey_quote_create_parses` `[reported]`, not rerun here |
| [`quotes/pinetree-quote-create.json`](quotes/pinetree-quote-create.json): a `Create` of a quote note | produced by Pinetree, a test server, so it shows a superset shape rather than a real peer's | Pinetree, parsed by Birchtree (commit `f09ec35`) | parses; all four quote spellings present and the canonical `quote` wins; a `canQuote` policy is present | Birchtree test `quote_aliases_merge_with_canonical_priority` `[reported]` |

Why the quote pair matters: before the fix, a quote with several spellings failed with `duplicate field 'quote'` and the whole activity was refused with 422. A parser should read each spelling into its own slot and prefer the canonical one. See [quotes](../../federation/compatibility/quotes.md).

## Rules for fixtures

- Keep the original body bytes. Re-formatting JSON changes the bytes a body digest was computed over; the signing vectors store the body as an exact string.
- State whether a fixture is captured or constructed, the producer and receiver builds, the expected behaviour and what has been verified.
- Never include a real key, token or non-public content. Public keys and throw-away test keys are fine.
- Validate in CI: every JSON file parses, and signing vectors behave as expected. Live multi-server runs are separate and more expensive.

## Planned families

Duplicate `Create`; `Delete` before `Create`; `Undo` before its activity; reused `Undo` id; `Announce(Create)` from a community; emoji encodings; poll votes as `Note` and as `Answer`; signed `GET` with redirects; alternative JSON-LD contexts; delayed media. The first four are exercised by the [minimal actor](../../guides/minimal-actor.md) self-test but are not yet extracted as files.

## Sources

- [Birchtree test fixtures](https://github.com/estyseesghosts/birchtree/tree/f09ec359af00233530a230b9242f8321578e6e37/tests/fixtures) — origin of the two quote payloads
- [Birchtree `quote_fed_interop.rs`](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/tests/quote_fed_interop.rs) — the tests that parse them
- [HTTP signatures](../../fundamentals/http-signatures.md) — the schemes the signing vectors cover
