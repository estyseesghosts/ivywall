# Security invariants for federation code

A checklist of what must stay true in a server that accepts remote identities, content and URLs. Each row names the invariant, one plausible failure that has actually been seen or read in code, and a negative test. The [minimal actor](../guides/minimal-actor.md) implements and tests most of them. This page states implementation policy; where a row goes beyond what ActivityPub requires, it says so.

## Invariants

| Invariant | Failure seen | Negative test |
| --------- | ------------ | ------------- |
| A valid signature does not authorize an activity. The signing actor must be the activity's `actor`, and must own what it changes | A correct `Accept` check compared the wrong field of the embedded `Follow` (its actor, not its object), a 403 Mastodon would not retry `[reported]` [Birchtree phase 6](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md) | Valid key, different claimed actor: refused (minimal actor test, 401) |
| The activity `id` and object ids are on the actor's origin, or authority is established another way | Mastodon accepted a boost whose id was on another host; stricter servers did not count it ([wrong-domain ids](../federation/failure-modes/wrong-domain-activity-ids.md)). A hostname match is common policy, not a protocol rule | Activity id on another host: refused |
| Body integrity is part of the signature | Mbin only logs a digest mismatch; a signature that does not cover `digest` leaves the body unprotected ([HTTP signatures](../fundamentals/http-signatures.md)) | Body changed after signing, and `digest` not signed: both refused (signing vectors) |
| Stale or replayed requests are rejected | Mbin does not check `Date` (a TODO) | `Date` outside the skew: refused |
| Key refresh is bounded and cannot substitute a key | A cached key survived 24 hours after rotation; the fix was one forced refetch with a cooldown `[reported]`. The refetched key must still belong to the signing actor | Rotated key recovers once; a key owned by another actor never verifies |
| Every outbound fetch is checked: scheme, resolved address, each redirect, size and time | Private-address and redirect SSRF; DNS work must stay bounded when lookups stall ([SSRF](ssrf.md)) | Redirect to a loopback address: refused; stalled resolver does not grow without bound |
| Private audience is rechecked at every path that serves it | Lemmy fetches of a private community need a signed request from an instance with a follower; an unsigned `Create` in Mobilizon is refetched from its claimed URL, whose origin check is unread ([Lemmy](../references/federation-docs/lemmy.md), [Mobilizon](../references/federation-docs/mobilizon.md)) | Unauthorized fetch, API read and stream subscription each refused |
| Duplicates and reordering cannot corrupt state. Dedup records only what was applied | An ignored `Undo` recorded as seen blocked the real one; `Delete` before `Create` resurrected a post ([Undo](../federation/failure-modes/undo-ignored-or-deduplicated.md), [delete](../federation/failure-modes/delete-before-create.md)) | Same activity twice; Undo of an unknown id then the real one; Delete then Create |
| Received HTML and media are validated before display | Mastodon sanitises incoming HTML to a fixed element list `[documented]` ([ActivityPub docs](https://docs.joinmastodon.org/spec/activitypub/)) | Script and event-handler attributes stripped |
| A crash before commit leaves no partial state | State is saved before an `Accept` is sent; WriteFreely sends first and can lose the follower | Kill between receipt and commit, then redeliver |

## Who may do what

The questions are different: which identity the transport authenticated, whether that identity owns the object, and whether the receiver must fetch from the origin.

| Operation | Authority | Evidence |
| --------- | --------- | -------- |
| Undo an activity | only its original actor | `[spec]` ActivityPub §6.10 |
| Edit a post | the post's author, same origin | enforced by Pixelfed (owner only), NodeBB (`attributedTo` origin) and Mastodon (ownership) `[source]` |
| Delete a post | its author; for an object not yet seen, only when the actor and object share a host | minimal actor rule; Pinetree's tombstone rule `[reported]` |
| Forward an activity to others | any server may forward; the receiver should not trust the forwarder's copy and may refetch from the origin | Mbin refetches from the origin `[source]`; ActivityPub allows inbox forwarding |
| Moderate in a group | the community's home instance or the moderated object's origin is trusted; otherwise a community moderator or admin who is not banned | Lemmy `verify_mod_action` `[source]` |
| Accept a follow | the account being followed | Birchtree fix above |

## Limits

Inbox body, nested JSON, fetch size, redirects, concurrency and queue growth need limits, presented as implementation policy: Misskey and Catodon cap inbox bodies at 64 KiB, Mastodon answers 413 to an oversized request, Pixelfed caps fetched responses at 2 MiB. None is an ActivityPub requirement.

## Sources

- [ActivityPub 2018](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — security considerations and §6.10
- [Birchtree phase 6 verification](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md) — authorization and dedup findings
- [Birchtree `fix_push_ssrf.rs`](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/tests/fix_push_ssrf.rs) and [Pinetree `dns_bounded_p1.rs`](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/tests/dns_bounded_p1.rs) — network-safety tests worth reusing
