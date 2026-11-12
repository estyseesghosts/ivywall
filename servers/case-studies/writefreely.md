# WriteFreely v0.17.3

WriteFreely is a Go publishing server for personal and multi-user blogs. Its federated identity is a blog rather than the local login account: a writer publishes Markdown and remote users can follow the blog and like posts. It provides a purpose-built client API and server-rendered pages, with a deliberately smaller social feature set than a general microblogging server. This page studies [v0.17.3](../../references/software/writefreely.md) at commit `d2485910010b1671a6e4341ab36cd199b7868e8d`; it is a source review, not a live security or interoperability test. `[source]` [routes](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/routes.go), [ActivityPub](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go).

## Architecture

The Go process serves HTML templates and JSON over HTTP and uses SQL for accounts, blog collections, posts, sessions and remote followers. It supports SQLite or MySQL-compatible storage; migrations are numbered separately from application releases. The reader, email jobs and publication functions are application code within this service rather than a separately deployed ActivityPub queue. Markdown is converted to HTML for publication, while post source and blog metadata are stored locally. `[source]` [application setup](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/app.go), [database](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/database.go), [migrations](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/migrations/migrations.go), [post rendering](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/posts.go).

Accounts and blogs are distinct: one login can own collections, while an individual collection has a federated actor and key. Remote users and follow/like relations are stored for interactions with local blogs; the inspected inbox is not a general-purpose archive of remote posts and replies. `[source]` [ActivityPub handlers](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go), [federation database](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/database_activitypub.go).

## Key code paths

### Discover and receive

