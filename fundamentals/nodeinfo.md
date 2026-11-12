# NodeInfo

[NodeInfo](../glossary.md#nodeinfo) is a small JSON document a server publishes to say what software and version it runs and which protocols it speaks. It is how clients and other servers guess capabilities, and it is only a hint: servers can report anything.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

A discovery document at `/.well-known/nodeinfo` links to a versioned schema document (2.0, 2.1 and later). `[documented]` NodeInfo project.

## What implementations do

Capability detection by software name and version is common but fragile; forks and renamed builds report their own names. See [client architecture](../clients/index.md).

## Technical details

> Unknown: fields each studied implementation reports, and which expose `metadata` extensions.

## Open questions

- Which software lets administrators change the reported software name?

## Sources

- [NodeInfo](https://nodeinfo.diaspora.software/) — schema and discovery
