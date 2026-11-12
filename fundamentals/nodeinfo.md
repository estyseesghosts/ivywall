# NodeInfo

[NodeInfo](../glossary.md#nodeinfo) is a small JSON document a server publishes to say what software and version it runs and which protocols it speaks. It is how clients and other servers guess capabilities, and it is only a hint: servers can report anything.

> **Coverage incomplete.** The discovery document and schema are described from the NodeInfo project. Not yet covered: the fields each studied server reports, which expose `metadata` extensions, and whether administrators can change the reported software name.

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
