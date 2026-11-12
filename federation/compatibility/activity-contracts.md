# Compatibility: what each server does with an incoming activity

"Supports `Update`" hides the differences that break interoperability: a server can apply a profile update, skip a post edit and refresh a poll. This table separates the object that is updated or undone, for the snapshots studied in the community-written [federation documents](../../references/federation-docs/index.md). It records the **receiving handler**: whether the activity is accepted and applied at storage. Whether the result then reaches that server's client API, timelines or search is a separate stage.

## Summary

| Software (snapshot) | `Update` of a profile | `Update` of a post (`Note`, `Page`, `Article`) | `Update` of a poll (`Question`) | `Undo(Announce)` | `Announce` of a post |
| ------------------- | --------------------- | ----------------------------------------------- | ------------------------------- | ---------------- | -------------------- |
| Mastodon 4.7.3 | yes | yes: edits, with ownership and age checks | yes: vote counts | yes | yes: becomes a boost |
| Misskey 2026.11.0-beta.1 | yes | **no**: skipped (`skip: Unknown type`) | yes | yes | yes: becomes a renote |
| Catodon 26.11.0-rc.1+38 | yes | yes | yes: also applies an edit when a later edit date is stated | yes | yes |
| Pixelfed 0.15.2+230 | yes | yes, only if the sender owns the stored status | **no branch found** | yes | yes |
| NodeBB 4.16.7+19 | yes | yes | yes (`Question` is an accepted post type) | yes | yes, if a local follower follows the announcer |
| Lemmy 1.0.0-beta.3+11 | no handler found | yes, inside a community `Announce` | not applicable | no handler found | yes: the community redistribution form |
| Wafrn 2026.11.01 | yes | yes, after a fixed 5-second wait | yes | yes | yes |
| Mbin v1.11.1 | not read | not read (`UpdateMessage` exists) | not read | not read | yes (`AnnounceMessage`) |
| Mobilizon 5.2.5-RC.1 | yes | yes: `Event`, `Note`, `Article`, `Member` | no clause found | yes | yes |
| WriteFreely 0.17.3+12 | no handler | no handler | no handler | no handler (`Undo` of `Like` and `Follow` only) | no handler |

`+N` means N commits after the named tag; those are development snapshots, not releases. "No handler found" means the read found none, not that the software cannot be made to do it. Rows are `[source-verified]` in each project's federation document, except Mastodon, whose cells are `[documented]` in [its ActivityPub documentation](https://docs.joinmastodon.org/spec/activitypub/) and, for post edits, `[source]` on the [post-edits record](post-edits.md). Misskey's `Update(Note)` result is also recorded there for 2026.10.1. Values for emit, translate and lose are in the [glossary](../../glossary.md#compatibility-values).

## Why the columns matter

- A sender that edits a post sees the edit federate to Mastodon, Catodon, NodeBB, Wafrn and Mobilizon, and not apply on Misskey or WriteFreely. Do not assume an edit has propagated; see [post edits](post-edits.md).
- A poll's `Update(Question)` carries vote counts, not an edit; Pixelfed has no branch, so its copy of a remote poll would not refresh `[inferred]`.
- `Undo(Announce)` being handled does not mean it takes effect: in the laboratory some origins kept the boost; see [Undo, boosts and unboosts](undo-and-reposts.md).
- Lemmy treats `Announce` as the way a community redistributes members' activities, not a boost; see its [federation document](../../references/federation-docs/lemmy.md).

## Extending the table

Add a column or row only with a pinned commit and a label from [AGENTS.md](../../AGENTS.md#evidence-labels). Use `yes`, `no`, `not read` or a short condition; never infer a cell from a handler's existence for another object type. Back each cell with a test when the [lab](../../testing/harness/local-lab.md) can run one.

## Sources

- [Mastodon ActivityPub documentation](https://docs.joinmastodon.org/spec/activitypub/) — supported activities for statuses and profiles
- [Community-written federation documents](../../references/federation-docs/index.md) — one per studied project, each with its pinned commit and evidence labels
