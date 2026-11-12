# ActivityPub client-to-server

ActivityPub defines a way for a client to ask a user's server to publish and change social data. The client finds the posting endpoint in the account-like **[actor](../glossary.md#actor)**, sends a signed-in request, and the server assigns identifiers, applies the operation, and may deliver it to other servers. This client-to-server protocol is a separate conformance profile from [server-to-server federation](activitypub-s2s.md): a server can support one without the other. `[spec]` ActivityPub 2018, §§2.1, 4–7.

## What the specification requires

### Discover, authenticate, submit

The client MUST discover the actor's `outbox` property and POST to that URL using `Content-Type: application/ld+json; profile="https://www.w3.org/ns/activitystreams"`. The server MAY treat `application/activity+json` as equivalent for client requests. The POST MUST authenticate as the user who owns that outbox, but ActivityPub does not prescribe a single authentication scheme. The body is one ActivityStreams activity or one non-activity object, possibly with embedded objects. `[spec]` §§5.1, 6, B.1.

The **outbox** is the actor's published-activity collection, an `OrderedCollection`, filtered according to the reader's permissions. An actor's **[inbox](../glossary.md#inbox)** is a separate collection of received activities; its contents are likewise subject to access controls. Ordered collections are presented consistently in reverse chronological order. `[spec]` §§5, 5.1–5.2.

On accepted submission, the server MUST ignore a client-supplied activity `id`, allocate a new activity ID, and return `201 Created`; unless the activity is transient, it MUST include its ID in `Location`. It MUST add the activity to the outbox, though its visible appearance can be delayed or temporary. An endpoint without client-to-server support SHOULD respond to a submission with `405 Method Not Allowed`. `[spec]` §6.

A bare object submitted to the outbox MUST be wrapped in `Create`; for non-transient objects both wrapper and object receive IDs. The server MUST copy the object's `to`, `bto`, `cc`, `bcc` and `audience` fields to the wrapper. The client is responsible for addressing: delivery considers those fields, not mentions alone. `bto` and `bcc` determine recipients but MUST be stripped before delivery. `[spec]` §§6, 6.1, 6.2.1.

### Activity side effects

When delivering to another server, `Create`, `Update`, `Delete`, `Follow`, `Add`, `Remove`, `Like`, `Block`, and `Undo` activities MUST have an `object`; `Add` and `Remove` also require `target`. These are server-to-server delivery requirements, rather than a blanket rule for every client submission. `[spec]` §7.

| Activity | Client-to-server effect |
| --- | --- |
| `Create` | Creates its embedded object; the server SHOULD copy the actor to `attributedTo` and reconcile addressing between wrapper and object on initial distribution. `[spec]` §6.2 |
| `Update` | With permission, MUST update the object. This is a **partial** update of top-level fields: supplied values replace existing ones; `null` removes a field. Federation carries the resulting whole object, not the patch. `[spec]` §6.3 |
| `Delete` | The server MAY replace the object with a `Tombstone`; later retrieval SHOULD return 410 with a tombstone or 404 otherwise. `[spec]` §6.4 |
| `Follow` | Add to the actor's following collection SHOULD happen only after a corresponding `Accept`. `[spec]` §6.5 |
| `Add`, `Remove` | SHOULD change the specified collection unless the server does not own it or another rule disallows the change. `[spec]` §§6.6–6.7 |
| `Like` | The server SHOULD add the object to the actor's `liked` collection. `[spec]` §6.8 |
| `Block` | The server SHOULD prevent the blocked actor interacting with the blocker's objects and SHOULD NOT deliver the Block to that actor. `[spec]` §6.9 |
| `Undo` | The undo and original activity MUST have the same actor; effects should be reversed where possible. Use `Delete` for `Create` and `Remove` for `Add`. `[spec]` §6.10 |

Federating servers MUST deliver posted activities according to the recipient rules; media upload mechanisms are outside the 2018 specification. `[spec]` §§6.11–6.12.

## What implementations do

This is a standard contract, not a claim that a particular deployment enables it. A server can expose federated ActivityPub while offering clients a different API. Check the [Mastodon REST API](../clients/apis/mastodon-rest.md), the [client API index](../clients/index.md), and each server's version-pinned documentation before relying on outbox POST. The authentication scheme, media upload, supported activities and error details need implementation-specific verification. `[spec]` §§2.1, 6.12, B.1.

## Technical details

This example is handwritten from ActivityPub §§6 and 6.2.1; it has not been run. The bearer credential is illustrative, not a mandated authentication scheme. The outbox URL is obtained from the actor representation, not constructed from the username.

```http
POST /users/alice/outbox HTTP/1.1
Host: alice.example
Authorization: Bearer <redacted>
Content-Type: application/ld+json; profile="https://www.w3.org/ns/activitystreams"

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Note",
  "content": "Hello, Bob",
  "to": ["https://bob.example/users/bob"]
}
```

```http
HTTP/1.1 201 Created
Location: https://alice.example/activities/123
```

The server creates a `Create` activity and a Note with distinct IDs and copies the Note's addressing to the activity. `Location` identifies the activity; receiving `201` is not proof that remote delivery succeeded. `[spec]` §§6, 6.2.1, 7.1.

## Pitfalls

- **Assuming federation implies this API.** Client-to-server and server-to-server are independent profiles. Discover and test the actual server interface. `[spec]` §2.1.
- **Treating a client update as a federated patch.** A client update is partial, while a federated update is a full replacement; mixing them can erase or retain the wrong fields. `[spec]` §§6.3.1, 7.3.
- **Leaking blind recipients.** Resolve `bto` and `bcc` before removing them from delivered objects, and avoid showing them to other readers. `[spec]` §6, B.11.
- **Assuming a stable upload endpoint or universal OAuth flow.** The 2018 recommendation specifies neither; consult the server's own API. `[spec]` §§6.12, B.1.

## Sources

- [ActivityPub W3C Recommendation, 23 January 2018](https://www.w3.org/TR/2018/REC-activitypub-20180123/) — profiles, collections, client requests, side effects and security considerations; particularly §§2.1, 5–6 and B.
- [ActivityStreams 2.0 Core](https://www.w3.org/TR/activitystreams-core/) — object and collection data model.
