# Mobilizon federation behaviour (community-written)

> **Not by the Mobilizon maintainers.** Written for this wiki from the project's source; it may be incomplete or inaccurate and must not be cited as the project's own statement. It follows the structure of [FEP-67ff](../feps/fep-67ff.md); the project publishes no such file.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [framagit.org/kaihuri/mobilizon](https://framagit.org/kaihuri/mobilizon) |
| Release basis | Release candidate: tag `5.2.5-RC.1` (the commit is that tag). |
| Commit | `f2590486f6ee056f01fa05412a16f9a08c65357e` (2026-09-30) |
| Other wiki revisions | No Mobilizon case study or fact sheet exists, so there is no other pinned revision. |
| Verification | Partial. `[source-verified]` items were read in the local checkout of this commit. The hosting site (Framagit) could not be retrieved independently, so the links point at it but were not re-fetched. |

Claim labels (`[source-verified]`, `[upstream-documented]`, `[observed]`, `[inferred]`, `[unverified]`) are defined in [AGENTS.md](../../AGENTS.md#community-written-federation-documents).

## Document

Mobilizon federates events, people, groups, comments, posts and group membership. The page records exact contracts for the parts that differ from ordinary microblogging: event attendance, group membership and invitations.

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; actor inbox `POST /@{name}/inbox`, shared inbox `POST /inbox`, relay actor `/relay` and `/relay/inbox` | `[source-verified]` [router.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/router.ex), [activity_pub_controller.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/controllers/activity_pub_controller.ex) |
| WebFinger and host-meta | serves both; remote lookup tries host-meta first, then falls back to the well-known WebFinger path | `[unverified]` |
| NodeInfo | `/.well-known/nodeinfo` and `/.well-known/nodeinfo/:version` | `[unverified]` |
| HTTP signatures (draft) | signs outgoing POSTs over `(request-target)`, `host`, `content-length`, `digest`, `date`; verifies incoming (see below) | `[unverified]` header list; behaviour of the inbox is source-verified |

### Supported FEPs

None found. No FEP is identified as implemented in this checkout; similar vocabulary is not evidence of conformance.  `[unverified]` negative: a search for FEP numbers was not exhaustive.

### Discovery

`/@{name}` serves actors via content negotiation; collections under `/@{name}/outbox`, `/following`, `/followers`, `/members`; event and comment URLs can be requested as ActivityPub objects. `[source-verified]` [router.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/router.ex)

### Authentication and the unsigned-`Create` path

The inbox controller has four clauses, in this order. `[source-verified]` [activity_pub_controller.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/controllers/activity_pub_controller.ex)

| Case | Behaviour |
| ---- | --------- |
| Valid signature, **actor inbox** | the recipient actor must be local; the sending actor is fetched; the recipient must be addressed in the message (`recipient_in_message`); the document is queued as `:incoming_ap_doc`; the response is `"ok"` |
| Valid signature, **shared inbox** | queued without a recipient check; response `"ok"` |
| **No valid signature, type `Create`** | the controller does **not** trust the submitted object. It calls `fetch_object_from_url` on `object.id` and responds `"ok"` regardless of the result |
| No valid signature, anything else | not queued; response `"error"` (a debug log hints that the reverse proxy must forward the `Host` header) |

The third row is the security-relevant one. It is a relayed-`Create` accommodation: the object is refetched from the URL named in the submission, never taken from the submitted body. This wiki did not read the fetch function or test it, so the following are open: whether the fetched URL is constrained to the sender's origin, whether the fetched object's author is checked against the claimed actor, and whether the fetch passes an SSRF filter. `> Unknown:` until verified. A success response ("ok") does not mean anything was applied.

### Activity and object matrix

Incoming activities are normalised by `handle_incoming` clauses in [transmogrifier.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/transmogrifier.ex). `[source-verified]` clause heads:

| Activity | Object | Accepts | Meaning and conditions |
| -------- | ------ | ------- | ---------------------- |
| `Create` | `Note` | yes | comment |
| `Create` | `Event` | yes | event |
| `Create` | `Member` | yes | a membership record: `role` and the group as `object` |
| `Create` | `Article` | yes | group post; needs `actor` and `attributedTo` |
| `Create` | `Tombstone` | yes | a deleted object arriving as a create |
| `Create` | other with an `id` | yes | actor-type creates (`type` is bound from the object) |
| `Update` | actor types (`Person`, `Group`, `Application`, `Service`, `Organization`) | yes, only remote actors and groups | an update of a **local** actor is refused |
| `Update` | `Event`, `Note`, `Article`, `Member`, `Tombstone` | yes | each has its own clause |
| `Follow`, `Accept`, `Reject` | actor | yes | follow flow; whether `Accept`/`Reject` also settle invitations and participation is `[inferred]` and not read |
| `Announce`, `Undo(Announce)` | object | yes | shares, including announced `Delete` |
| `Undo` | `Follow` | yes | the only other `Undo` form; not a general undo |
| `Delete` | object | yes | |
| `Join` | event | yes | **attendance request**: creates a participation for the actor (`metadata.message` from `participationMessage`); whether it stays pending until an organiser accepts was not read |
| `Join` | group | yes | **group membership request** `[inferred]`: the same clause calls `Join.join` with whatever object was fetched, so the object's type is expected to decide |
| `Leave` | event or group | yes | ends attendance or membership; refused with `:only_organizer` when the actor is an event's only organiser |
| `Invite` | `object` = group, `target` = invited actor | yes | creates a pending **invited** member; the invitee then answers with `Accept` or `Reject` |
| `Remove` | `object` = member, `origin` = group | yes | a moderator or admin removes a member; the group must be a `Group`, the actor must be allowed to remove, and the person must be a non-rejected member |
| `Flag` | | yes | report |

How this differs from a follow: `Follow` subscribes to an actor's posts. `Join` on an event is a request to attend and carries an optional message; `Join` on a group is a request for membership with a role. `Invite` is an offer from a group moderator to a person and changes nothing until the person accepts. Which fields of an event propagate on `Update(Event)` was not read. `> Unknown:`

### Distinctive behaviour

- Event attendance, group membership and invitations are first-class activities rather than extensions on `Follow`. `[source-verified]` above.
- `Member` objects carry a `role` (a string of the role). `[source-verified]` [member converter](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_stream/converter/member.ex)

Constructed examples (field names from the converters; not captured):

```json
{
  "type": "Join",
  "id": "https://mobilizon.example/join/1",
  "actor": "https://other.example/users/alice",
  "object": "https://mobilizon.example/events/ev1",
  "participationMessage": "Can I bring a friend?"
}
```

```json
{
  "type": "Invite",
  "id": "https://mobilizon.example/invite/7",
  "actor": "https://mobilizon.example/@moderator",
  "object": "https://mobilizon.example/@group",
  "target": "https://other.example/users/bob"
}
```

### Operational behaviour

- Inbound signed documents are queued and applied later, so a `200 "ok"` is not proof of application. `[source-verified]`
- Outgoing delivery expands follower and member collections, prefers shared inboxes, deduplicates inbox URLs and queues one delivery per inbox; with relay support on, public activities are addressed to relay followers and public `Create` is also published through the relay. `[unverified]` publisher not re-read.

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| Bad signature, non-`Create` | `"error"`, not queued | `[source-verified]` |
| Unsigned `Create` | object refetched; always `"ok"` | `[source-verified]` |
| Activity without an `id` | `:error` | `[source-verified]` |
| `Leave` by an event's only organiser | refused | `[source-verified]` |
| `Update` of a local actor | refused with `update_not_allowed` | `[source-verified]` |
| Unmatched activity type | `handle_incoming` falls through to a generic clause | `[source-verified]` (last clause) |
| Proxy not forwarding `Host` | signature validation fails; debug hint logged | `[source-verified]` |

## Sources

- [Mobilizon repository](https://framagit.org/kaihuri/mobilizon) — source read at commit `f2590486f6ee056f01fa05412a16f9a08c65357e`
- [transmogrifier.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/federation/activity_pub/transmogrifier.ex) — incoming activity handlers
- [activity_pub_controller.ex](https://framagit.org/kaihuri/mobilizon/-/blob/f2590486f6ee056f01fa05412a16f9a08c65357e/lib/web/controllers/activity_pub_controller.ex) — inbox clauses
