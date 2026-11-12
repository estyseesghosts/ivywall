# NodeInfo

[NodeInfo](../glossary.md#nodeinfo) is a small JSON document a server publishes to say what software and version it runs and which protocols it speaks. It is how clients and other servers guess capabilities, and it is only a hint: servers can report anything.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

The discovery document at `/.well-known/nodeinfo` supplies links with versioned relation types to the server’s NodeInfo documents. A client chooses a schema it understands; the project documents schemas 1.0, 1.1, 2.0 and 2.1. `[documented]` [NodeInfo protocol](https://nodeinfo.diaspora.software/protocol.html) and [schemas](https://nodeinfo.diaspora.software/schema.html).

## What implementations do

Software name and version are metadata, not proof that a particular endpoint or feature is enabled. Check the actual server and handle missing or disabled features. See [client architecture](../clients/index.md).

## Technical details

> Unknown: fields each studied implementation reports, and which expose `metadata` extensions.

## Open questions

- Which software lets administrators change the reported software name?

## Sources

- [NodeInfo](https://nodeinfo.diaspora.software/) — schema and discovery
