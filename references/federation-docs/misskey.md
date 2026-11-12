# Misskey federation behaviour (community-written)

> **Disclaimer.** This document was **not written by the Misskey maintainers**. It was written for this wiki from the project's source and may be incomplete or inaccurate. Do not cite it as a statement by the project. It follows the structure of [FEP-67ff](../feps/fep-67ff.md) but the project does not publish such a file, so it does not mean Misskey conforms to that FEP.

## Provenance

| Field | Value |
| ----- | ----- |
| Authorship | Written for this wiki, not by upstream |
| Project repository | [github.com/misskey-dev/misskey](https://github.com/misskey-dev/misskey) |
| Release basis | Development snapshot: 8 commits after tag `2026.11.0-beta.1`, a pre-release. |
| Commit | `5163caea120c901017eb52da17332939d527b8f2` (2026-11-11) |
| Other wiki revisions | The [Misskey case study](../../servers/case-studies/misskey.md) and [fact sheet](../software/misskey.md) pin release 2026.10.1 (`4840fa6`). Findings below are for a later snapshot; the `Update(Note)` limitation is also recorded for 2026.10.1 on the [post-edits record](../../federation/compatibility/post-edits.md). |
| Verification | Partial. `[source-verified]` items were read at this commit. |

Claim labels used below: `[source-verified]` read in the source at the commit named above; `[upstream-documented]` stated in the project's documentation and not checked in source; `[observed]` seen in a test or captured exchange; `[inferred]` concluded from source without a test; `[unverified]` carried over from an earlier draft and not checked.

## Document

### Protocols and standards

| Standard | Direction | Evidence |
| -------- | --------- | -------- |
| ActivityPub server-to-server | sends and receives; shared inbox `POST /inbox`, per-user `POST /users/:user/inbox` | `[source-verified]` [ActivityPubServerService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/server/ActivityPubServerService.ts) |
| WebFinger, NodeInfo 2.0 and 2.1 | serves | `[source-verified]` [WellKnownServerService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/server/WellKnownServerService.ts) |
| HTTP signatures (draft-cavage, `rsa-sha256`) | verifies and signs | `[upstream-documented]`; inbox parsing in the server service |
| `RsaSignature2017` Linked Data signatures | signs outgoing activities and verifies embedded signatures on relayed ones | `[source-verified]` [`attachLdSignature`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRendererService.ts), [JsonLdService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/JsonLdService.ts) |

### Supported FEPs

No FEP support was established. Misskey-specific terms (`_misskey_quote`, `_misskey_reaction`, `_misskey_votes`) predate or sit beside FEPs; see the extensions below. An earlier draft listed FEP-67ff as supported; that was wrong (see the disclaimer) and has been removed. FEP-044f is not read by Misskey's inbound quote code at this commit (see Quotes).

### Discovery

Actor and note URLs include `/users/{user}` and `/notes/{note}`; ActivityPub representations are chosen by content negotiation. Actors expose public keys and featured collections. `[source-verified]` [ActivityPubServerService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/server/ActivityPubServerService.ts)

### Authentication and limits

| Item | Behaviour | Evidence |
| ---- | --------- | -------- |
| Inbox body limit | 64 KiB (`bodyLimit: 1024 * 64`) on both inboxes; larger bodies are rejected | `[source-verified]` same file |
| Split of work | signature parsing, SHA-256 body digest and host checks at the HTTP endpoint; key resolution and cryptographic verification later in the queued inbox processor | `[source-verified]` [InboxProcessorService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/queue/processors/InboxProcessorService.ts) |
| Actor refresh | a remote actor not fetched in the last 24 hours is refreshed when it sends an activity | `[source-verified]` [ApInboxService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts) |

### Activity and object matrix

The inbox dispatcher recognises `Create`, `Delete`, `Update`, `Follow`, `Accept`, `Reject`, `Add`, `Remove`, `Announce`, `Like`, `Undo`, `Block`, `Flag`, `Move`; anything else returns "unrecognized activity type". `[source-verified]` [`performOneActivity`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts). An activity name alone is not support; the object type decides:

| Activity | Object | Accepts | Notes |
| -------- | ------ | ------- | ----- |
| `Update` | `Person` and other actors | **yes** | refreshes the actor; the activity actor must equal the stored actor URI |
| `Update` | `Question` | **yes** | updates the poll's vote totals |
| `Update` | **`Note`** and other post types | **no** | returns `skip: Unknown type`. A Mastodon-style post edit is not applied |
| `Create` | post types | yes | |
| `Delete` | notes, actors | yes | |
| `Like` | note | yes | becomes a reaction, see below |
| `Announce` | post | yes | becomes a renote; also from relays |
| `Undo` | `Follow`, `Block`, `Like`, `Announce`, `Accept` | yes | |
| `Move` | actor | yes | |
| `Flag` | | yes | report |

The `Update(Note)` row is the most important single fact in this table: a sender that edits a post will see the edit federate to Mastodon-family servers but not apply on Misskey 2026.11.0-beta.1 development builds like this one. `[source-verified]` [`update`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts); the same behaviour is recorded for the 2026.10.1 release on the [post-edits record](../../federation/compatibility/post-edits.md).

### Distinctive behaviour

| Topic | Outbound | Inbound | Evidence |
| ----- | -------- | ------- | -------- |
| Reactions | `Like` with `content` and `_misskey_reaction` both set to the reaction; custom emoji add an `Emoji` tag unless local-only | `Like` becomes a reaction using `_misskey_reaction`, else `content`, else `name`; "already reacted" is skipped. There is no `EmojiReact` branch | `[source-verified]` [`renderLike`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRendererService.ts), [`like`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts) |
| Quotes | `_misskey_quote` and `quoteUrl`, both the quoted URL | reads `_misskey_quote` or `quoteUrl` only; not `quoteUri`, not FEP-044f `quote`, in the code read | `[source-verified]` [ApNoteService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/models/ApNoteService.ts) |
| Renotes | `Announce` (public, home, followers visibility only; "cannot render non-public note" otherwise) | `Announce` of a post | `[source-verified]` |
| Polls | `Question` with `oneOf`/`anyOf` choices and `_misskey_votes` per choice | `Question` choices read from `oneOf` or `anyOf` by `name` | `[source-verified]` [`renderQuestion`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRendererService.ts), [ApQuestionService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/models/ApQuestionService.ts) |
| Poll vote | `Create` of a `Note` with `name` = the chosen option, `inReplyTo` = the poll note, addressed `to` the poll owner only; the id uses a `#votes/` fragment | not read | `[source-verified]` outbound, `[unverified]` inbound |
| Visibility mapping | public: `to` Public, `cc` followers. home: `to` followers, `cc` Public. followers: `to` followers. specified: explicit recipients. Inbound audience is parsed into a visibility and visible users; an empty "specified" audience is raised to public in one case | `[source-verified]` [ApRendererService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRendererService.ts), [ApNoteService](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/models/ApNoteService.ts) |

Consumers should treat the extension terms as optional; older releases and other software may omit them. `[upstream-documented]` [ActivityPub extensions](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/docs/contributing/activitypub.md)

### Operational behaviour

- Queue-based inbox processing; the HTTP endpoint accepts quickly and verification runs later. `[source-verified]`
- Object creation takes a per-object Redis lock keyed by the activity URI to avoid concurrent duplicate work. `[source-verified]` [`announceNote`](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts)

### Failure behaviour

| Condition | Behaviour | Evidence |
| --------- | --------- | -------- |
| Suspended remote actor | activity ignored | `[source-verified]` |
| `Update` actor differs from stored actor | `skip: invalid actor` | `[source-verified]` |
| `Update` of an unsupported object type | `skip: Unknown type` | `[source-verified]` |
| `Like` target note not found | `skip: target note not found` | `[source-verified]` |
| Announce target unresolved or federation-blocked URI | skipped | `[source-verified]` |
| Body over 64 KiB | rejected | `[source-verified]` |
| Quote target unfetchable | permanent versus temporary error is distinguished | `[source-verified]` |
| Retry behaviour of failed inbox jobs | not read | `[unverified]` |

### Examples

A `Like` carrying a reaction, constructed from `renderLike` and not captured from a server:

```json
{
  "type": "Like",
  "id": "https://misskey.example/likes/abc123",
  "actor": "https://misskey.example/users/u1",
  "object": "https://remote.example/notes/n1",
  "content": ":blobcat:",
  "_misskey_reaction": ":blobcat:",
  "tag": [{ "type": "Emoji", "name": ":blobcat:" }]
}
```

## Sources

- [Misskey repository](https://github.com/misskey-dev/misskey) — source read at commit `5163caea120c901017eb52da17332939d527b8f2`
- [ApInboxService.ts](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApInboxService.ts) — dispatcher and handlers
- [ApRendererService.ts](https://github.com/misskey-dev/misskey/blob/5163caea120c901017eb52da17332939d527b8f2/packages/backend/src/core/activitypub/ApRendererService.ts) — outgoing representations
