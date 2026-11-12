# ActivityPub server-to-server

The server-to-server profile of [ActivityPub](../glossary.md#activitypub) lets one server send social activities to accounts hosted elsewhere. The sending server discovers each recipient's delivery endpoint, called an **[inbox](../glossary.md#inbox)**, and POSTs the activity there. The receiving server authenticates and authorizes what it receives, applies supported effects and may distribute it to local users. ActivityPub specifies the delivery and data model but leaves authentication mechanisms and many operational details to implementations. `[spec]` ActivityPub 2018, §§2.1, 7, B.1–B.2.

## What the specification requires

### Representations and discovery

A federated actor advertises its `inbox` and `outbox` as `OrderedCollection`s in its actor representation. For dereferencing objects, servers MUST serve ActivityStreams JSON-LD for `Accept: application/ld+json; profile="https://www.w3.org/ns/activitystreams"` and SHOULD also serve it for `application/activity+json`. A server-to-server POST MUST use the former profile as Content-Type; GET requests MUST use it in Accept. Servers SHOULD interpret `application/activity+json` as equivalent in server-to-server interactions. `[spec]` §§3.2, 5.1–5.2, 7.

An activity ordinarily has a globally unique `id`; an intentionally transient activity may omit one. The specification says identifiers MUST be provided in server-to-server communication unless transient (§3.1), and §7 says an activity sent over the network SHOULD have an ID unless transient. Inboxes MUST deduplicate returned activities by comparing their IDs. `[spec]` §§3.1, 5.2, 7.

### Resolve recipients and deliver

The sender determines targets from `to`, `bto`, `cc`, `bcc`, and `audience`, looks up each actor's `inbox`, then POSTs the activity there. For collection recipients it MUST dereference the collection, discover member inboxes, and limit nested collection expansion; it MUST deduplicate final recipients and exclude the activity's own actor. The special Public URI (`https://www.w3.org/ns/activitystreams#Public`) signals public accessibility; it MUST NOT itself receive delivery. `[spec]` §§5.6, 7.1.

For a server that supports both profiles, §7.1.1 requires delivery to individuals or actor-owned collections named in those fields. The server MUST use blind recipient fields for targeting but remove `bto` and `bcc` before delivery. `[spec]` §§6, 7.1.1.

Delivery to a third-party server SHOULD be asynchronous, and network failures SHOULD be retried. The specification does not set a universal retry schedule or guarantee delivery, ordering, or exactly-once side effects. Implementations SHOULD take care not to overload peers, for example with exponential backoff. `[spec]` §§7.1, B.7; the absence of a universal guarantee is an inference from those provisions.

### Shared inbox and forwarding

A **shared inbox** is an optional endpoint advertised by actors for efficient delivery to multiple recipients on one server. For delivery to the originating actor's followers, a sender MAY replace individual deliveries with a shared inbox when the recipients share it. For Public-addressed objects it MAY send to known shared inboxes, but MUST still deliver to otherwise-addressed actors and collections not covered by this mechanism. A shared inbox is not a blanket replacement for every addressed delivery. `[spec]` §7.1.3.

Inbox forwarding addresses replies that the original server could not deliver to a private collection. A receiving server MUST forward to `to`, `cc`, or `audience` only when **all** three conditions hold: the activity is new to that server; one of those fields names a collection it owns; and `inReplyTo`, `object`, `target`, or `tag` references an object it owns. It SHOULD bound recursive checking. It MUST use only the original addressing fields, not discover additional recipients while traversing references, and MAY filter targets under local rules. `[spec]` §7.1.2.

### Incoming effects and authorization

| Incoming activity | Specified effect |
| --- | --- |
| `Create` | Appears in the recipient's inbox; the server will likely store the activity and object. `[spec]` §7.2 |
| `Update` | The receiver SHOULD replace its copy with the complete supplied object, after checking authorization. It MUST take care the update is authorized. This differs from the partial [client update](activitypub-c2s.md). `[spec]` §7.3 |
| `Delete` | Assuming ownership, the receiver SHOULD remove its copy and MAY retain a `Tombstone`. The protocol cannot force a remote copy to be deleted. `[spec]` §7.4 |
| `Follow` | The recipient SHOULD send an `Accept` or `Reject`, immediately or after review; it MAY omit an explicit rejection. A rejected request MUST NOT add a follower. `[spec]` §7.5 |
| `Accept` / `Reject` of a `Follow` | The requester's server SHOULD add the accepted actor to its following collection; it MUST NOT do so on rejection. `[spec]` §§7.6–7.7 |
| `Add` / `Remove` | The receiver SHOULD modify a locally owned target collection, subject to authorization and local rules. `[spec]` §§7.8–7.9 |
| `Like` / `Announce` | If present, the relevant `likes` / `shares` collection SHOULD receive the activity. `[spec]` §§7.10–7.11 |
| `Undo` | The actor of the Undo MUST be the actor of the activity being undone; reverse effects where possible. `[spec]` §7.12 |

## What implementations do

The recommendation does not mandate an authentication mechanism. HTTP request signatures are a separate interoperability convention; see [HTTP signatures and authentication](http-signatures.md) for its distinctions and implementation coverage. Don't infer that a signature on a transport request by itself proves every embedded object is authorized: forwarded activities can have a different origin and need an appropriate verification policy. `[spec]` B.1–B.2.

A 2xx response can indicate acceptance of an HTTP delivery without proving every recipient displayed the object or that later asynchronous processing succeeded. The exact acknowledgment, retries, policy filtering, request limits and supported vocabulary are implementation-specific and must be verified for the deployment; no universal values are asserted here. `[spec]` §§7.1–7.2, B.7.

## Technical details

The following is a handwritten, unexecuted example based on §§3.2, 5.6 and 7. The example IDs and hosts are fictional. It shows one direct inbox delivery, not an authentication recipe; peers may require an additional signature and digest.

```http
GET /users/bob HTTP/1.1
Host: bob.example
Accept: application/ld+json; profile="https://www.w3.org/ns/activitystreams"
```

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://bob.example/users/bob",
  "type": "Person",
  "inbox": "https://bob.example/users/bob/inbox",
  "outbox": "https://bob.example/users/bob/outbox"
}
```

```http
POST /users/bob/inbox HTTP/1.1
Host: bob.example
Content-Type: application/ld+json; profile="https://www.w3.org/ns/activitystreams"

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://alice.example/activities/123",
  "type": "Create",
  "actor": "https://alice.example/users/alice",
  "to": ["https://bob.example/users/bob"],
  "object": {
    "id": "https://alice.example/notes/456",
    "type": "Note",
    "attributedTo": "https://alice.example/users/alice",
    "to": ["https://bob.example/users/bob"],
    "content": "Hello, Bob"
  }
}
```

The `Create` ID identifies the activity; the Note ID identifies the content. A retry should retain the original activity ID so the receiver can recognize a duplicate; do not mistake that for a protocol guarantee of exactly-once processing. `[spec]` §§3.1, 5.2, 7.1.

## Pitfalls

- **Posting to Public.** Public is an audience marker, not a delivery endpoint. Resolve real actors and collections. `[spec]` §§5.6, 7.1.
- **Leaking blind addresses.** Resolve `bto` and `bcc` for delivery and remove them from the outgoing representation; do not expose them in displays. `[spec]` §6, B.11.
- **Accepting claims without checking authority.** Validate the sender, the activity, and the authority to modify the object. A forwarded request can have a transport signer distinct from the activity actor. `[spec]` §§7.3, B.2.
- **Treating URLs as safe.** Remote actor, object, collection, key and redirect URLs are untrusted. Restrict schemes and destinations, reject internal-network targets in production, bound recursion and response size, and sanitize rendered markup. `[spec]` B.3–B.5, B.9–B.10; destination and redirect validation are engineering recommendations.
- **Assuming a complete global view.** Collections can be access-controlled; delivery can fail and be retried, and local policy can filter forwarding. Do not use one server's view as proof that no other reply exists. `[spec]` §§5.2–5.4, 7.1–7.1.2.

## Sources

- [ActivityPub W3C Recommendation, 23 January 2018](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — actor and collection representation, server delivery and side effects, and security considerations; particularly §§3–5, 7 and B.
- [ActivityStreams 2.0 Core](https://www.w3.org/TR/activitystreams-core/) — data model, collections and JSON-LD representation.
