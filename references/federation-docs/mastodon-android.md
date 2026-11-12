# Mastodon for Android federation behaviour

Mastodon for Android is a client application. It communicates with a user's server through the Mastodon API; the server performs ActivityPub federation. Its repository at commit `9ae49ec403719a8894903e011a9ad71c91c71c0d` does not contain a root `FEDERATION.md`. `[source]` [pinned repository](https://github.com/mastodon/mastodon-android/tree/9ae49ec403719a8894903e011a9ad71c91c71c0d), [API request implementation](https://github.com/mastodon/mastodon-android/blob/9ae49ec403719a8894903e011a9ad71c91c71c0d/mastodon/src/main/java/org/joinmastodon/android/api/MastodonAPIRequest.java).

## Technical details

The app manages account sessions and API authorization against the selected server. Its presentation of federated content is mediated by that server's API; discovery, signing, supported activities and delivery depend on the server. This does not establish compatibility with every implementation of the Mastodon API. `[source]` [account session manager](https://github.com/mastodon/mastodon-android/blob/9ae49ec403719a8894903e011a9ad71c91c71c0d/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSessionManager.java). See the [Mastodon API overview](../../clients/apis/mastodon-rest.md).

## Sources

- [Mastodon for Android at commit 9ae49ec403](https://github.com/mastodon/mastodon-android/tree/9ae49ec403719a8894903e011a9ad71c91c71c0d) — studied client source.
- [Mastodon API documentation](https://docs.joinmastodon.org/api/) — client-server API overview.
