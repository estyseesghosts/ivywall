# Mbin federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the Mbin maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean Mbin conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [github.com/MbinOrg/mbin](https://github.com/MbinOrg/mbin) |
| Release basis | Release `v1.11.1` (the commit is that tag). |
| Commit | `6d04519c09ce4b42acf791359e770c7fff5d4840` (2026-11-10) |
| Other wiki revisions | No Mbin case study or fact sheet exists yet, so there is no other pinned revision. |
| Verification | Partial. `[source-verified]` items were read at this commit; collection and activity shapes come from the project's own developer documentation. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; user and magazine inboxes plus a shared inbox | `[upstream-documented]` [developer docs](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/05-fediverse_developers/README.md) |
| WebFinger | resolves user and magazine actors | `[source-verified]` [user](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/EventSubscriber/ActivityPub/UserWebFingerSubscriber.php) and [group](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/EventSubscriber/ActivityPub/GroupWebFingerSubscriber.php) subscribers |
| HTTP signatures (draft-cavage, RSA-SHA256) | signs outgoing; verifies incoming. Only the draft `Signature` header is handled; no RFC 9421 code was found in the validator | `[source-verified]` [SignatureValidator](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/SignatureValidator.php) |
| NodeInfo 2.0 and 2.1 | served | `[unverified]` |

### Supported FEPs

| FEP | Support | Evidence |
| --- | ------- | -------- |
| FEP-1b12 (group federation) | magazines are `Group` actors and announce members' activities to their audience | `[upstream-documented]` developer docs; the developer docs link a path that does not match the FEP repository's current layout |

An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer) and has been removed. No other FEP support was established.

### Discovery

- Instance actor `/i/actor` (`Application`); users `/u/{username}` (`Person`); magazines `/m/{name}` (`Group`). `[upstream-documented]` developer docs.
- User outbox, followers and following are described with payloads in the docs. The magazine outbox returns an empty object, magazine followers expose a count and no items, and the moderators and featured collections are not paginated. `[upstream-documented]` same docs; which collections can be enumerated is therefore: user outbox, followers and following (paged), moderators and featured (complete, unpaged); the magazine outbox and magazine followers cannot.

### Authentication: what the signature validator accepts

All of the following is `[source-verified]` in [SignatureValidator.php](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/SignatureValidator.php) at this commit.

| Check | Behaviour |
| ----- | --------- |
| Required headers | `Signature` and `Date` must be present, otherwise the request is rejected |
| Date freshness | **not checked**: the code carries `// @todo verify headers date`. A signed request can be replayed any time later, as long as the signed headers do not make the signature depend on something else |
| `keyId` and activity `id` | both must be valid HTTPS URLs; `id` is required |
| Key host versus activity | the host of `keyId` must equal the host of the activity `id`, and every `actor` must be on the key's host; a mismatch rejects the request |
| Digest | the `Digest` header is compared with the digest computed from the body, but a **mismatch is only logged as a warning, not an error**. When `digest` is among the signed headers, the signing string uses the computed digest, so a tampered body makes the signature fail. If `digest` is not signed, the body is not covered by the signature `[inferred]` |
| Key source | the actor's stored key, else the actor document's `publicKey.publicKeyPem`; no key means rejection |
| Algorithm | RSA with SHA-256 only; an `openssl_verify` result of anything other than 1 is a failure |

**Forwarded activities.** If the key host and the activity host differ, or the actor host differs from the key host while equalling the activity host, and one of the activity's receivers is an inbox on the key's host, Mbin concludes the activity was forwarded. It does not trust the forwarder's copy: it dispatches a new message after fetching the activity from the activity id's own host with a signed GET, and skips this if the origin instance is banned. `[source-verified]` same file and [ActivityHandler](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/MessageHandler/ActivityPub/Inbox/ActivityHandler.php). Validation happens in the queued handler, not in the HTTP request, so a rejected signature is not visible to the sender as an HTTP error `[inferred]`.

### Activity and object matrix

Inbound activity messages exist for `Create`, `Update`, `Delete`, `Add`, `Remove`, `Like`, `Dislike`, `Announce`, `Follow`, `Block`, `Flag` and `Lock`, plus undo and accept/reject handling. `[source-verified]` message classes and [ActivityHandler](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/MessageHandler/ActivityPub/Inbox/ActivityHandler.php). The developer documentation describes what Mbin sends:

