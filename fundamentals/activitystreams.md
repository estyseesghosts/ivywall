# ActivityStreams 2.0

ActivityStreams is the JSON vocabulary that describes who did what to what: an **[actor](../glossary.md#actor)** performs an activity such as `Create` or `Follow` on an object such as a `Note`. [ActivityPub](../glossary.md#activitypub) carries these documents between servers, so every other page in this wiki depends on this one.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

ActivityStreams JSON documents SHOULD include the normative `@context`; for `application/activity+json`, a consumer MUST assume it when absent. Objects use `type` and may have an `id`; not every ActivityStreams object must have a dereferenceable URL. ActivityPub adds identifier requirements, including an explicit anonymous-object exception. Collections (`Collection`, `OrderedCollection` and their pages) group items. `[spec]` [ActivityStreams Core §§2.1, 3.1](https://www.w3.org/TR/activitystreams-core/) and [ActivityPub §3.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/#obj-id).

## What implementations do

A server that processes JSON without full [JSON-LD](../glossary.md#json-ld) expansion must account for alternative valid forms; ActivityPub explicitly notes compact representations of the Public audience. Whether a particular server accepts each form must be checked against its version. `[spec]` [ActivityPub §5.6](https://www.w3.org/TR/2018/REC-activitypub-20180123/#public-addressing).

## Technical details

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Create",
  "actor": "https://example.com/users/alice",
  "object": { "type": "Note", "content": "Hello" }
}
```

Hand-written example, not captured from a server.

## Open questions

- Which implementations run a real JSON-LD processor and which pattern-match on fixed shapes?
- How are `@context` extensions handled when unknown?

## Sources

- [ActivityStreams 2.0 Core](https://www.w3.org/TR/activitystreams-core/) — data model
- [ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/) — activity and object types
