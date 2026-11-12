# How remote state spreads and diverges

A public post is not stored everywhere. Each server holds only what reached it, in the order it arrived, with authority it could check. This page lists the ways content becomes known to another server and the rules that keep a server's copy of remote objects correct when delivery is late, repeated or out of order. It is the model behind the [failure modes](index.md); the order-dependent cases there are examples of it.

## Four different questions

For any post, ask separately: did the sender publish it, does the receiving server know it, can a given user see it, and will their client show it? Each can be false while the others are true. A stored object is not a visible one, and a visible one is not necessarily in a timeline.

## How a server comes to know an object

| Path | Who starts it | State needed first | If missed |
| ---- | ------------- | ------------------ | --------- |
| Direct delivery to an addressed actor's inbox | sender | recipient is addressed in `to`, `cc`, `bto`, `bcc` or `audience` | lost unless retried |
| Followers' delivery, collapsed to one POST per shared inbox | sender | an accepted follow | follower never sees it |
| Mention or reply | sender | the target is addressed | target may not see it |
| Boost | booster's server | followers of the booster | original author's server may not know the booster |
| Inbox forwarding | recipient server | the activity addressed a collection the recipient owns | ghost replies (replies seen without their parent) |
| Relay subscription | relay | subscription to the relay | none, unless subscribed |
| Fetch by URL or search | receiving server | a URL and permission to fetch | not found, or `401` if fetch is signed-only |
| Thread backfill | receiving server | a known post and its context or replies collection | an incomplete thread |

`[spec]` ActivityPub 2018 §7.1 (delivery), §7.1.2 (forwarding from inbox, to avoid ghost replies), §7.1.3 (shared inbox delivery); relays are described by FEP-ae0c and backfilling by FEP-f228 (see the [FEP registry](../references/feps/registry.md)). No path is guaranteed, and no server has a complete view.

## Rules for a remote object's lifecycle

A server's copy moves through: unknown, known (a `Create` applied), changed (`Update`), and deleted. A delete can arrive for an object never seen, so "deleted" needs a record independent of the object.

1. **Two keys, two jobs.** Deduplicate activities by activity id, and objects by canonical object URI. One does not stand in for the other ([duplicate objects](failure-modes/duplicate-remote-objects.md)).
2. **Record an activity as processed only after it changed state.** An ignored or unresolved `Undo` must be retried later ([Undo has no effect](failure-modes/undo-ignored-or-deduplicated.md)).
3. **Keep a tombstone for deleted URIs, including unseen ones**, written only when the deleting actor owns the object, and refuse a later `Create` for it ([deleted post reappears](failure-modes/delete-before-create.md)).
4. **Authority travels with the claim.** Accept a change only from the object's owner; a forwarded copy proves nothing about who authored it ([invariants](../security/invariants.md)).
5. **Commit state before acknowledging or answering.**

Orderings and what a correct receiver does. The [minimal actor](../guides/minimal-actor.md) self-test runs the first, second and fourth rows and the first half of the third:

| Arrives | Then | Correct result |
| ------- | ---- | -------------- |
| `Delete(P)` | `Create(P)` | `P` stays absent |
| `Create(P)` | `Create(P)` again | one copy |
| `Undo` of an id never applied | later, the original activity and the `Undo` again | the first `Undo` is ignored and not recorded, so the redelivered one applies |
| `Delete(P)` by a non-owner | | ignored; no tombstone |
| `Update(P)` | `Create(P)` | undecided: Catodon creates the post from an `Update`; Misskey skips post updates ([contracts](compatibility/activity-contracts.md)) |

## Recovery

A sender cannot always know which servers hold an object, so missed deletes and edits are not guaranteed to reach everyone. Receivers narrow the gap by re-checking known objects when accessed again (FEP-044f asks this of quote approvals) and, for followers, by comparing follower lists (FEP-8fcf, implemented by Mastodon and Pixelfed). Neither makes the network consistent; both reduce divergence.

> Unknown: how Mastodon, Akkoma, GoToSocial and Lemmy order the cases in the table. A matching experiment against pinned releases is the next step ([local lab](../testing/harness/local-lab.md)).

## Sources

- [ActivityPub 2018 §7](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery) — delivery, forwarding and shared inboxes
- [FEP registry](../references/feps/registry.md) — ae0c, f228, 8fcf, 044f
- [Minimal actor self-test](../guides/minimal-actor/selftest.py) — the ordering cases above, run against the example server
