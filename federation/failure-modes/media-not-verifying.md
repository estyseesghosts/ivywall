# Media appears missing in federation tests

A post can arrive before its attachment is ready, and a test can report a failure because it reads the wrong API field, cannot fetch a test server's HTTPS URL, or demands identical bytes after a server transforms an image. These outcomes look similar in a client but have different causes. The Pinetree/Birchtree laboratory provides a dated example of each kind of ambiguity; its test servers were minimal test implementations, and the findings below are historical test reports rather than general compatibility ratings.

## Expected and observed behaviour

A useful check distinguishes the remote post, its attachment metadata, a usable media URL, successful HTTP retrieval, and the semantics of the downloaded image. The benchmark's 19 October 2026 run 5 report lists 202 media-burst checks, of which 155 passed its byte-hash check. The remaining 47 were reported as Mastodon-involved: 18 `no-attachment`, seven HTTP 404 mismatches, and 22 HTTP 200 responses with differing bytes. A mismatch is the outcome of this particular oracle; it does not establish that all 47 attachments were unusable or that each failure had the same cause. `[reported]` [run 5 report, media burst](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L79-L82).

The operator's earlier investigation reported two relevant confounders: the media-fetch helper lacked the lab certificate authority for some HTTPS URLs, and some fetched Mastodon media had HTTP 200 with a different hash after transformation. Those observations cannot independently classify every run 5 row. `[reported]` [laboratory problems, item 44](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L177-L181).

## Root cause and affected versions

The laboratory report identifies Pinetree build `f58be005c558f650` and Birchtree build `e24d75aea1085a06` for run 5. Its separate interoperability section identifies Mastodon 4.7.3, but the media-burst rows do not independently identify the exact Mastodon image digest or all peer versions. Do not apply these outcomes to arbitrary releases or deployments. `[reported]` [run setup](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L8-L13), [interoperability section](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L98-L103).

The earlier feature checker initially inspected `files` or `attachments`, missing the Mastodon-shaped `media_attachments` field. The same record reports that the field was added. Another recheck reported attachments on Birchtree destinations after the feature check's wait had ended. These are reports about the laboratory's test implementation and particular samples; they do not prove that all other missing-media results were harmless delay. `[reported]` [field mismatch](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L101-L106), [recheck](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L168-L172).

## Code path

The version of the stress script committed with the later documentation reads `files`, `media_attachments`, or `attachments`, selects a URL and compares the SHA-256 of fetched bytes with the upload. It waits and polls until a deadline. This script snapshot is evidence of the recorded harness code; the report does not establish that the post-run snapshot is byte-for-byte the exact script used in run 5. `[source]` [stress harness](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/scripts/fediverse-bench/phase-stress.py#L374-L432).

## Reproduction

The original per-check artifacts, image digests and exact remote deployment configuration are needed to reproduce and classify individual run 5 rows; the summary alone does not provide them. For a new test, use isolated pinned servers and fixture media. Record the activity, remote post ID, API response and attachment fields, then poll the media URL to a stated deadline using the test CA. Record HTTP status, content type, size, hashes and whether the image decodes. Compare against both the original upload and any documented source-side derivative; a byte difference should be classified separately from an inaccessible or invalid image.

## Technical details

A test that only hashes bytes conflates two questions: whether a server made the media available and whether it preserved the original byte sequence. A server may transcode or strip metadata, so byte equality is useful when lossless preservation is the requirement but is not a universal playback oracle. This is a testing recommendation, not an observed result for every format or server.

## Sources

- [Run 5 report at commit 1c1d00c](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md) — dated historical summary, builds and media categories.
- [Laboratory problems record](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L101-L106) — field mismatch, rechecks and HTTPS test configuration caveats.
- [Stress harness at the same commit](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/scripts/fediverse-bench/phase-stress.py#L374-L432) — later committed media-check implementation.