WebFinger exposes a blog's actor, generally at `/api/collections/{alias}`. The actor's advertised **[inbox](../../glossary.md#inbox)** receives `POST /api/collections/{alias}/inbox`. The handler looks up the local collection, decodes the activity and dispatches supported resolver callbacks. `Follow` resolves the remote actor and prepares an `Accept`; its asynchronous path sends that acceptance before writing the follow relation, so a send failure can leave a follow unrecorded. `[source]` [routes](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/routes.go), [inbox handler](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go), [WebFinger](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/webfinger.go).

The inbox stores a `Like` on a local post and can undo a Like or follow in its supported forms. Its `Delete` callback acknowledges without importing or removing a remote post, and the resolver does not implement a general incoming `Create`/remote-thread store. A successful HTTP response alone must not be read as proof that arbitrary activity types were applied. `[source]` [ActivityPub resolver](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go), [federation database](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/database_activitypub.go).

### Publish and deliver

After a local post mutation, a goroutine constructs `Create`, `Update`, or `Delete` representations and delivers to remote followers. It groups recipients by shared inbox where provided, otherwise by individual inbox; explicitly mentioned users have an additional delivery path which can duplicate delivery. Delivery is sequential in this path, without a demonstrated persisted retry queue. A restart or transient failure can therefore lose an outbound attempt. The POST helper reads a response but does not turn its HTTP status into an error, so network I/O success alone is not evidence that the peer accepted the activity. `[source]` [`federatePost` and `makeActivityPost`](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go), [post handlers](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/posts.go).

## API coverage

The server offers a writing-oriented JSON API for accounts, collections and posts, plus browser forms and rendered pages. It is not a Mastodon-compatible REST API or the standard ActivityPub client-to-server outbox interface. A client should model blog aliases, post IDs and Markdown separately and explicitly handle unsupported social operations rather than assuming timeline, boost, poll or remote-reply endpoints. `[source]` [route registry](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/routes.go), [post handling](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/posts.go).

API mutation authorization and browser sessions have different checks; the v0.17.3 release fixed several authentication and ownership issues. The release advises revoking existing access tokens after upgrading: upgrading alone does not revoke them. `[documented]` [v0.17.3 release notes](https://github.com/writefreely/writefreely/releases/tag/v0.17.3); `[source]` [request handling](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/handle.go).

## Federation behaviour

| Feature | v0.17.3 source behavior |
| --- | --- |
| Identity and discovery | Public blog collections are ActivityPub `Person` actors discovered through WebFinger. |
| Publication | Outgoing post activities carry a `Note` or `Article`; Markdown is rendered to HTML, with tags, mentions and linked image attachments. |
| Update and deletion | Local changes emit `Update` and `Delete`; the separate mention-delivery path can emit `Create` for an update and merits a regression test. |
| Follow | Incoming Follow can cause an `Accept` and persisted remote follower relation. |
| Likes | Incoming Like and Undo Like change a local post's stored remote-like relation. |
| Remote conversations | No general incoming Create or remote-reply graph is established by the inspected resolver; a reply may exist elsewhere without appearing as a native WriteFreely thread. |

`[source]` [ActivityPub implementation](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go), [federation persistence](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/database_activitypub.go), [posts](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/posts.go). The table describes local code paths, not observed behavior of a named peer.

Private and password-protected blogs are excluded from the publication federation path. Blog visibility settings are not interchangeable with Mastodon's post audience model; an unlisted blog should not be assumed private or non-federated. The v0.17.3 release fixed a private outbox disclosure, illustrating why web, API and ActivityPub representations all need separate permission checks. `[source]` [federation path](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go); `[documented]` [release notes](https://github.com/writefreely/writefreely/releases/tag/v0.17.3).

## Resource usage

No measured memory, throughput, database size or CPU figures are available here. Shared-inbox grouping reduces repeated destination requests but does not make sequential fan-out durable. Benchmark with actual follower counts, distinct inbox counts and remote outage patterns before applying a capacity estimate.

## Strengths, known bugs and tradeoffs

The relatively compact publishing model and SQL-backed deployment can suit a small writing community; it does not supply the distributed delivery guarantees or social feature set of a larger server. The outgoing signing path creates an RSA-SHA256 `Signature` and SHA-256 digest over the request; its existence does not establish incoming authentication. `[source]` [ActivityPub implementation](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go).

The inspected inbox path does not visibly verify inbound HTTP signatures or bind a verified signer to the activity's claimed actor. This is a source-observed assurance gap, not a claim that an exploit was tested or that an external proxy could not add controls. v0.17.3 also hardened remote network fetching against server-side request forgery, a distinct boundary from authenticating activity authors. `[source]` [inbox](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go), [network request handling](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/webfinger.go); `[documented]` [v0.17.3 release](https://github.com/writefreely/writefreely/releases/tag/v0.17.3).

## Technical details

Outgoing signatures cover `(request-target)`, `date`, `host` and `digest`. They do not provide durable delivery or imply that an inbox applies the activity. Inspect the destination response and final stored state when testing federation. `[source]` [`makeActivityPost`](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go).

A complete restore requires a consistent database snapshot, `config.ini`, the `keys/` directory, and any locally maintained assets or templates. Versioned migrations run sequentially; take and test a backup before upgrading. Federation identity and session access depend on preserving keys. `[source]` [migrations](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/migrations/migrations.go), [keys](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/keys.go); `[documented]` [release notes](https://github.com/writefreely/writefreely/releases/tag/v0.17.3).

Open questions requiring isolated tests include forged and replayed inbox activities, destination 4xx/5xx handling, `Update` sent to mentions, duplicate delivery, private outbox access, and migration interruption. No peer compatibility matrix or exploit result is claimed here.

## Sources

- [WriteFreely v0.17.3 source tree](https://github.com/writefreely/writefreely/tree/d2485910010b1671a6e4341ab36cd199b7868e8d) — pinned implementation.
- [ActivityPub handling and delivery](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/activitypub.go) — incoming resolver, outbound signing and fan-out.
- [Routes](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/routes.go) and [federation database](https://github.com/writefreely/writefreely/blob/d2485910010b1671a6e4341ab36cd199b7868e8d/database_activitypub.go) — endpoint and relationship implementation.
- [v0.17.3 release notes](https://github.com/writefreely/writefreely/releases/tag/v0.17.3) — version-specific fixes and upgrade instructions.
