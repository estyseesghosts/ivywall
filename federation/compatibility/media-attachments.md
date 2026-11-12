# Compatibility: remote media attachments

A post and its attachment arrive separately. Servers disagree about when the attachment becomes visible through their API, which URL they expose while it is pending, and whether they keep the original bytes. The October 2026 [laboratory](../../testing/interoperability/bench-evidence.md) results below are `[reported]`, not rerun here, and peer builds are unrecorded unless stated

## Summary

| Server | Observed behaviour | Evidence |
| ------ | ------------------ | -------- |
| Mastodon | Exposes `remote_url` immediately and leaves `url` empty until the local copy is processed | `[reported]` [lab repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md) quoting `media_attachment_serializer.rb` lines 25 to 33 |
| Mastodon | Re-encodes uploaded media, so bytes served by the origin differ from the uploaded file | `[reported]` [media investigation](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-20-media-federation.md) citing `lazy_thumbnail.rb` and `media_attachment.rb` |
| Misskey, Catodon, Akkoma | Delivered media to the lab Mastodon with no attachment visible there in 9 run 5 rows | `[reported]` [run 5](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) |
| Test servers | Different pending models: one hides the file until fetched, one shows a record with `url: null` | `[reported]` [repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md) |

In run 5's media burst all 47 transfers that failed a byte-hash check involved Mastodon; why, and how the checks misled, is on [media appears missing in federation tests](../failure-modes/media-not-verifying.md). The longest arrival delay after settling was 6.1 seconds. `[reported]` [run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md).

## Information lost in translation

- **A pending attachment is not a failed one.** Attachment record present with `url: null` means metadata exists and bytes may still be processing. Absent attachment may mean not yet fetched, omitted, unsupported or lost.
- **Byte equality is the wrong baseline for Mastodon.** The correct comparison is the file the origin serves after its own processing, and even then a receiver may transform it again. `[reported]` [media investigation](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-20-media-federation.md).
- **The 404 rows carry the destination's own cache path.** The failing URL was Mastodon's own `system/cache/` path, meaning the row existed but the bytes were never servable, through a fetch or storage failure, or Sidekiq lag. Independent senders failed identically. `[reported]` [media investigation](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-20-media-federation.md).

## Technical details

| Attachment as seen in an API | Likely meaning |
| ---------------------------- | -------------- |
| Absent | unfetched, omitted, unsupported or missing |
| Present, `url: null`, `remote_url: null` | pending and no fallback |
| Present, `url: null`, `remote_url` set | pending; origin URL usable as a fallback |
| `url` set | a served copy exists; may be transformed |

The zero-record case at a Mastodon destination (no attachment at all after delivery) was unexplained: 0 of 34 deliveries into the lab Mastodon from five senders produced an attachment, while a separate direct suite against real Mastodon 4.7.3 did transfer media. The lab's Sidekiq and Rails logs were not retained, so the mechanism is unproven. `[reported]` [media investigation](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-20-media-federation.md).

**Coverage limit.** The fixture was a 69-byte PNG. Nothing here speaks for large JPEGs, animated GIFs, video, audio, authenticated fetches, redirect chains or CDN failures. `[reported]` [repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md).

## Test procedure

Use pinned images and several fixture files (PNG, large JPEG, GIF, short video). Record timestamps for: note received, attachment row created, download started and finished, processing finished, first successful served URL. Compare served bytes to the origin's post-processing bytes and to the original upload separately, and check decoding.

## Sources

- [Birchtree federation repair notes](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/federation_repair.md) — pending-media models and the Mastodon serializer comparison, at Birchtree f09ec35
- [Birchtree media federation investigation](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/state/logs/2026-10-20-media-federation.md) — the three verdicts for Mastodon-involved media failures
- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — counts, categories and arrival delay
