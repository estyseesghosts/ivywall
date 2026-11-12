# Streaming and recovery in a client

A stream tells a client what changed while it was connected. It is not a record of everything that happened, so a client that only listens will miss posts, deletions and notification changes whenever the connection drops. This page gives the two servers' stream mechanics and a recovery method that works for both.

## Stream mechanics

| | Mastodon | Misskey |
| - | -------- | ------- |
| Transport | long-lived HTTP server-sent events, or WebSocket | WebSocket at `wss://{host}/streaming?i={token}` |
| Subscribing | the stream or timeline is chosen in the request (home, public, hashtag, notifications) | opening the socket receives nothing; send `{"type":"connect","body":{"channel":"…","id":"…"}}` for each channel |
| Keep-alive | heartbeat comment lines starting with `:` (for example `:thump`), which parsers ignore | not read |
| Token | `Authorization: Bearer`; a WebSocket may also use `Sec-WebSocket-Protocol`; an `access_token` query parameter is discouraged because it reaches access logs | `i` query parameter; omitting it gives a logged-out stream with less information |

`[documented]` [Mastodon streaming](https://docs.joinmastodon.org/methods/streaming/), [Misskey streaming API](https://misskey-hub.net/en/docs/for-developers/api/streaming/). Birchtree's contract tests exercise SSE and WebSocket clients, revocation closing both, and a WebSocket closed when pings go unanswered `[source]` [phase5_streaming.rs](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/tests/phase5_streaming.rs); they test a server, not a real client.

## Recovery method

A design recommendation, not a measured result:

1. Keep a local cache keyed by the server's ids, with the newest id seen per timeline.
2. Apply a live event only if its id is not already cached; a duplicate must be a no-op.
3. On disconnect, reconnect with backoff, then fetch the missed range over REST from the newest cached id, following every pagination link, and merge by id.
4. Treat a deletion or edit event as a change to a cached item, including one that arrives after the item was shown.
5. Replace temporary local ids (an optimistic post) with the server's id when the create returns, and drop the temporary entry if the stream delivers the real one first.
6. If the gap is larger than one page, show that the timeline has a hole; only the server can fill history it never received.
7. Deduplicate notifications by id across the stream and the REST list.

## Two ids for one post

A server-local note id and the ActivityPub URI of the same post are different. A reply or notification can name a post the server has not fetched; keep the URI as the stable reference and resolve it when the post arrives. See [identity](../../fundamentals/identity.md) and the [Mastodon REST API](../apis/mastodon-rest.md).

## Open questions

Reconnect and cursor behaviour of real clients (Tusky, Phanpy and others) has not been read; this method is untested against them.

## Sources

- [Mastodon streaming methods](https://docs.joinmastodon.org/methods/streaming/) — SSE, WebSocket, heartbeats, authentication
- [Misskey streaming API](https://misskey-hub.net/en/docs/for-developers/api/streaming/) — connection and channels
- [Birchtree streaming contract tests](https://github.com/estyseesghosts/birchtree/blob/f09ec359af00233530a230b9242f8321578e6e37/tests/phase5_streaming.rs) — server-side behaviour under revocation and dead peers
