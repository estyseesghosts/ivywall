# Media appears missing in federation tests

A federated post can arrive before its attachment is ready, and a test can report "missing" for reasons unrelated to federation. This page lists the causes found in the October 2026 [laboratory](../../testing/interoperability/bench-evidence.md); what servers actually do with remote media is on [remote media attachments](../compatibility/media-attachments.md).

## Expected and observed behaviour

Expected: every sent attachment is retrievable at the destination. Observed: of 202 media-burst checks in run 5, 155 passed a byte-hash comparison; the other 47 all involved Mastodon (18 no attachment visible, 7 HTTP 404, 22 HTTP 200 with different bytes). A mismatch is the outcome of one oracle; it does not show the 47 attachments were unusable or shared a cause. `[reported]` [run 5 report](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L79-L82).

## Root cause

Test-side causes the laboratory found, each a [test-oracle](../../testing/interoperability/test-oracles.md) error:

1. **Wrong API field.** The checker read `files` or `attachments`, not Mastodon-style `media_attachments`. `[reported]` [field mismatch](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L101-L106).
2. **Too early.** A pending attachment record exists before its bytes do; a recheck found the attachments after the wait had ended. `[reported]` [recheck](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L168-L172).
3. **No lab CA.** The fetch helper could not open some HTTPS media URLs. `[reported]` [item 44](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L177-L181).
4. **Wrong baseline.** Mastodon re-encodes uploads, so a hash of the original upload cannot match.

These do not prove every other missing-media result was harmless delay. Only the separate direct-interoperability section names Mastodon 4.7.3; the media-burst rows do not identify the Mastodon image, so do not apply them to a release. `[reported]` [run setup](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L8-L13), [interoperability section](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L98-L103).

## Code path

The stress harness reads `files`, `media_attachments` or `attachments`, picks a URL and compares the SHA-256 of fetched bytes with the upload, polling to a deadline. It is the committed snapshot, not proven to be the exact script run. `[source]` [stress harness](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/scripts/fediverse-bench/phase-stress.py#L374-L432).

## Reproduction

Needs the original per-check artifacts and image digests, which the summary lacks. For a new test: pinned servers, fixture media, poll the media URL to a stated deadline with the test CA, and record status, type, size, hashes and whether the image decodes. Compare against the origin's served file as well as the upload.

## Technical details

A byte hash answers "was the original preserved", not "was media made available". Use it only when lossless preservation is the requirement.

## Sources

- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md) — media categories and builds
- [Laboratory problems record](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L101-L106) — field mismatch, rechecks, HTTPS caveats
- [Stress harness](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/scripts/fediverse-bench/phase-stress.py#L374-L432) — media-check implementation
