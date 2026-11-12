# An interoperability test matrix for a new server

A list of what to test when a new server must federate with Mastodon, Misskey, Catodon, Akkoma and their relatives. It is derived from failures in the October 2026 laboratory, so every row exists because something actually broke or was mistaken for breaking. It is a design recommendation (`[hypothesis]` as a method), not a result.

## Before you start

Use pinned images and record every version. Fixture accounts only. For each case record the sender, the receiver, the activity payload, the HTTP outcome, and the eventual state at both ends. Success needs evidence of state, not an HTTP 200 or 202. Read [reading federation benchmark results](bench-evidence.md) first; [FediTest](feditest.md) has executable designs for several rows.

## The matrix

| Area | Required cases | Why (what broke) |
| ---- | -------------- | ---------------- |
| Discovery | WebFinger over HTTPS, canonical actor URI, redirects, non-standard ports | HTTPS-only WebFinger is required by RFC 7033; what was Mastodon-specific in the lab was the dropped non-standard port ([WebFinger](../../fundamentals/webfinger.md)) |
| Signatures | key rotation, PEM whitespace, signed GETs, missing or bad signatures, both schemes, `Digest` and `Content-Digest`, malformed digest, modified body | Akkoma PEM, stale keys, scheme mismatch ([HTTP signatures](../../fundamentals/http-signatures.md)) |
| Serialisation | equivalent JSON-LD forms: alias or compact IRI, array versus single value, nested context | servers that match one shape ([ActivityStreams](../../fundamentals/activitystreams.md)) |
| Follow | open and locked accounts, Accept, Reject, cancel, `Undo` replay | pending versus accepted; `Undo(Follow)` id reuse ([failure mode](../../federation/failure-modes/undo-ignored-or-deduplicated.md)) |
| Object identity | same note by inbox and by direct fetch, concurrently | duplicate rows ([failure mode](../../federation/failure-modes/duplicate-remote-objects.md)) |
| Activity authority | id on the wrong host; actor and object owned by different servers | [wrong-domain ids](../../federation/failure-modes/wrong-domain-activity-ids.md) |
| Delivery order | `Create`/`Delete`, `Follow`/`Undo` in both orders | [deleted post reappears](../../federation/failure-modes/delete-before-create.md) |
| Reactions | plain like, emoji like, `EmojiReact`, several distinct emoji, `Undo` | [reactions](../../federation/compatibility/emoji-reactions.md) |
| Reposts | `Announce`, `Undo`, delete of the wrapper, counters | [Undo and unboosts](../../federation/compatibility/undo-and-reposts.md) |
| Polls | `Note`-typed options, future `closed` timestamp, `Note` and `Answer` votes | [polls](../../federation/compatibility/polls.md) |
| URI forms | vote ids with path, fragment, query string | Catodon vote tallies |
| Replies | parent present, absent, late, inaccessible | [missing replies](../../federation/failure-modes/missing-replies.md) |
| Quotes | FEP-044f, `_misskey_quote`, `quoteUrl`, `quoteUri`; approval, rejection, revocation | [quotes](../../federation/compatibility/quotes.md) |
| Mentions | tag, no tag, text only, delayed notification | [mentions](../../federation/compatibility/mentions.md) |
| Media | pending record, origin fallback, transformation, fetch errors, large files | [media](../../federation/compatibility/media-attachments.md) |
| Visibility | public, followers-only, direct, locked, blocks | prevent disclosure |
| Load | bursts, cold start, queue delay, retry, restart | slow first delivery |

## Test both directions

Every operation needs a sender case and a receiver case. Real asymmetries in the lab: A's reactions are understood by B but B's are not understood by A; one side enforces quote consent and the other does not; one side's `Undo` is ignored by its peer; one side shows remote media immediately and the other waits for a local copy. For interactions, run the whole lifecycle: create, receive, display, reverse, confirm the reversal, replay the original activity.

## Technical details

The wiki's own standard for outcomes is the five-way classification in [test oracles](test-oracles.md). A row that cannot be classified as verified compatible, verified incompatible, eventually convergent, harness invalid or unresolved is not finished.

## Open questions

No row of this matrix has been run by this wiki. The first useful run uses immutable images and captured per-cell requests.

## Sources

- [Run 5 report](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-19-phase7-run5.md) — what the laboratory covered and what it left unclassified
- [Federation bench problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — the failures behind each row
