# ActivityStreams 2.0

ActivityStreams is the JSON vocabulary that describes who did what to what: an **[actor](../glossary.md#actor)** performs an activity such as `Create` or `Follow` on an object such as a `Note`. [ActivityPub](../glossary.md#activitypub) carries these documents between servers, so every other page in this wiki depends on this one.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

Documents are JSON with a `@context`; objects have a `type` and usually an `id` that is a dereferenceable URL. Collections (`Collection`, `OrderedCollection` and their pages) group items. `[spec]` ActivityStreams 2.0 Core.

## What implementations do

Many servers treat documents as plain JSON and ignore [JSON-LD](../glossary.md#json-ld) processing, which makes extension terms and compaction a source of interoperability bugs. To be verified per implementation.

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
