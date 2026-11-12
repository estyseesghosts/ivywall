# Guide: a minimal ActivityPub server

A working single-user server in about 270 lines of Python, with no packages beyond the standard library and the `openssl` command. It publishes one actor, verifies signed deliveries, answers a `Follow`, delivers notes to followers and keeps its state correct under duplicates, reordering and undo. It has been run against itself (two instances over signed HTTP, 16 checks), not against Mastodon or any other implementation; the last milestone is still open. Code: [`server.py`](minimal-actor/server.py) and [`selftest.py`](minimal-actor/selftest.py).

## Run it

```sh
python3 guides/minimal-actor/selftest.py        # two servers on loopback, prints PASS/FAIL per check
python3 guides/minimal-actor/server.py --user alice --host example.org --port 8080 \
    --data ./data --token SECRET                # behind a TLS proxy; --scheme http --allow-private for tests only
```

Admin calls need `X-Admin-Token`: `POST /admin/follow {"handle":"bob@other.example"}` and `POST /admin/publish {"content":"hello"}`.

## Milestones

| # | Milestone | Where in `server.py` | Status |
| - | --------- | -------------------- | ------ |
| 1 | WebFinger and actor document with inbox, outbox and public key | `Actor.webfinger`, `Actor.actor_doc`, `make_key` | self-tested |
| 2 | Persistent signing key; signed outgoing requests; safe remote fetch | `sign_headers`, `Actor.request`, `Actor.check_url` | self-tested |
| 3 | Inbox that verifies signed POSTs | `Actor.verify`, `Actor.handle` | self-tested (modified body, no signature, stale date, wrong actor, wrong host) |
| 4 | Receive `Follow`, persist, answer `Accept` | `on_follow`, `on_accept` | self-tested |
| 5 | Publish a `Note` in `Create`, one POST per follower inbox, bounded retries | `Actor.publish`, `Actor.deliver` | self-tested |
| 6 | Receive `Like` and `Announce` of your notes; replies are stored as remote notes | `record_reaction`, `on_create` | `Like` self-tested |
| 7 | `Undo` and `Delete` without resurrecting removed state | `on_undo`, `on_delete`, tombstones | self-tested |
| 8 | Pass a defined suite against a pinned Mastodon release | none | **not done** |

## Design decisions

- **Verify, then authorise.** `verify` proves who signed. `handle` then requires the activity's `actor` to equal that signer and the activity `id` to be on the actor's host (a common policy, not a protocol rule). Objects are changed only by their owner. See [security invariants](../security/invariants.md).
- **Commit before you acknowledge or answer.** State is written (atomically, `save`) before an `Accept` goes out and before `202`. A crash leaves the sender to retry.
- **Record only what changed state.** An activity id enters `applied` only when its handler returned `applied`. An `Undo` of an id never applied is ignored and not recorded, so a redelivery works ([Undo has no effect](../federation/failure-modes/undo-ignored-or-deduplicated.md)).
- **Tombstones.** A `Delete` for an unseen object by an actor on the object's host is remembered, and a late `Create` is refused ([deleted post reappears](../federation/failure-modes/delete-before-create.md)).
- **Bounded fetch.** Scheme and resolved address are checked, redirects are not followed, size and time are limited, and a key is refetched at most once a minute ([SSRF](../security/ssrf.md)).
- **`202` means received.** The result of processing is in state, not in the status code.

## What it leaves out, deliberately

Timelines, OAuth, media, polls, quotes, edits of your own notes, blocks, migration, RFC 9421 signatures, shared inboxes, a job queue (delivery uses threads) and any user interface. Real interoperability also needs: an HTTPS name on the standard port (Mastodon resolves WebFinger over HTTPS only and needs each actor to map to an `acct:` handle, see its [federation document](../references/federation-docs/mastodon.md)), a signature scheme the peer accepts ([HTTP signatures](../fundamentals/http-signatures.md)), and a queue that survives restarts.

## Next: milestone 8

Run it against a pinned Mastodon in the [quick lab](../testing/harness/local-lab.md). Birchtree's 14-step follow run is the model for acceptance: discovery, inbound and outbound follow with `Accept`, `Undo`, a locked account, and `Reject`, with state read on both sides. Record the result in the [result format](../testing/fixtures/result-schema.md) and do not call it ActivityPub compliance: it covers the follow family.

## Sources

- [ActivityPub 2018](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — inbox, outbox, delivery and `Follow`/`Accept`
- [HTTP signatures](../fundamentals/http-signatures.md) — the scheme the example signs and verifies
- [Birchtree phase 6 verification](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/docs/logs/2026-10-17-phase-6-verification.md) — the follow-family acceptance run and the bugs it found
