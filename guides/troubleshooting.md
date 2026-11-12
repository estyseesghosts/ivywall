# Federation troubleshooting

Work from the symptom to the stage where federation broke, then decide whether the sender, the receiver, the network or your test caused it. An HTTP success is never the end of the check: a `202` means received, so confirm the stored result as well. Each recipe lists the command, what a healthy answer looks like, the usual causes and a pointer to the page that explains the cause.

## First, rule out your test

Before blaming software, check the lab: the running binaries are the ones you think (read the build from the process, not the file), hostnames resolve from inside every container, certificates are trusted by every peer, ports are free, and workers are running. A failed check is a software finding only after those pass. See [test oracles](../testing/interoperability/test-oracles.md) and the [local lab](../testing/harness/local-lab.md).

## By stage

### 1. Discovery: the remote account cannot be found

```sh
curl -sS -i -H 'Accept: application/jrd+json' 'https://HOST/.well-known/webfinger?resource=acct:USER@HOST'
curl -sS -i -H 'Accept: application/activity+json' 'ACTOR_URL'
```

Healthy: `200` with a link whose `rel` is `self` and type `application/activity+json`; the actor document's `id` equals the URL you fetched, and it has `inbox` and `publicKey.id`, `owner`, `publicKeyPem`. Causes: WebFinger over plain HTTP or a non-standard port (WebFinger is HTTPS-only; one studied server dropped the port), a proxy that serves HTML to the `Accept` header, an actor `id` on another host than its URL, a resolver that ignores `/etc/hosts`. See [WebFinger](../fundamentals/webfinger.md).

### 2. Fetching: `401`/`403` on a GET

The remote requires a signed fetch (secure mode / authorized fetch). Sign the GET as a local actor or the instance actor. Healthy: the same URL returns `200` once signed. See [HTTP signatures](../fundamentals/http-signatures.md).

### 3. Authentication: the inbox returns `401`

Check the request you sent, in this order:

1. **Digest.** `printf '%s' "$BODY" | openssl dgst -sha256 -binary | openssl base64` must equal the `Digest` value after `SHA-256=` (or the `Content-Digest` value for RFC 9421). Hash the bytes you send, not a re-serialised copy.
2. **Signed headers.** `(request-target)`, `host`, `date` and `digest` must all be in the `headers` list, and the receiver must see the same `Host` your proxy rewrote to; one studied server logs a hint to forward the `Host` header.
3. **Date.** Within the receiver's skew (one studied server allows one day, another one hour, another none).
4. **Key.** `keyId` resolves to an actor whose `publicKey.id` and `owner` match; the key is current (a receiver may cache an old one for hours); the PEM parses.
5. **Actor.** The activity's `actor` equals the key's owner, and the activity `id` is on that host.

Reproduce offline with the [signing vectors](../testing/fixtures/signing/vectors.json): `python3 tools/signing_vectors.py verify`. If your signature verifies there but the peer rejects it, the cause is the peer's scheme or policy, not your arithmetic. Sender versus receiver: send the same request to a server you control, such as the [minimal actor](minimal-actor.md), and see which check fails.

### 4. Processing: the inbox returns `202` but nothing appears

`202` means queued. Find the queue and the log line that rejected it.

| Server | Where to look |
| ------ | ------------- |
| Mastodon | `ingress` queue, `ActivityPub::ProcessingWorker` |
| Misskey, Catodon | inbox queue worker (`InboxProcessorService`); verification runs after the `202` |
| Pixelfed | `InboxPipeline` jobs |
| Mbin | `ActivityHandler` message handler |
| Mobilizon | `Federator` incoming document queue |

Common causes: signature or key checked later in the worker; object failed validation; sender not authorised for the object (a `Delete` or `Update` by someone who does not own it); the activity was a duplicate and ignored. See [first-contact races](../federation/failure-modes/first-contact-races.md) and [wrong-domain ids](../federation/failure-modes/wrong-domain-activity-ids.md).

### 5. A follow succeeds but no posts arrive

Verify from both accounts: the follow is `accepted`, not pending (a locked account keeps a pending request and unlocking does not approve it). Check that the followee persisted the follower before or despite sending `Accept` (one server sends `Accept` first and loses the follower if sending fails), that the post reached the follower's inbox, and that the delivery job did not exhaust its retries. See [life of a follow](../federation/activities/life-of-a-follow.md) and [delivery queues](../federation/delivery/queues-and-retries.md).

### 6. Replies, media, deletion, reversal

| Symptom | First checks | Page |
| ------- | ------------ | ---- |
| Replies missing | parent fetch needs a signed GET; reply audience; backfill | [replies missing](../federation/failure-modes/missing-replies.md) |
| Media exists but does not render | attachment record versus fetched bytes; `url` versus `remote_url`; processing queue | [media](../federation/failure-modes/media-not-verifying.md), [attachments](../federation/compatibility/media-attachments.md) |
| Deleted post reappears | `Delete` before `Create`; tombstone; duplicate delivery | [deleted post reappears](../federation/failure-modes/delete-before-create.md) |
| Unboost, unlike or unfollow has no effect | `Undo` names the earlier activity's real id; dedup recorded an ignored `Undo` | [Undo has no effect](../federation/failure-modes/undo-ignored-or-deduplicated.md) |
| Edit does not show | receiver skips `Update` of posts | [contracts](../federation/compatibility/activity-contracts.md) |
| Mention without notification | tag versus text; notification index | [mentions](../federation/compatibility/mentions.md) |

## Evidence to collect before reporting

Both software versions (image digest or commit), the exact request as sent (headers and body bytes), the response and its time, the receiver's queue and log lines, the stored state read from the receiver (not only a timeline), and the result of the lab checks above. Redact tokens and keys. Record whether the evidence is captured or inferred, using the [result format](../testing/fixtures/result-schema.md).

## Sources

- [Federation bench problem log](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md) — the failures behind these recipes (`[reported]`)
- [RFC 7033: WebFinger](https://www.rfc-editor.org/rfc/rfc7033) — discovery requirements
- [Community-written federation documents](../references/federation-docs/index.md) — per-server queue and signature behaviour