| Activity | Object / target | Meaning | Federated | Evidence |
| -------- | --------------- | ------- | --------- | -------- |
| `Follow` / `Undo`, `Accept` / `Reject` | user or magazine | follow; local users auto-accept | yes | `[upstream-documented]` |
| `Create`, `Update`, `Delete` | thread (`Page`), microblog and comments (`Note`), private message | content | yes | `[upstream-documented]` |
| `Like` / `Undo(Like)` | post or comment | up-vote | yes | `[upstream-documented]` |
| `Dislike` | post or comment | down-vote | **not federated outbound**; inbound `Dislike` has a handler | `[upstream-documented]` and `[source-verified]` (message class) |
| `Announce` | content id | boost by a user; magazine redistribution of `Create`, `Update`, `Add`, `Remove`, `Announce`, `Delete`, `Like`, `Dislike`, `Flag` and `Lock` | yes | `[upstream-documented]` |
| `Flag` | content | report; `Announce(Flag)` goes only to instances that have moderators of that magazine | yes | `[upstream-documented]` |
| `Add` / `Remove` | moderators collection, featured collection | add or remove a moderator, pin or unpin a thread | yes | `[upstream-documented]` |
| `Block` | user, `audience` = magazine | ban from a magazine; the instance-level ban has no `audience` | yes | `[source-verified]` [BlockFactory](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Factory/ActivityPub/BlockFactory.php) |
| `Lock` | content | no new comments | yes | `[upstream-documented]` |
| `Delete` (admin account deletion) | user | looks identical to the user deleting their own account | yes | `[upstream-documented]` |

### Distinctive behaviour

- A magazine announces the activities its members do with it as the audience; Announce can carry an inner activity object, or just a URL for the receiver to fetch. `[source-verified]` [AnnounceWrapper](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/src/Service/ActivityPub/Wrapper/AnnounceWrapper.php)
- Down-votes are not federated. `[upstream-documented]`

### Operational behaviour

> Unknown: retry schedules and queue configuration for delivery were not read.

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| Missing `Signature` or `Date` | rejected as an invalid signature | `[source-verified]` |
| `keyId` or `id` not HTTPS | rejected | `[source-verified]` |
| Key host differs from activity or actor host and no forwarding match | rejected | `[source-verified]` |
| Forwarded activity | refetched from the origin; skipped if that instance is banned | `[source-verified]` |
| Actor has no usable public key | logged as a warning and the message dropped | `[source-verified]` |
| Digest mismatch | warning only | `[source-verified]` |
| Stale `Date` | accepted | `[source-verified]` (the check is a TODO) |

### Examples

Both examples are **constructed** from the field lists in the factories and developer docs and have not been run or captured. The upstream docs generate their own examples with `DocumentationGenerateFederationCommand`, which this wiki did not execute.

A user's `Create` announced by a magazine (shape per AnnounceWrapper and the docs):

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://mbin.example/m/news/announce/1",
  "type": "Announce",
  "actor": "https://mbin.example/m/news",
  "object": {
    "id": "https://other.example/activities/create/9",
    "type": "Create",
    "actor": "https://other.example/u/alice",
    "object": { "type": "Page", "id": "https://other.example/post/42" }
  }
}
```

A moderator banning a user from a magazine (`BlockFactory`: type `Block`, `audience` = the magazine, actor = the moderator):

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://mbin.example/activities/block/3",
  "type": "Block",
  "actor": "https://mbin.example/u/moderator",
  "audience": "https://mbin.example/m/news",
  "object": "https://other.example/u/spammer"
}
```

## Sources

- [Mbin repository](https://github.com/MbinOrg/mbin) — source read at commit `6d04519c09ce4b42acf791359e770c7fff5d4840`
- [Mbin federation developer documentation](https://github.com/MbinOrg/mbin/blob/6d04519c09ce4b42acf791359e770c7fff5d4840/docs/05-fediverse_developers/README.md) — activity, object and collection descriptions (`[upstream-documented]`)
