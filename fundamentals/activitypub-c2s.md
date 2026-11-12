# ActivityPub client-to-server

The client-to-server part of ActivityPub defines how an app posts to a user's **outbox** and reads their inbox. In practice almost no large server implements it; clients use each server family's own API instead. This page records why, and what that means for client authors.

> **Stub.** Scaffolding only. Nothing on this page has been checked against pinned source yet; treat every statement as `[hypothesis]` unless it carries another label.

## What the specification requires

Clients authenticate (method unspecified), POST activities to the actor's outbox, and the server assigns ids and performs side effects. `[spec]` ActivityPub, section 6.

## What implementations do

Real clients use the Mastodon REST API or Misskey's API. See [Clients](../clients/index.md) and [the Mastodon REST API](../clients/apis/mastodon-rest.md).

## Technical details

> Unknown: which servers expose a working outbox POST, and with what authentication.

## Open questions

- Does any maintained server accept client-to-server posts in production?

## Sources

- [ActivityPub (W3C Recommendation)](https://www.w3.org/TR/activitypub/) — base protocol
