# Failure mode: the same remote post is stored twice

A busy server sees two copies of one remote post: replies attach to one, edits apply to the other, and a delete removes only one. It happens when a remote note can arrive by several paths (an inbox `Create`, a fetch of a reply's parent, a lookup by URL) and those paths do not share one identity check.

## Expected and observed behaviour

In a laboratory run, a test server stored some remote notes twice, with different local ids and the same canonical URI; the fix log gives the mechanism but this wiki has not verified the duplicate counts. `[reported]` [Pinetree P1 fix log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-fixes-p1.md).

## Root cause

Two contributing mechanisms were found: no uniqueness constraint on the object's canonical URI, and a direct lookup path that used a different ingest routine from the inbox. Deduplicating by activity id alone prevents reprocessing one delivery, not creating two rows for one object. `[reported]` [Pinetree P1 fix log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-fixes-p1.md).

| Key | Prevents |
| --- | -------- |
| Incoming activity id | reprocessing the same delivered event |
| Canonical object URI | two local records for one remote object |

## Affected versions

| Software | Versions | Status |
| -------- | -------- | ------ |
| Test server | pre-fix builds | Fixed with a unique URI index and one shared ingest path; later storm test created no new duplicates `[reported]` |

> Unknown: whether any of Mastodon, Misskey, Catodon or Akkoma shows the same behaviour; the lab did not test it.

## Technical details

Existing duplicate rows were shadowed in the URI index, not deleted. The same shared-path rule also repaired a fetched note arriving without its reply link or media job. `[reported]` [Pinetree P1 fix log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-fixes-p1.md).

## Reproduction

Deliver a `Create` and trigger a lookup by URL for the same object concurrently; count rows for the canonical URI.

## Sources

- [Pinetree bench fixes, P1](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/state/logs/2026-10-17-bench-fixes-p1.md) — URI uniqueness and ingest unification
