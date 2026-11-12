# ActivityStreams 2.0

ActivityStreams is the JSON vocabulary that describes who did what to what: an **[actor](../glossary.md#actor)** performs an activity such as `Create` or `Follow` on an object such as a `Note`. [ActivityPub](../glossary.md#activitypub) carries these documents between servers, so every other page in this wiki depends on this one.

> **Coverage incomplete.** The data model and example follow the specification. Not yet covered: which studied servers run a JSON-LD processor, and how unknown `@context` extensions are handled. Statements without an evidence label are general background, not verified findings.

## What the specification requires

ActivityStreams JSON documents SHOULD include the normative `@context`; for `application/activity+json`, a consumer MUST assume it when absent. Objects use `type` and may have an `id`; not every ActivityStreams object must have a dereferenceable URL. ActivityPub adds identifier requirements, including an explicit anonymous-object exception. Collections (`Collection`, `OrderedCollection` and their pages) group items. `[spec]` [ActivityStreams Core §§2.1, 3.1](https://www.w3.org/TR/activitystreams-core/) and [ActivityPub §3.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/#obj-id).

## What implementations do

Many servers read these documents as plain JSON in the common Mastodon shape, not by full [JSON-LD](../glossary.md#json-ld) expansion. Akkoma says so outright: it does not perform JSON-LD processing. `[documented]` [Akkoma federation document](../references/federation-docs/akkoma.md). Other studied servers are `> Unknown:`; the cited documents do not say. The consequence is that a valid alternative serialisation can fail where the common one works, and an unknown extension term is dropped or misread. ActivityPub itself notes compact forms of the Public audience. `[spec]` [ActivityPub §5.6](https://www.w3.org/TR/2018/REC-activitypub-20180123/#public-addressing).

### What JSON-LD 1.1 adds

`@context` maps short terms to full IRIs, so different JSON can mean the same data: a term can be an alias (`"Note"` for an IRI), a compact IRI (`"as:Note"`), or defined in a nested context; contexts can be remote URLs the processor must fetch, and *protected* terms cannot be redefined by a later context. After expansion two differently written documents compare equal. `[spec]` [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/). Fetching a remote context is a network request chosen by the sender, so it needs the same limits as any [remote fetch](../security/ssrf.md); a server that does no expansion avoids that risk and the compatibility benefit together.

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

## Sources

- [ActivityStreams 2.0 Core](https://www.w3.org/TR/activitystreams-core/) — data model
- [ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/) — activity and object types
- [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/) — contexts, expansion, protected terms, remote contexts
