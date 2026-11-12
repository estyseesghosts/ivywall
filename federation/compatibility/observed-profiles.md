# Compatibility: observed profiles of Mastodon, Misskey, Catodon, Akkoma and Sharkey

A one-page index of how five server families behaved when third-party servers talked to them in the October 2026 [laboratory](../../testing/interoperability/bench-evidence.md). It is a router into the per-feature records, not a ranking; results are `[reported]`, not rerun here, and peer builds are unrecorded unless stated.

Sharkey appears only in an earlier four-server suite (Pinetree, Misskey, Sharkey), recorded in Pinetree's smoke notes against Sharkey 2025.4.7 and Misskey 2026.10.1-alpha.0; it was not a node in the ten-node runs. `[reported]` [Pinetree audit](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/audit-2026-10-16-phase0-to-now.md).

## Summary

| Family | Distinctive observed behaviour | Where it is recorded |
| ------ | ------------------------------ | -------------------- |
| Mastodon | did not discover test servers on non-standard ports (HTTPS-only WebFinger itself is required by RFC 7033, so the port handling is the finding); accepted an Announce whose id was on a different host; reused a `Undo(Follow)` id; re-encodes media; had fewer visible posts after 180 seconds in the post storm; first contact `Follow` occasionally answered 422 | [discovery](../../fundamentals/webfinger.md), [wrong-domain ids](../failure-modes/wrong-domain-activity-ids.md), [Undo](../failure-modes/undo-ignored-or-deduplicated.md), [media](media-attachments.md), [first contact](../failure-modes/first-contact-races.md) |
| Misskey | Reactions as `Like` with `_misskey_reaction`; `closed` on polls; did not apply some `Undo(Announce)`; `renoteCount` not decremented in a local test; concurrent first lookups raced; DNS path ignored the hosts file | [reactions](emoji-reactions.md), [polls](polls.md), [Undo](undo-and-reposts.md) |
| Catodon | Misskey-derived but not wire-identical: polls from some voters not tallied, correlated with a `#` fragment in the vote activity id | [polls](polls.md) |
| Akkoma | Separate `EmojiReact`; `Create(Answer)` poll votes; poll options must be typed `Note`; `publicKeyPem` with two trailing newlines; mentions without a tag; `Undo` must name an existing activity; no search backend in the lab | [reactions](emoji-reactions.md), [polls](polls.md), [mentions](mentions.md), [Undo](undo-and-reposts.md), [HTTP signatures](../../fundamentals/http-signatures.md) |
| Sharkey | Misskey-family quote metadata, timestamp-style poll closure noted by the investigators; follow requests to a locked account stay pending | [quotes](quotes.md) |

Peer builds were not recorded in the cited reports apart from the Mastodon 4.7.3 direct suite and the Sharkey and Misskey pins above. Add a row with versions when a pinned rerun exists.

## Reading the results

Basic social-graph activity (follows, posts, replies, likes, boosts, most deletes) exchanged cleanly across all five families in the final run (162 of 162 cross-family checks); the failures cluster in reactions, poll votes, quote authorization, media and reversing actions. The counts come from different suites and are not a compatibility percentage: see [reading federation benchmark results](../../testing/interoperability/bench-evidence.md).

## Sources

- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — final counts and classifications
- [Pinetree audit, 16 October](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/audit-2026-10-16-phase0-to-now.md) — Misskey and Sharkey version pins
- [Federation bench problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — per-family findings with item numbers
