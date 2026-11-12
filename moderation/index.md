# Moderation

Moderation on the Fediverse is done per server, with tools that differ a great deal: account and domain blocks, outright federation rejection, report forwarding, spam handling, remote media filtering, message rewriting and administrator audit trails. This section compares how implementations do it and what each approach costs.

## Pages

No topic pages yet. Planned:

- Blocking and federation controls — account and domain blocks, rejection, limiting.
- Message rewriting — Akkoma's [Message Rewrite Facility](../glossary.md#mrf) compared with Mastodon's moderation tooling and GoToSocial's federation controls.
- Reports, spam, remote media and audit trails.

## Notes and open questions

> Unknown: what happens to already-stored remote content when a domain is blocked, per implementation.

## Sources

- [Mastodon moderation documentation](https://docs.joinmastodon.org/admin/moderation/) — baseline moderation features
- [Akkoma documentation](https://docs.akkoma.dev/) — MRF policies
