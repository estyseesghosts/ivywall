# Project federation documents

Several Fediverse projects publish a `FEDERATION.md` that states what their software supports. This section keeps one page per studied project. Where upstream publishes one, the page is a verbatim mirror. Some pages contain a document written for this wiki (marked **community-written**, with a disclaimer that the maintainers did not write it and it may be inaccurate); others explain the relevant upstream documentation or client role.

## Upstream documents, mirrored verbatim

These are the projects' own statements, copied unedited. Each page records the upstream file, commit and licence.

| Project | Mirror | Commit | Licence |
| ------- | ------ | ------ | ------- |
| Mastodon | [Mastodon](mastodon.md) | `b31c484d97` | AGPL-3.0 |
| Akkoma | [Akkoma](akkoma.md) | `3e9ad30e1e` | AGPL-3.0 |
| Iceshrimp.NET | [Iceshrimp.NET](iceshrimp-net.md) | `52ef47bd05` | EUPL-1.2 |
| Loops | [Loops](loops-server.md) | `d942be8e8c` | AGPL-3.0 |
| snac | [snac](snac2.md) | `846137df09` | MIT |

## Upstream pointers

Upstream has a `FEDERATION.md` that points elsewhere, or a related document, and the page explains it. These are not the projects' complete federation statements.

- [GoToSocial](gotosocial.md) — upstream file links to the online federation documentation.
- [Mastodon for Android](mastodon-android.md) — client and server responsibilities.

## Community-written, not by the maintainers

> **These are not official project documents.** They were written for this wiki from the projects' source, may be incomplete or inaccurate, and must not be cited as statements by the maintainers. They follow the structure of [FEP-67ff](../feps/fep-67ff.md) but do not mean the projects publish such a file. Each page has its own provenance block and claim-level labels.

- [Catodon](catodon.md)
- [Lemmy](lemmy.md)
- [Mbin](mbin.md)
- [Misskey](misskey.md)
- [Mobilizon](mobilizon.md)
- [NodeBB](nodebb.md)
- [Pixelfed](pixelfed.md)
- [Wafrn](wafrn.md)
- [WriteFreely](writefreely.md)

## Notes and open questions

Mirrored documents are the projects' own claims. Compare them against source before using them in a [compatibility record](../../federation/index.md); until then they are `[documented]` at best.

Community-written descriptions are not upstream claims and need source verification for the exact revision; a snapshot does not establish support in other releases.

## Sources

- [FEP-67ff: FEDERATION.md](https://fediverse.codeberg.page/fep/fep/67ff/) — the proposal that standardises this file
